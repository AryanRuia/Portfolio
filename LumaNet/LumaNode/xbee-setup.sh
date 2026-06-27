#!/bin/bash

echo "🔧 LumaNet XBee Configuration & Testing Suite"
echo "============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if XBee is connected
check_xbee_hardware() {
    echo "🔍 Checking XBee hardware connection..."
    
    if lsusb | grep -i ftdi > /dev/null; then
        echo -e "${GREEN}✅ FTDI device detected${NC}"
        lsusb | grep -i ftdi
    else
        echo -e "${RED}❌ No FTDI device found${NC}"
        echo "Please check:"
        echo "  1. XBee is inserted into USB adapter"
        echo "  2. USB adapter is connected to Pi"
        echo "  3. Wait 10 seconds after connecting"
        return 1
    fi
    
    if [ -e /dev/ttyUSB0 ]; then
        echo -e "${GREEN}✅ Serial device /dev/ttyUSB0 found${NC}"
        ls -la /dev/ttyUSB0
    else
        echo -e "${RED}❌ /dev/ttyUSB0 not found${NC}"
        echo "Available serial devices:"
        ls -la /dev/tty* | grep USB || echo "No USB serial devices found"
        return 1
    fi
    
    if [ -r /dev/ttyUSB0 ] && [ -w /dev/ttyUSB0 ]; then
        echo -e "${GREEN}✅ Permissions OK${NC}"
    else
        echo -e "${YELLOW}⚠️  Permission issue${NC}"
        echo "Run: sudo usermod -a -G dialout $USER"
        echo "Then logout and login again"
        return 1
    fi
    
    return 0
}

# Test XBee communication
test_xbee_communication() {
    echo "🔌 Testing XBee communication..."
    
    if ! command -v node > /dev/null; then
        echo -e "${RED}❌ Node.js not found${NC}"
        return 1
    fi
    
    if [ ! -d "server/node_modules" ]; then
        echo -e "${RED}❌ Node modules not found. Run 'npm install' in server directory${NC}"
        return 1
    fi
    
    cat > test_xbee_comm.js << 'EOF'
const { SerialPort } = require('serialport');
const { DelimiterParser } = require('@serialport/parser-delimiter');

console.log('🔌 Starting XBee communication test...');

const port = new SerialPort({
    path: '/dev/ttyUSB0',
    baudRate: 115200,
    dataBits: 8,
    parity: 'none',
    stopBits: 1
});

const parser = port.pipe(new DelimiterParser({ delimiter: '\n' }));

let messageCount = 0;
let receivedCount = 0;

port.on('open', () => {
    console.log('✅ XBee port opened successfully');
    
    const interval = setInterval(() => {
        messageCount++;
        const message = JSON.stringify({
            type: 'test',
            nodeId: process.env.NODE_ID || 'test-node',
            counter: messageCount,
            timestamp: Date.now()
        });
        
        port.write(message + '\n');
        console.log(`📤 Sent message ${messageCount}: ${message}`);
        
        if (messageCount >= 5) {
            clearInterval(interval);
            setTimeout(() => {
                port.close();
                console.log(`\n📊 Test Summary:`);
                console.log(`   Messages sent: ${messageCount}`);
                console.log(`   Messages received: ${receivedCount}`);
                console.log('🔌 XBee communication test completed');
                process.exit(0);
            }, 3000);
        }
    }, 2000);
});

parser.on('data', (data) => {
    receivedCount++;
    const message = data.toString().trim();
    console.log(`📥 Received message ${receivedCount}: ${message}`);
});

port.on('error', (err) => {
    console.error('❌ XBee error:', err.message);
    process.exit(1);
});

port.on('close', () => {
    console.log('🔌 XBee connection closed');
});

// Timeout after 15 seconds
setTimeout(() => {
    console.log('⏰ Test timeout reached');
    port.close();
    process.exit(0);
}, 15000);
EOF
    
    cd server && node ../test_xbee_comm.js
    cd ..
    rm test_xbee_comm.js
}

# Configure XBee as coordinator
configure_coordinator() {
    echo "🎯 Configuring XBee as Coordinator (Node 1)..."
    
    cat > xbee_coordinator_config.txt << 'EOF'
+++
ATID 1234
ATCE 1
ATMY 0
ATAP 1
ATBD 7
ATCH 0C
ATWR
ATCN
EOF
    
    echo "Configuration commands saved to xbee_coordinator_config.txt"
    echo ""
    echo "Manual configuration steps:"
    echo "1. Run: sudo minicom -D /dev/ttyUSB0 -b 115200"
    echo "2. Copy and paste these commands:"
    echo ""
    cat xbee_coordinator_config.txt
    echo ""
    echo "3. Exit minicom: Ctrl+A then X"
    echo ""
    read -p "Press Enter when configuration is complete..."
    
    # Verify configuration
    echo "🔍 Verifying coordinator configuration..."
    verify_xbee_config "coordinator"
}

