#!/bin/bash

echo "📡 Setting up Pi as WiFi Hotspot for LumaNet"
echo "============================================"

# Install required packages
echo "Installing hotspot packages..."
sudo apt update
sudo apt install -y hostapd dnsmasq

# Stop services
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Configure hostapd
echo "Configuring WiFi hotspot..."
sudo tee /etc/hostapd/hostapd.conf > /dev/null << 'EOF'
interface=wlan0
driver=nl80211
ssid=LumaNet-Mesh
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=LumaNet123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF

# Configure dnsmasq
echo "Configuring DHCP..."
sudo tee /etc/dnsmasq.conf > /dev/null << 'EOF'
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

# Configure static IP for wlan0
echo "Configuring static IP..."
sudo tee -a /etc/dhcpcd.conf > /dev/null << 'EOF'

# LumaNet Hotspot Configuration
interface wlan0
static ip_address=192.168.4.1/24
nohook wpa_supplicant
EOF

# Enable IP forwarding
echo "Enabling IP forwarding..."
echo 'net.ipv4.ip_forward=1' | sudo tee -a /etc/sysctl.conf

# Configure hostapd daemon
echo "DAEMON_CONF=\"/etc/hostapd/hostapd.conf\"" | sudo tee -a /etc/default/hostapd

# Enable services
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

echo ""
echo "✅ Pi Hotspot Configuration Complete!"
echo ""
echo "📋 Hotspot Details:"
echo "  Network Name: LumaNet-Mesh"
echo "  Password: LumaNet123"
echo "  Pi IP: 192.168.4.1"
echo "  LumaNet URL: http://192.168.4.1:3000"
echo ""
echo "🔄 Reboot required to activate hotspot:"
echo "  sudo reboot"
echo ""
echo "📱 After reboot:"
echo "  1. Students connect to 'LumaNet-Mesh' WiFi"
echo "  2. Use password: LumaNet123"
echo "  3. Open browser to: http://192.168.4.1:3000"
echo "  4. Login: admin / admin123"
