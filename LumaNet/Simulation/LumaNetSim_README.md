# LumaNetSim - Offline Network Simulation

A comprehensive Python simulation for modeling low-power wireless mesh networks designed for regions without stable internet or power infrastructure. This tool enables researchers and engineers to evaluate the efficiency and cost-effectiveness of wireless mesh networks (like your LumaNet prototype using Raspberry Pi 5, XBee Pro 900 HP, and XBee 3 Pro modules) compared to traditional wired infrastructure solutions.

## Features

### Network Simulation
- **Realistic topology modeling**: Nodes randomly distributed across configurable geographic areas
- **Path loss simulation**: Friis equation-based signal degradation for realistic wireless propagation
- **Multi-hop data propagation**: Data spreads from source node (Node 0) through mesh network
- **Collision detection**: Accounts for packet collisions when multiple nodes transmit simultaneously
- **Battery tracking**: Monitors energy consumption for transmission, reception, and idle modes

### Performance Metrics
- **Synchronization metrics**:
  - Time to full sync (propagation latency)
  - Sync efficiency (% of nodes successfully synced)
  - Average node latency
  - Sync time distribution across network

- **Network reliability**:
  - Packet transmission success rate
  - Packets lost to collisions
  - Network connectivity status (connected/fragmented)
  - Average throughput (kbps)

- **Energy analysis**:
  - Per-node energy consumption (mAh)
  - Battery depletion rate
  - Energy per MB transferred
  - Idle vs. active power modes

### Cost Analysis
- **Infrastructure comparison**:
  - LumaNet wireless mesh cost
  - Fiber optic equivalent cost
  - Annual maintenance comparison
  - 5-year total cost of ownership
  - Return on investment (ROI)

### Visualizations
1. **Network Topology**: Shows node positions and connectivity (green=synced, red=pending)
2. **Sync Progress**: Real-time percentage of network synced over time
3. **Battery Status**: Individual node battery levels
4. **Cumulative Nodes**: Number of synced nodes timeline
5. **Sync Distribution**: Histogram of node sync times
6. **Cost Comparison**: 5-year cost trajectory analysis
7. **Advanced Metrics Dashboard**:
   - Energy consumption per node
   - Sync time distribution
   - Network degree distribution
   - Link distance distribution
   - Efficiency metrics
   - Infrastructure equivalency

## Hardware Profiles

### XBee 900 HP (Long Range, Low Power)
- **Range**: 8 km (realistic rural coverage)
- **Speed**: 200 kbps
- **Power TX**: 950 mW | RX: 55 mW | Idle: 15 mW
- **Cost**: $75 (module) + $100 (node infrastructure)
- **Best for**: Large area coverage, remote regions

### XBee 3 Pro (High Speed, Moderate Range)
- **Range**: 1.5 km
- **Speed**: 250 kbps
- **Power TX**: 500 mW | RX: 85 mW | Idle: 35 mW
- **Cost**: $22 (module) + $100 (node infrastructure)
- **Best for**: Dense networks, high throughput needs

## Configuration

### Quick Start - Modify Parameters

Open `LumaNetSim.py` and adjust these parameters (lines 54-62):

```python
NUM_NODES = 50             # Change to 25, 75, 100, etc.
AREA_SIZE_KM = 10          # Coverage area (10x10 km in this example)
FILE_SIZE_MB = 5           # Data to synchronize (5 MB ~2 min at 200kbps)
SIMULATION_TYPE = "XBee_900HP"  # Or "XBee_3_Pro"
SIMULATION_TIME_STEPS = 500     # Maximum simulation duration
COLLISION_PROBABILITY = 0.02    # 2% chance of collision
MAX_HOPS = 3               # Maximum hops to prevent loops
```

### Running the Simulation

```bash
python LumaNetSim.py
```

The simulation will:
1. Initialize node positions randomly across the area
2. Build network topology based on radio range
3. Run synchronization simulation
4. Generate detailed report with metrics
5. Display cost-benefit analysis
6. Show visualizations (6 graphs + advanced metrics)

## Simulation Metrics Explained

### Time to Full Sync
Time in seconds for data to propagate from source to all nodes. Depends on:
- File size and transmission speeds
- Network topology and connectivity
- Collision rates and retransmission delays

### Sync Efficiency
Percentage of nodes that successfully received the file. Should be 100% for connected networks.

### Network Reliability
Successful transmission rate = (Packets Transmitted) / (Packets Transmitted + Lost)
- 100%: No collisions
- <80%: High collision rate (consider reducing node density or transmission power)

### Average Throughput
Effective data rate = File Size / Time to Sync

### Energy Consumption
Total energy in Wh spent on transmission, reception, and idle listening. Key for:
- Battery life estimation
- Solar panel sizing
- Operational costs

### Cost Analysis
LumaNet achieves **100-150x cost savings** compared to fiber optic in typical rural deployments:
- No excavation or pole installation required
- Minimal maintenance (battery/solar panel management)
- Can be deployed in days vs. months for fiber
- Easier to scale and modify

## Advanced Usage

### Running Multi-Scenario Comparison

Uncomment this section in the main execution block to compare multiple configurations:

```python
# Create scenario comparison
comparison = ScenarioComparison()
comparison.run_comparison(
    node_counts=[25, 50, 75, 100],
    hardware_types=["XBee_900HP", "XBee_3_Pro"],
    file_sizes=[2, 5, 10]
)
comparison.plot_comparison()
```

This will run 24 scenarios and create comparative visualizations showing:
- Sync speed across configurations
- Cost implications
- 5-year savings
- Energy consumption
- Network reliability
- ROI percentages