# Configure XBee as router
configure_router() {
    read -p "Enter node number for this router (2, 3, 4, etc.): " node_num
    
    echo "🎯 Configuring XBee as Router (Node $node_num)..."
    
    cat > xbee_router_config.txt << EOF
+++
ATID 1234
ATCE 0
ATMY $node_num
ATAP 1
ATBD 7
ATCH 0C
ATWR
ATCN
EOF
    
    echo "Configuration commands saved to xbee_router_config.txt"
    echo ""
    echo "Manual configuration steps:"
    echo "1. Run: sudo minicom -D /dev/ttyUSB0 -b 115200"
    echo "2. Copy and paste these commands:"
    echo ""
    cat xbee_router_config.txt
    echo ""
    echo "3. Exit minicom: Ctrl+A then X"
    echo ""
    read -p "Press Enter when configuration is complete..."
    
    # Verify configuration
    echo "🔍 Verifying router configuration..."
    verify_xbee_config "router" "$node_num"
}

# Verify XBee configuration
verify_xbee_config() {
    local node_type="$1"
    local node_num="$2"
    
    echo "Creating verification script..."
    cat > verify_xbee.py << 'EOF'
#!/usr/bin/env python3
import serial
import time
import sys

def send_at_command(ser, command):
    ser.write((command + '\r').encode())
    time.sleep(0.5)
    response = ser.read_all().decode().strip()
    return response

try:
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    time.sleep(2)
    
    print("📡 Entering command mode...")
    ser.write(b'+++')
    time.sleep(1.5)
    response = ser.read_all().decode().strip()
    
    if 'OK' not in response:
        print("❌ Failed to enter command mode")
        sys.exit(1)
    
    print("✅ Command mode entered")
    
    # Check configuration
    commands = ['ATID', 'ATCE', 'ATMY', 'ATAP', 'ATBD', 'ATCH']
    config = {}
    
    for cmd in commands:
        response = send_at_command(ser, cmd)
        config[cmd] = response.replace(cmd, '').strip()
        print(f"{cmd}: {config[cmd]}")
    
    # Exit command mode
    send_at_command(ser, 'ATCN')
    
    # Verify expected values
    expected = {
        'ATID': '1234',
        'ATAP': '1',
        'ATBD': '7',
        'ATCH': 'C'
    }
    
    all_good = True
    for cmd, expected_val in expected.items():
        if config[cmd] != expected_val:
            print(f"❌ {cmd} mismatch: expected {expected_val}, got {config[cmd]}")
            all_good = False
    
    if all_good:
        print("✅ XBee configuration verified successfully!")
    else:
        print("❌ Configuration verification failed")
        sys.exit(1)
        
    ser.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF
    
    if command -v python3 > /dev/null; then
        python3 verify_xbee.py
        rm verify_xbee.py
    else
        echo "⚠️  Python3 not available for automatic verification"
        echo "Please manually verify configuration using minicom"
    fi
}

# View current XBee settings
view_xbee_settings() {
    echo "🔍 Viewing current XBee settings..."
    
    cat > check_xbee_settings.txt << 'EOF'
+++
ATID
ATCE
ATMY
ATAP
ATBD
ATCH
ATCN
EOF
    
    echo "To view current settings:"
    echo "1. Run: sudo minicom -D /dev/ttyUSB0 -b 115200"
    echo "2. Copy and paste these commands:"
    echo ""
    cat check_xbee_settings.txt
    echo ""
    echo "3. Note down the values"
    echo "4. Exit minicom: Ctrl+A then X"
    echo ""
    echo "Expected values:"
    echo "  ATID: 1234 (PAN ID - same for all nodes)"
    echo "  ATCE: 1 (coordinator) or 0 (router)"
    echo "  ATMY: 0 (coordinator) or 1,2,3... (router)"
    echo "  ATAP: 1 (API mode)"
    echo "  ATBD: 7 (115200 baud)"
    echo "  ATCH: C (channel 12)"
}

