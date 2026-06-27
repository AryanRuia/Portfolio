import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle
import numpy as np
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
from datetime import datetime

# CONFIGURATION & HARDWARE PROFILES

# Hardware Profiles based on your prototype
HARDWARE_SPECS = {
    "XBee_900HP": {
        "name": "LumaNet (900 MHz Long Range)",
        "range_km": 8.0,          # Conservative rural range
        "speed_kbps": 200,        # Max throughput
        "cost_per_module": 75.00,
        "base_node_cost": 100.00,  # Pi 5 + Case + SD + Battery bank
        "power_tx_mw": 950,        # Transmission power in mW
        "power_rx_mw": 55,         # Receiving power in mW
        "power_idle_mw": 15,       # Idle power in mW
        "battery_capacity_mah": 10000  # mAh
    },
    "XBee_3_Pro": {
        "name": "LumaNet (2.4 GHz High Speed)",
        "range_km": 1.5,
        "speed_kbps": 250,
        "cost_per_module": 22.00,
        "base_node_cost": 100.00,
        "power_tx_mw": 500,
        "power_rx_mw": 85,
        "power_idle_mw": 35,
        "battery_capacity_mah": 10000
    }
}

# Fiber Optic Comparison Benchmark
FIBER_SPECS = {
    "cost_per_km": 25000,  # ~$40k/mile (aerial/rural average)
    "speed_mbps": 1000,    # Gigabit
    "maintenance_annual": 5000  # Annual maintenance per km
}

# Simulation Parameters
NUM_NODES = 50             # Scalable: Change to 75, 100, etc.
AREA_SIZE_KM = 10          # 10x10 km village/region
FILE_SIZE_MB = 5           # Size of "Educational Packet" to sync (5MB = 2 minutes at 200kbps)
SIMULATION_TYPE = "XBee_900HP" # Options: "XBee_900HP" or "XBee_3_Pro"
SIMULATION_TIME_STEPS = 500  # Max time steps to simulate (seconds)
COLLISION_PROBABILITY = 0.02  # 2% collision chance when multiple nodes transmit simultaneously
RETRANSMISSION_DELAY = 3     # Steps before retrying failed transmission
MAX_HOPS = 3               # Maximum hops to prevent excessive retransmissions

# DATA STRUCTURES

@dataclass
class Packet:
    """Represents a data packet in transmission"""
    node_id: int
    destination_id: int
    size_kb: float
    data_transferred_kb: float = 0.0
    creation_time: int = 0
    failed_attempts: int = 0
    
    @property
    def is_complete(self) -> bool:
        return self.data_transferred_kb >= self.size_kb

@dataclass
class NetworkMetrics:
    """Stores simulation statistics"""
    total_time_steps: int = 0
    time_to_full_sync: int = -1
    synced_nodes_history: List[int] = None
    sync_percentage_history: List[float] = None
    energy_consumed_kwh: float = 0.0
    energy_consumed_per_node_wh: float = 0.0
    packets_transmitted: int = 0
    packets_lost: int = 0
    packets_retransmitted: int = 0
    average_latency_ms: float = 0.0
    network_efficiency_percent: float = 0.0
    average_throughput_kbps: float = 0.0
    network_reliability_percent: float = 0.0
    
    def __post_init__(self):
        if self.synced_nodes_history is None:
            self.synced_nodes_history = []
        if self.sync_percentage_history is None:
            self.sync_percentage_history = []

# SIMULATION CLASS