## Understanding the Results

### Example Output
```
Time to Full Sync: 331 seconds
Nodes Successfully Synced: 50/50
Sync Efficiency: 100.0%
Network Reliability: 81.6%
Average Throughput: 131.7 kbps

LumaNet Network Cost: $8,750.00
Fiber Optic Network Cost: $1,171,629.35
5-Year Total Savings: $2,334,508.70
Cost Multiplier: Fiber is 133.9x more expensive
```

### Interpretation
- **331 seconds**: ~5.5 minutes to sync 5MB across 50 nodes
- **100% efficiency**: All nodes received data successfully
- **81.6% reliability**: 81.6% of transmission attempts succeeded
- **$2.3M savings**: LumaNet is dramatically cheaper over 5 years
- **133.9x**: Fiber costs 134x more than wireless mesh

## Key Insights & Recommendations

1. **Network Size Matters**
   - Larger networks take exponentially longer to sync
   - Tree-like topologies are fastest; mesh provides redundancy

2. **Hardware Selection**
   - 900 HP: Better for sparse, large areas (8 km range)
   - 3 Pro: Better for dense urban/suburban (1.5 km range)
   - Mixed networks provide optimal cost-benefit

3. **Topology Optimization**
   - Ensure network is fully connected (check "Connectivity" output)
   - Target average node degree of 5-10 for redundancy without overkill
   - Aim for <2 km average inter-node distance

4. **Power Considerations**
   - 50 node network consumes ~0.02-0.05 Wh per synchronization
   - With 10,000 mAh batteries: 200,000-500,000+ syncs possible
   - Solar panels required for continuous operation

5. **Cost Justification**
   - LumaNet ROI becomes positive in <1 year
   - 5-year savings typically exceed $1-2 million for 50+ nodes
   - Fiber maintenance costs are significant factor

## Customization & Extensions

### Adding Custom Hardware Profiles
```python
HARDWARE_SPECS = {
    "Custom_Device": {
        "name": "My Device Name",
        "range_km": 5.0,
        "speed_kbps": 150,
        "cost_per_module": 50.00,
        "base_node_cost": 80.00,
        "power_tx_mw": 800,
        "power_rx_mw": 60,
        "power_idle_mw": 20,
        "battery_capacity_mah": 5000
    }
}
```

### Modifying Terrain Effects
Current path loss uses Friis equation with 2dB standard deviation random variation. To add terrain:
1. Modify `calculate_path_loss()` method
2. Add terrain height map
3. Apply 3D distance calculations
4. Consider vegetation/obstruction factors

### Extending the Simulation
The framework supports:
- Multiple concurrent data transfers
- Variable file sizes
- Prioritized data delivery
- Directional antennas
- Repeater nodes with longer range
- Gateway nodes with internet connectivity

## Technical Implementation

### Path Loss Model
Uses free-space Friis equation with environmental correction:
```
PL(dB) = 20*log10(d) + 20*log10(f) + 32.45 + N(0, 2)
Signal Quality = 1 - (PL / 120)  # Normalized 0-1
```

### Energy Model
```
Energy (mAh) = (Power (mW) × Time (sec)) / 3600000
Battery % = 100 - (Energy / Battery Capacity mAh) × 100
```

### Synchronization Algorithm
1. Node 0 starts with complete file
2. Each time step, synced nodes transmit to unsynced neighbors
3. Data accumulates until threshold (100% received)
4. Nodes become sources for further propagation
5. Collisions reduce transmission success rate

## Troubleshooting

### Network Not Connecting
- Check `Network Topology: Connectivity` - should be "Connected"
- Increase `AREA_SIZE_KM` or reduce `NUM_NODES`
- Use longer-range hardware (XBee_900HP)

### Sync Takes Too Long
- Reduce `FILE_SIZE_MB` (network throughput limited)
- Use higher-speed hardware
- Increase node density (reduce `AREA_SIZE_KM` or add more nodes)

### High Packet Loss
- Reduce `COLLISION_PROBABILITY` (interference less likely)
- Increase inter-node distances
- Add more routing diversity (higher node degree)

### Energy Unrealistic
- Verify `power_tx_mw`, `power_rx_mw` match your hardware specs
- Check battery voltage is 3.7V (standard for Li-ion)
- Confirm `battery_capacity_mah` matches your power bank

## Dependencies

```
numpy
networkx
matplotlib
```

Install with: `pip install numpy networkx matplotlib`

## Performance Notes

- **Computational complexity**: O(n²) for topology (n = number of nodes)
- **Memory usage**: ~1KB per node + 10KB per edge
- **Simulation speed**: 500 time steps × 50 nodes ≈ 5-10 seconds

For large-scale simulations (>500 nodes):
- Consider reducing `SIMULATION_TIME_STEPS`
- Use spatial indexing for neighbor discovery
- Parallelize scenario comparisons

## Citation & Usage

This simulation is designed for:
- Network feasibility studies
- Cost-benefit analysis
- Hardware selection
- Community infrastructure planning
- Emergency/disaster communication systems

## Future Enhancements

- [ ] Mobile node support
- [ ] Directional antenna models
- [ ] Multi-hop scheduling optimization
- [ ] Packet routing protocols (AODV, DSR)
- [ ] QoS metrics
- [ ] 3D terrain mapping
- [ ] Real GPS coordinate import
- [ ] Time-dependent analysis (day/night power)
- [ ] Video: Network animation export

---

**Created for**: LumaNet - Offline community networks for underserved regions

**Last Updated**: January 2026

**Author**: Developed for Algorithmic Trading / Connectivity Projects