# Test mesh network sync
test_mesh_sync() {
    echo "🌐 Testing mesh network synchronization..."
    
    if ! systemctl is-active --quiet lumanet; then
        echo -e "${RED}❌ LumaNet service not running${NC}"
        echo "Start with: sudo systemctl start lumanet"
        return 1
    fi
    
    echo "Creating test subject to verify sync..."
    
    # Create test subject
    TIMESTAMP=$(date +%s)
    SUBJECT_NAME="Mesh Test $TIMESTAMP"
    
    RESPONSE=$(curl -s -X POST http://localhost:3000/api/subjects \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$SUBJECT_NAME\",\"description\":\"Testing mesh sync at $(date)\"}")
    
    if echo "$RESPONSE" | grep -q "id"; then
        echo -e "${GREEN}✅ Test subject created successfully${NC}"
        echo "Subject: $SUBJECT_NAME"
        
        # Check sync events
        echo ""
        echo "📊 Recent sync events:"
        psql -U lumanet_user -d lumanet -c "SELECT event_type, source_node, timestamp FROM sync_events ORDER BY timestamp DESC LIMIT 5;" 2>/dev/null || echo "Could not query sync events"
        
        echo ""
        echo "⏰ Wait 30 seconds, then check other nodes for this subject:"
        echo "   curl http://othernode.local:3000/api/subjects | grep \"$SUBJECT_NAME\""
        
    else
        echo -e "${RED}❌ Failed to create test subject${NC}"
        echo "Response: $RESPONSE"
        return 1
    fi
}

# Comprehensive XBee diagnostics
run_diagnostics() {
    echo "🔬 Running comprehensive XBee diagnostics..."
    echo ""
    
    # Hardware check
    echo "1. Hardware Detection:"
    if check_xbee_hardware; then
        echo -e "${GREEN}   ✅ Hardware OK${NC}"
    else
        echo -e "${RED}   ❌ Hardware issues detected${NC}"
        return 1
    fi
    
    echo ""
    echo "2. Service Status:"
    if systemctl is-active --quiet lumanet; then
        echo -e "${GREEN}   ✅ LumaNet service running${NC}"
    else
        echo -e "${YELLOW}   ⚠️  LumaNet service not running${NC}"
    fi
    
    echo ""
    echo "3. XBee Logs:"
    echo "   Recent XBee-related log entries:"
    sudo journalctl -u lumanet -n 10 --no-pager | grep -i xbee || echo "   No recent XBee logs found"
    
    echo ""
    echo "4. Network Connectivity:"
    if ping -c 1 8.8.8.8 > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Internet connectivity OK${NC}"
    else
        echo -e "${YELLOW}   ⚠️  No internet (normal for mesh-only operation)${NC}"
    fi
    
    echo ""
    echo "5. Database Sync Events:"
    EVENT_COUNT=$(psql -U lumanet_user -d lumanet -c "SELECT COUNT(*) FROM sync_events;" -t 2>/dev/null | tr -d ' ')
    if [ "$EVENT_COUNT" -gt 0 ]; then
        echo -e "${GREEN}   ✅ $EVENT_COUNT sync events in database${NC}"
    else
        echo -e "${YELLOW}   ⚠️  No sync events found${NC}"
    fi
    
    echo ""
    echo "📋 Diagnostic Summary Complete"
}

# Main menu
show_menu() {
    echo ""
    echo "🔧 XBee Configuration Menu"
    echo "=========================="
    echo "1) Check XBee Hardware"
    echo "2) Configure as Coordinator (Node 1)"
    echo "3) Configure as Router (Node 2+)"
    echo "4) View Current Settings"
    echo "5) Test Communication"
    echo "6) Test Mesh Sync"
    echo "7) Run Full Diagnostics"
    echo "8) Exit"
    echo ""
}

# Main script
if ! check_xbee_hardware; then
    echo ""
    echo -e "${YELLOW}⚠️  XBee hardware issues detected. Please fix before continuing.${NC}"
    echo ""
    echo "Common solutions:"
    echo "1. Check physical connections"
    echo "2. Run: sudo usermod -a -G dialout $USER"
    echo "3. Logout and login again"
    echo "4. Try a different USB port"
    exit 1
fi

while true; do
    show_menu
    read -p "Enter choice (1-8): " choice
    
    case $choice in
        1)
            check_xbee_hardware
            ;;
        2)
            configure_coordinator
            ;;
        3)
            configure_router
            ;;
        4)
            view_xbee_settings
            ;;
        5)
            test_xbee_communication
            ;;
        6)
            test_mesh_sync
            ;;
        7)
            run_diagnostics
            ;;
        8)
            echo "Exiting XBee configuration tool..."
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please enter 1-8.${NC}"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