class LumaNetSimulation:
    def __init__(self, num_nodes, area_size, hardware_key):
        self.num_nodes = num_nodes
        self.area_size = area_size
        self.specs = HARDWARE_SPECS[hardware_key]
        self.nodes = []
        self.graph = nx.Graph()
        self.total_cost = 0
        self.metrics = NetworkMetrics()
        self.in_flight_packets = defaultdict(deque)  # Queue of packets per edge
        self.transmission_queue = defaultdict(deque)  # Queue of packets waiting to send
        self.node_battery_status = {}  # Track battery level per node
        self.node_sync_time = {}  # Track when each node was synced
        
        # Initialize Nodes with random positions
        for i in range(num_nodes):
            self.nodes.append({
                "id": i,
                "x": random.uniform(0, area_size),
                "y": random.uniform(0, area_size),
                "has_file": False,  # Sync status
                "percent_received": 0.0,
                "data_received_kb": 0.0,
                "last_synced_step": -1,
                "energy_used_mah": 0.0
            })
            self.node_battery_status[i] = 100.0  # Start at 100%
            self.node_sync_time[i] = -1
            
        # Node 0 starts with the file
        self.nodes[0]['has_file'] = True
        self.nodes[0]['percent_received'] = 100.0
        self.node_sync_time[0] = 0
            
        # Calculate Costs
        self.total_cost = self.num_nodes * (self.specs["cost_per_module"] + self.specs["base_node_cost"])

    def calculate_path_loss(self, distance_km):
        """
        Implements Friis path loss equation for more realistic signal degradation.
        Returns signal quality factor (0-1).
        """
        if distance_km == 0:
            return 1.0
        
        # Frequency: 900 MHz = 0.9 GHz
        frequency_ghz = 0.9 if "900HP" in self.specs['name'] else 2.4
        
        # Friis equation: PL(dB) = 20*log10(distance) + 20*log10(frequency) + constant
        path_loss_db = 20 * math.log10(distance_km) + 20 * math.log10(frequency_ghz) + 32.45
        
        # Additional environmental losses (rural area)
        path_loss_db += random.gauss(0, 2)  # Small random variation for interference
        
        # Convert back to linear scale and invert to get quality (0-1)
        signal_quality = max(0, 1 - (path_loss_db / 120))  # Normalized to ~120dB max loss
        return signal_quality

    def build_network_topology(self):
        """Connects nodes if they are within radio range, considering path loss."""
        self.graph.clear()
        for i in range(self.num_nodes):
            self.graph.add_node(i, pos=(self.nodes[i]['x'], self.nodes[i]['y']))
            
        # Check distance between every pair
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                dist = math.sqrt((self.nodes[i]['x'] - self.nodes[j]['x'])**2 + 
                                 (self.nodes[i]['y'] - self.nodes[j]['y'])**2)
                
                if dist <= self.specs['range_km']:
                    # Calculate signal quality using path loss model
                    signal_quality = self.calculate_path_loss(dist)
                    
                    if signal_quality > 0.1:  # Only add edge if signal is strong enough
                        effective_speed = self.specs['speed_kbps'] * signal_quality
                        effective_speed = max(10, effective_speed)  # Floor speed at 10 kbps
                        
                        self.graph.add_edge(i, j, distance=dist, speed=effective_speed, 
                                          signal_quality=signal_quality)

    def calculate_transmission_cost(self, transmission_time_sec, is_transmitting=True):
        """Calculate energy consumed for transmission or reception in mAh"""
        if is_transmitting:
            power_mw = self.specs['power_tx_mw']
        else:
            power_mw = self.specs['power_rx_mw']
        
        # Energy = Power * Time (converting to mAh: mW * sec / (1000 * 3600))
        energy_mah = (power_mw * transmission_time_sec) / 3600000
        return energy_mah

    def run_sync_simulation(self, time_steps=None):
        """
        Simulates data propagating from Node 0 through the network with realistic
        collision handling, battery consumption, and packet queue management.
        """
        if time_steps is None:
            time_steps = SIMULATION_TIME_STEPS
            
        file_size_kb = FILE_SIZE_MB * 8 * 1024
        self.metrics.synced_nodes_history = []
        self.metrics.sync_percentage_history = []
        
        # Track energy consumption
        node_energy = defaultdict(float)
        transmission_log = []
        
        for t in range(time_steps):
            synced_count = sum(1 for n in self.nodes if n['has_file'])
            self.metrics.synced_nodes_history.append(synced_count)
            self.metrics.sync_percentage_history.append((synced_count / self.num_nodes) * 100)
            
            # Stop if all nodes synced
            if synced_count == self.num_nodes:
                self.metrics.time_to_full_sync = t
                self.metrics.total_time_steps = t
                break
            
            # Determine which nodes can transmit (have file, have battery)
            transmitting_nodes = []
            for tx_node in self.nodes:
                if tx_node['has_file'] and self.node_battery_status[tx_node['id']] > 1.0:
                    neighbors = list(self.graph.neighbors(tx_node['id']))
                    # Find neighbors without the file
                    pending_neighbors = [n for n in neighbors if not self.nodes[n]['has_file']]
                    if pending_neighbors:
                        transmitting_nodes.append((tx_node['id'], pending_neighbors))
            
            # Handle transmissions with collision detection per receiver
            successful_transmissions = []
            
            for tx_id, rx_list in transmitting_nodes:
                for rx_id in rx_list:
                    # Check for collision only if multiple transmitters are reaching this receiver
                    concurrent_transmitters = sum(1 for check_tx, check_rx_list in transmitting_nodes if rx_id in check_rx_list)
                    
                    # Apply collision probability based on concurrent transmissions
                    if concurrent_transmitters > 1 and random.random() < (COLLISION_PROBABILITY * concurrent_transmitters):
                        self.metrics.packets_lost += 1
                        continue
                    
                    if self.graph.has_edge(tx_id, rx_id):
                        edge_data = self.graph.get_edge_data(tx_id, rx_id)
                        speed_kbps = edge_data['speed']
                        
                        # Data transferred in this time step (1 second)
                        data_transferred_kb = speed_kbps * 1.0  # 1 second
                        
                        # Deduct energy for transmission
                        tx_energy = self.calculate_transmission_cost(1.0, is_transmitting=True)
                        rx_energy = self.calculate_transmission_cost(1.0, is_transmitting=False)
                        
                        self.nodes[tx_id]['energy_used_mah'] += tx_energy
                        self.nodes[rx_id]['energy_used_mah'] += rx_energy
                        node_energy[tx_id] += tx_energy
                        node_energy[rx_id] += rx_energy
                        
                        # Update battery status
                        self.node_battery_status[tx_id] -= (tx_energy / self.specs['battery_capacity_mah']) * 100
                        self.node_battery_status[rx_id] -= (rx_energy / self.specs['battery_capacity_mah']) * 100
                        
                        # Update receiving node
                        self.nodes[rx_id]['data_received_kb'] += data_transferred_kb
                        self.nodes[rx_id]['percent_received'] = min(100.0, 
                            (self.nodes[rx_id]['data_received_kb'] / file_size_kb) * 100)
                        
                        if self.nodes[rx_id]['percent_received'] >= 100 and not self.nodes[rx_id]['has_file']:
                            self.nodes[rx_id]['has_file'] = True
                            self.node_sync_time[rx_id] = t
                        
                        successful_transmissions.append((tx_id, rx_id, data_transferred_kb))
                        self.metrics.packets_transmitted += 1
            
            # Apply idle energy drain for all nodes
            for node_id in range(self.num_nodes):
                idle_energy = self.specs['power_idle_mw'] / 3600000  # Convert to mAh for 1 second
                self.node_battery_status[node_id] -= (idle_energy / self.specs['battery_capacity_mah']) * 100
                self.node_battery_status[node_id] = max(0, self.node_battery_status[node_id])
                node_energy[node_id] += idle_energy
        
        # Handle case where simulation times out without full sync
        if self.metrics.time_to_full_sync < 0:
            self.metrics.total_time_steps = time_steps
        
        synced_count = sum(1 for n in self.nodes if n['has_file'])
        total_energy_mah = sum(node_energy.values())
        
        # Convert mAh to Wh (assuming 3.7V battery voltage)
        BATTERY_VOLTAGE = 3.7
        total_energy_wh = (total_energy_mah / 1000) * BATTERY_VOLTAGE
        self.metrics.energy_consumed_kwh = total_energy_wh / 1000
        self.metrics.energy_consumed_per_node_wh = total_energy_wh / self.num_nodes if self.num_nodes > 0 else 0
        
        # Calculate average latency (average time for nodes to sync after node 0)
        sync_times = [t for t in self.node_sync_time.values() if t > 0]
        if sync_times:
            # Latency = average time for nodes to propagate data to them
            self.metrics.average_latency_ms = (np.mean(sync_times)) * 1000  # Convert to ms
        else:
            self.metrics.average_latency_ms = 0
        
        # Calculate network reliability (packets successfully transmitted / total)
        total_packets = self.metrics.packets_transmitted + self.metrics.packets_lost
        if total_packets > 0:
            self.metrics.network_reliability_percent = (self.metrics.packets_transmitted / total_packets) * 100
        else:
            self.metrics.network_reliability_percent = 100.0
        
        # Calculate average throughput
        if self.metrics.time_to_full_sync > 0:
            self.metrics.average_throughput_kbps = file_size_kb / self.metrics.time_to_full_sync
        
        self.metrics.network_efficiency_percent = (synced_count / self.num_nodes) * 100
        
        return self.metrics

    def compare_to_fiber(self):
        """Compare LumaNet to fiber optic connectivity with detailed metrics"""
        if nx.is_connected(self.graph):
            mst = nx.minimum_spanning_tree(self.graph, weight='distance')
            total_cable_km = sum(d['distance'] for u, v, d in mst.edges(data=True))
        else:
            total_cable_km = self.num_nodes * 0.5
        
        fiber_cost = total_cable_km * FIBER_SPECS["cost_per_km"]
        fiber_annual_maintenance = total_cable_km * FIBER_SPECS["maintenance_annual"]
        
        lumanet_cost = self.total_cost
        cost_savings_initial = fiber_cost - lumanet_cost
        cost_savings_5_year = cost_savings_initial - (fiber_annual_maintenance * 5)
        
        # ROI Calculation
        roi_percent = (cost_savings_5_year / lumanet_cost * 100) if lumanet_cost > 0 else 0
        payback_years = (fiber_cost / fiber_annual_maintenance) if fiber_annual_maintenance > 0 else 0
        
        comparison = {
            "lumanet_cost": lumanet_cost,
            "fiber_cost": fiber_cost,
            "cost_savings_initial": cost_savings_initial,
            "cost_savings_5_year": cost_savings_5_year,
            "fiber_annual_maintenance": fiber_annual_maintenance,
            "roi_percent": roi_percent,
            "payback_years": payback_years,
            "total_cable_km": total_cable_km
        }
        
        return comparison

    def visualize(self):
        """Creates comprehensive visualization with multiple subplots"""
        pos = {i: (self.nodes[i]['x'], self.nodes[i]['y']) for i in range(self.num_nodes)}
        
        fig = plt.figure(figsize=(18, 12))
        
        # Network Topology Plot
        ax1 = plt.subplot(2, 3, 1)
        colors = ['green' if n['has_file'] else 'red' for n in self.nodes]
        nx.draw(self.graph, pos, node_color=colors, node_size=100, with_labels=False, 
                ax=ax1, alpha=0.7, edge_color='gray', width=0.5)
        ax1.set_title(f"Network Topology: {self.specs['name']}\n(Green = Synced, Red = Pending)")
        ax1.set_xlabel("Kilometers")
        ax1.set_ylabel("Kilometers")
        ax1.grid(True, linestyle='--', alpha=0.3)

        # Sync Progress Over Time
        ax2 = plt.subplot(2, 3, 2)
        ax2.plot(self.metrics.sync_percentage_history, linewidth=2, color='blue')
        ax2.fill_between(range(len(self.metrics.sync_percentage_history)), 
                         self.metrics.sync_percentage_history, alpha=0.3, color='blue')
        ax2.set_title(f"Data Propagation Efficiency\n({FILE_SIZE_MB} MB File)")
        ax2.set_xlabel("Time Steps (Seconds)")
        ax2.set_ylabel("% of Network Synced")
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim([0, 105])

        # Battery Status
        ax3 = plt.subplot(2, 3, 3)
        battery_levels = [self.node_battery_status[i] for i in range(self.num_nodes)]
        ax3.bar(range(self.num_nodes), battery_levels, color='orange', alpha=0.7)
        ax3.set_title("Battery Status (% Remaining)")
        ax3.set_xlabel("Node ID")
        ax3.set_ylabel("Battery %")
        ax3.set_ylim([0, 105])
        ax3.grid(True, alpha=0.3, axis='y')

        # Number of Synced Nodes Over Time
        ax4 = plt.subplot(2, 3, 4)
        ax4.plot(self.metrics.synced_nodes_history, linewidth=2, color='green', marker='o', markersize=3)
        ax4.fill_between(range(len(self.metrics.synced_nodes_history)), 
                         self.metrics.synced_nodes_history, alpha=0.3, color='green')
        ax4.set_title("Cumulative Synced Nodes")
        ax4.set_xlabel("Time Steps (Seconds)")
        ax4.set_ylabel("Number of Synced Nodes")
        ax4.grid(True, alpha=0.3)

        # Sync Time Distribution
        ax5 = plt.subplot(2, 3, 5)
        sync_times = [t for t in self.node_sync_time.values() if t >= 0]
        if sync_times:
            ax5.hist(sync_times, bins=20, color='purple', alpha=0.7, edgecolor='black')
            ax5.set_title("Sync Time Distribution")
            ax5.set_xlabel("Time to Sync (Seconds)")
            ax5.set_ylabel("Number of Nodes")
            ax5.grid(True, alpha=0.3, axis='y')

        # Cost Comparison
        ax6 = plt.subplot(2, 3, 6)
        self._plot_cost_comparison(ax6)

        plt.tight_layout()
        plt.show()

    def _plot_cost_comparison(self, ax):
        """Helper method to plot cost comparison"""
        if nx.is_connected(self.graph):
            mst = nx.minimum_spanning_tree(self.graph, weight='distance')
            total_cable_km = sum(d['distance'] for u, v, d in mst.edges(data=True))
        else:
            total_cable_km = self.num_nodes * 0.5
            
        fiber_cost = total_cable_km * FIBER_SPECS["cost_per_km"]
        fiber_maintenance = total_cable_km * FIBER_SPECS["maintenance_annual"]
        
        # 5-year comparison
        years = [0, 1, 2, 3, 4, 5]
        lumanet_costs = [self.total_cost] * 6  # No additional cost
        fiber_costs = [fiber_cost + (fiber_maintenance * y) for y in years]
        
        ax.plot(years, lumanet_costs, 'o-', linewidth=2, markersize=8, label='LumaNet', color='#2ecc71')
        ax.plot(years, fiber_costs, 's-', linewidth=2, markersize=8, label='Fiber Optic', color='#e74c3c')
        
        ax.set_xlabel("Years")
        ax.set_ylabel("Cumulative Cost ($)")
        ax.set_title("5-Year Cost Comparison")
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}k'))

    def create_advanced_visualization(self):
        """Create additional detailed visualizations for energy and performance analysis"""
        fig = plt.figure(figsize=(16, 10))
        
        # Energy consumption per node
        ax1 = plt.subplot(2, 3, 1)
        energy_per_node = [self.nodes[i]['energy_used_mah'] for i in range(self.num_nodes)]
        ax1.bar(range(self.num_nodes), energy_per_node, color='orange', alpha=0.7)
        ax1.set_title("Energy Consumption per Node (mAh)")
        ax1.set_xlabel("Node ID")
        ax1.set_ylabel("Energy (mAh)")
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Node sync time distribution
        ax2 = plt.subplot(2, 3, 2)
        sync_times = [t for t in self.node_sync_time.values() if t >= 0]
        if sync_times:
            ax2.hist(sync_times, bins=max(10, len(set(sync_times))//2), color='purple', alpha=0.7, edgecolor='black')
            ax2.set_title("Sync Time Distribution")
            ax2.set_xlabel("Seconds to Sync")
            ax2.set_ylabel("Number of Nodes")
            ax2.grid(True, alpha=0.3, axis='y')
        
        # Network degree distribution
        ax3 = plt.subplot(2, 3, 3)
        degrees = [d for n, d in self.graph.degree()]
        ax3.hist(degrees, bins=15, color='teal', alpha=0.7, edgecolor='black')
        ax3.set_title("Network Degree Distribution")
        ax3.set_xlabel("Number of Neighbors")
        ax3.set_ylabel("Number of Nodes")
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Sync progress curve
        ax4 = plt.subplot(2, 3, 4)
        ax4.plot(self.metrics.synced_nodes_history, linewidth=2.5, color='darkgreen', marker='o', markersize=4)
        ax4.fill_between(range(len(self.metrics.synced_nodes_history)), 
                         self.metrics.synced_nodes_history, alpha=0.2, color='green')
        ax4.set_title(f"Network Growth ({FILE_SIZE_MB} MB sync)")
        ax4.set_xlabel("Time (seconds)")
        ax4.set_ylabel("Synced Nodes")
        ax4.grid(True, alpha=0.3)
        
        # Efficiency metrics
        ax5 = plt.subplot(2, 3, 5)
        metrics_names = ['Sync\nEfficiency', 'Network\nReliability']
        metrics_values = [self.metrics.network_efficiency_percent, self.metrics.network_reliability_percent]
        colors = ['#2ecc71' if v >= 90 else '#f39c12' if v >= 70 else '#e74c3c' for v in metrics_values]
        bars = ax5.bar(metrics_names, metrics_values, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax5.set_ylabel("Percentage (%)")
        ax5.set_title("Key Efficiency Metrics")
        ax5.set_ylim([0, 105])
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, val in zip(bars, metrics_values):
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Range vs actual coverage
        ax6 = plt.subplot(2, 3, 6)
        max_range = self.specs['range_km']
        distances = []
        for u, v, d in self.graph.edges(data=True):
            distances.append(d['distance'])
        
        if distances:
            ax6.hist(distances, bins=15, color='skyblue', alpha=0.7, edgecolor='black')
            ax6.axvline(x=np.mean(distances), color='red', linestyle='--', linewidth=2, label=f'Avg: {np.mean(distances):.1f} km')
            ax6.axvline(x=max_range, color='orange', linestyle='--', linewidth=2, label=f'Max Range: {max_range} km')
            ax6.set_title("Link Distance Distribution")
            ax6.set_xlabel("Distance (km)")
            ax6.set_ylabel("Number of Links")
            ax6.legend()
            ax6.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()

    def _plot_cost_comparison(self, ax):
        """Helper method to plot cost comparison"""
        if nx.is_connected(self.graph):
            mst = nx.minimum_spanning_tree(self.graph, weight='distance')
            total_cable_km = sum(d['distance'] for u, v, d in mst.edges(data=True))
        else:
            total_cable_km = self.num_nodes * 0.5
            
        fiber_cost = total_cable_km * FIBER_SPECS["cost_per_km"]
        
        technologies = ['LumaNet\n(Wireless)', 'Fiber\nOptic']
        costs = [self.total_cost, fiber_cost]
        colors = ['#2ecc71', '#e74c3c']
        
        bars = ax.bar(technologies, costs, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
        ax.set_ylabel("Cost ($)")
        ax.set_title("Cost Comparison Analysis")
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, cost in zip(bars, costs):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${cost:,.0f}',
                   ha='center', va='bottom', fontweight='bold')

    def generate_report(self):
        """Generate comprehensive simulation report"""
        if nx.is_connected(self.graph):
            mst = nx.minimum_spanning_tree(self.graph, weight='distance')
            total_cable_km = sum(d['distance'] for u, v, d in mst.edges(data=True))
        else:
            total_cable_km = self.num_nodes * 0.5
            
        fiber_cost = total_cable_km * FIBER_SPECS["cost_per_km"]
        fiber_annual_maintenance = total_cable_km * FIBER_SPECS["maintenance_annual"]
        
        # Calculate 5-year cost comparison
        # LumaNet: Initial cost only (wireless, minimal maintenance)
        lumanet_5year_cost = self.total_cost  # No annual maintenance for wireless mesh
        
        # Fiber: Initial + 5 years of maintenance
        fiber_5year_cost = fiber_cost + (fiber_annual_maintenance * 5)
        
        # Savings calculation
        savings_initial = fiber_cost - self.total_cost
        savings_5_year = fiber_5year_cost - lumanet_5year_cost
        
        # ROI Calculation
        roi_percent = (savings_5_year / lumanet_5year_cost * 100) if lumanet_5year_cost > 0 else 0
        payback_years = (fiber_cost / fiber_annual_maintenance) if fiber_annual_maintenance > 0 else 0
        
        avg_sync_time = self.metrics.time_to_full_sync if self.metrics.time_to_full_sync >= 0 else -1
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "simulation_config": {
                "num_nodes": self.num_nodes,
                "area_size_km": self.area_size,
                "file_size_mb": FILE_SIZE_MB,
                "hardware_type": self.specs['name'],
                "simulation_time_steps": self.metrics.total_time_steps
            },
            "network_topology": {
                "total_edges": self.graph.number_of_edges(),
                "average_degree": sum(dict(self.graph.degree()).values()) / self.num_nodes if self.num_nodes > 0 else 0,
                "network_connectivity": "Connected" if nx.is_connected(self.graph) else "Fragmented"
            },
            "performance_metrics": {
                "time_to_full_sync_seconds": avg_sync_time,
                "nodes_synced": sum(1 for n in self.nodes if n['has_file']),
                "sync_efficiency_percent": self.metrics.network_efficiency_percent,
                "network_reliability_percent": self.metrics.network_reliability_percent,
                "average_throughput_kbps": self.metrics.average_throughput_kbps,
                "average_latency_ms": self.metrics.average_latency_ms,
                "total_energy_consumed_wh": self.metrics.energy_consumed_kwh * 1000,
                "total_energy_consumed_kwh": self.metrics.energy_consumed_kwh,
                "energy_per_node_wh": self.metrics.energy_consumed_per_node_wh,
                "packets_transmitted": self.metrics.packets_transmitted,
                "packets_lost": self.metrics.packets_lost,
                "average_battery_remaining": sum(self.node_battery_status.values()) / self.num_nodes if self.num_nodes > 0 else 0
            },
            "cost_analysis": {
                "lumanet_initial_cost": round(self.total_cost, 2),
                "fiber_initial_cost": round(fiber_cost, 2),
                "initial_cost_savings": round(savings_initial, 2),
                "fiber_annual_maintenance": round(fiber_annual_maintenance, 2),
                "lumanet_5year_cost": round(lumanet_5year_cost, 2),
                "fiber_5year_cost": round(fiber_5year_cost, 2),
                "5_year_total_savings": round(savings_5_year, 2),
                "cost_multiplier": round(fiber_cost / self.total_cost, 2) if self.total_cost > 0 else 0,
                "payback_years": round(payback_years, 2),
                "roi_percent": round(roi_percent, 2)
            },
            "hardware_specs": self.specs
        }
        
        return report

    def print_detailed_report(self):
        """Print formatted report to console"""
        report = self.generate_report()
        
        print("\n" + "="*70)
        print(f"LUMANET SIMULATION REPORT - {self.specs['name']}")
        print("="*70)
        print(f"\nSimulation Configuration:")
        print(f"  • Nodes: {self.num_nodes}")
        print(f"  • Coverage Area: {self.area_size} x {self.area_size} km")
        print(f"  • File Size: {FILE_SIZE_MB} MB")
        print(f"  • Simulation Duration: {report['simulation_config']['simulation_time_steps']} seconds")
        
        print(f"\nNetwork Topology:")
        print(f"  • Edges (Links): {report['network_topology']['total_edges']}")
        print(f"  • Average Node Degree: {report['network_topology']['average_degree']:.2f}")
        print(f"  • Connectivity: {report['network_topology']['network_connectivity']}")
        
        print(f"\nPerformance Metrics:")
        print(f"  • Time to Full Sync: {report['performance_metrics']['time_to_full_sync_seconds']} seconds")
        print(f"  • Nodes Successfully Synced: {report['performance_metrics']['nodes_synced']}/{self.num_nodes}")
        print(f"  • Sync Efficiency: {report['performance_metrics']['sync_efficiency_percent']:.1f}%")
        print(f"  • Network Reliability: {report['performance_metrics']['network_reliability_percent']:.1f}%")
        print(f"  • Average Throughput: {report['performance_metrics']['average_throughput_kbps']:.1f} kbps")
        print(f"  • Average Latency: {report['performance_metrics']['average_latency_ms']:.1f} ms")
        print(f"  • Total Energy Consumed: {report['performance_metrics']['total_energy_consumed_wh']:.2f} Wh ({report['performance_metrics']['total_energy_consumed_kwh']:.4f} kWh)")
        print(f"  • Energy per Node: {report['performance_metrics']['energy_per_node_wh']:.2f} Wh")
        print(f"  • Packets Transmitted: {report['performance_metrics']['packets_transmitted']}")
        print(f"  • Packets Lost: {report['performance_metrics']['packets_lost']}")
        print(f"  • Average Battery Remaining: {report['performance_metrics']['average_battery_remaining']:.1f}%")
        
        print(f"\nCost Analysis:")
        print(f"  • LumaNet Network Cost: ${report['cost_analysis']['lumanet_initial_cost']:,.2f}")
        print(f"  • Fiber Optic Network Cost: ${report['cost_analysis']['fiber_initial_cost']:,.2f}")
        print(f"  • Initial Cost Savings: ${report['cost_analysis']['initial_cost_savings']:,.2f}")
        print(f"  • Fiber Annual Maintenance: ${report['cost_analysis']['fiber_annual_maintenance']:,.2f}")
        print(f"  • 5-Year Total Savings: ${report['cost_analysis']['5_year_total_savings']:,.2f}")
        print(f"  • Cost Multiplier: Fiber is {report['cost_analysis']['cost_multiplier']:.1f}x more expensive")
        print(f"  • Payback Period: {report['cost_analysis']['payback_years']:.2f} years")
        
        print("\n" + "="*70 + "\n")
        
        return report
        
# SCENARIO COMPARISON CLASS

class ScenarioComparison:
    """Compare multiple network configurations"""
    
    def __init__(self):
        self.results = []
    
    def run_comparison(self, node_counts, hardware_types, file_sizes):
        """Run simulations across multiple parameters"""
        print("\n" + "="*70)
        print("RUNNING MULTI-SCENARIO ANALYSIS")
        print("="*70 + "\n")
        
        scenario_num = 0
        total_scenarios = len(node_counts) * len(hardware_types) * len(file_sizes)
        
        for num_nodes in node_counts:
            for hw_type in hardware_types:
                for file_mb in file_sizes:
                    scenario_num += 1
                    print(f"[{scenario_num}/{total_scenarios}] Nodes: {num_nodes}, Hardware: {hw_type.replace('XBee_', '')}, File: {file_mb}MB")
                    
                    # Temporarily set globals
                    global FILE_SIZE_MB, NUM_NODES, SIMULATION_TYPE
                    old_file_mb = FILE_SIZE_MB
                    old_nodes = NUM_NODES
                    old_hw = SIMULATION_TYPE
                    
                    FILE_SIZE_MB = file_mb
                    NUM_NODES = num_nodes
                    SIMULATION_TYPE = hw_type
                    
                    # Run simulation
                    sim = LumaNetSimulation(num_nodes, AREA_SIZE_KM, hw_type)
                    sim.build_network_topology()
                    sim.run_sync_simulation()
                    report = sim.generate_report()
                    
                    self.results.append(report)
                    
                    # Restore globals
                    FILE_SIZE_MB = old_file_mb
                    NUM_NODES = old_nodes
                    SIMULATION_TYPE = old_hw
        
        print(f"\n✓ Completed {total_scenarios} scenarios.\n")
    
    def plot_comparison(self):
        """Visualize scenario comparison results"""
        if not self.results:
            print("No results to plot")
            return
        
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Network Configuration Comparison', fontsize=16, fontweight='bold')
        
        # Organize data by configuration
        configs = {}
        for r in self.results:
            hw = r['simulation_config']['hardware_type'].replace('LumaNet (', '').replace(')', '')
            key = f"{r['simulation_config']['num_nodes']} nodes - {hw}"
            if key not in configs:
                configs[key] = r
        
        sorted_keys = sorted(configs.keys())
        
        # Plot 1: Sync time
        ax1 = plt.subplot(2, 3, 1)
        sync_times = [configs[k]['performance_metrics']['time_to_full_sync_seconds'] for k in sorted_keys]
        ax1.barh(range(len(sorted_keys)), sync_times, color='steelblue', alpha=0.7)
        ax1.set_yticks(range(len(sorted_keys)))
        ax1.set_yticklabels(sorted_keys, fontsize=9)
        ax1.set_xlabel('Time to Sync (seconds)')
        ax1.set_title('Synchronization Speed')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Plot 2: Cost
        ax2 = plt.subplot(2, 3, 2)
        costs = [configs[k]['cost_analysis']['lumanet_initial_cost'] for k in sorted_keys]
        ax2.barh(range(len(sorted_keys)), costs, color='green', alpha=0.7)
        ax2.set_yticks(range(len(sorted_keys)))
        ax2.set_yticklabels(sorted_keys, fontsize=9)
        ax2.set_xlabel('Initial Cost ($)')
        ax2.set_title('Network Cost')
        ax2.grid(True, alpha=0.3, axis='x')
        ax2.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}k'))
        
        # Plot 3: 5-year savings
        ax3 = plt.subplot(2, 3, 3)
        savings = [configs[k]['cost_analysis']['5_year_total_savings'] for k in sorted_keys]
        ax3.barh(range(len(sorted_keys)), savings, color='darkgreen', alpha=0.7)
        ax3.set_yticks(range(len(sorted_keys)))
        ax3.set_yticklabels(sorted_keys, fontsize=9)
        ax3.set_xlabel('5-Year Savings ($)')
        ax3.set_title('Economic Advantage')
        ax3.grid(True, alpha=0.3, axis='x')
        ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}k'))
        
        # Plot 4: Energy consumption
        ax4 = plt.subplot(2, 3, 4)
        energy = [configs[k]['performance_metrics']['total_energy_consumed_wh'] for k in sorted_keys]
        ax4.barh(range(len(sorted_keys)), energy, color='orange', alpha=0.7)
        ax4.set_yticks(range(len(sorted_keys)))
        ax4.set_yticklabels(sorted_keys, fontsize=9)
        ax4.set_xlabel('Energy Consumed (Wh)')
        ax4.set_title('Power Consumption')
        ax4.grid(True, alpha=0.3, axis='x')
        
        # Plot 5: Reliability
        ax5 = plt.subplot(2, 3, 5)
        reliability = [configs[k]['performance_metrics']['network_reliability_percent'] for k in sorted_keys]
        ax5.barh(range(len(sorted_keys)), reliability, color='purple', alpha=0.7)
        ax5.set_yticks(range(len(sorted_keys)))
        ax5.set_yticklabels(sorted_keys, fontsize=9)
        ax5.set_xlabel('Reliability (%)')
        ax5.set_title('Network Reliability')
        ax5.set_xlim([0, 105])
        ax5.grid(True, alpha=0.3, axis='x')
        
        # Plot 6: ROI percentage
        ax6 = plt.subplot(2, 3, 6)
        roi = [configs[k]['cost_analysis']['roi_percent'] for k in sorted_keys]
        ax6.barh(range(len(sorted_keys)), roi, color='teal', alpha=0.7)
        ax6.set_yticks(range(len(sorted_keys)))
        ax6.set_yticklabels(sorted_keys, fontsize=9)
        ax6.set_xlabel('ROI (%)')
        ax6.set_title('Return on Investment (5-year)')
        ax6.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.show()

# RUN SIMULATION

# Initialize
sim = LumaNetSimulation(NUM_NODES, AREA_SIZE_KM, SIMULATION_TYPE)

# Build & Run
sim.build_network_topology()
sim.run_sync_simulation()

# Generate and print report
report = sim.print_detailed_report()

# Compare to fiber
comparison = sim.compare_to_fiber()
fiber_5year = comparison['fiber_cost'] + (comparison['fiber_annual_maintenance'] * 5)
lumanet_5year = comparison['lumanet_cost']
print(f"\n5-Year Cost-Benefit Analysis:")
print(f"  • LumaNet 5-year cost: ${lumanet_5year:,.2f}")
print(f"  • Fiber 5-year cost: ${fiber_5year:,.2f}")
print(f"  • 5-year savings: ${fiber_5year - lumanet_5year:,.2f}")
print(f"  • LumaNet requires {comparison['total_cable_km']:.1f} km of infrastructure equivalent")

# Create visualizations
print("\nGenerating primary visualization...")
sim.visualize()

print("Generating advanced metrics visualization...")
sim.create_advanced_visualization()

print(f"✓ Simulation Complete. Time to sync {FILE_SIZE_MB} MB to {NUM_NODES} nodes: {sim.metrics.time_to_full_sync} seconds.")
