#!/bin/bash

echo "🚀 Starting LumaNet System"
echo "=========================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -f "server/package.json" ] || [ ! -f "client/package.json" ]; then
    echo -e "${RED}❌ Error: Run this script from the LumaNodeV2 directory${NC}"
    echo "Usage: cd LumaNodeV2 && ./start.sh"
    exit 1
fi

# Check if system is installed
if [ ! -f "server/dist/index.js" ]; then
    echo -e "${RED}❌ System not built. Run ./master-install.sh first${NC}"
    exit 1
fi

# Start LumaNet service
echo "🔄 Starting LumaNet service..."
sudo systemctl start lumanet

# Wait for service to start
sleep 3

# Check if service is running
if systemctl is-active --quiet lumanet; then
    echo -e "${GREEN}✅ LumaNet service started successfully${NC}"
    
    # Get system info
    NODE_ID=$(grep "NODE_ID=" server/.env | cut -d'=' -f2)
    HOSTNAME=$(hostname)
    
    echo ""
    echo "🌐 System Information:"
    echo "  Node ID: $NODE_ID"
    echo "  Hostname: $HOSTNAME"
    echo ""
    echo "🔗 Access URLs:"
    echo "  Local: http://localhost:3000"
    echo "  Network: http://$HOSTNAME.local:3000"
    echo "  IP: http://$(hostname -I | awk '{print $1}'):3000"
    echo ""
    echo "🔑 Login Credentials:"
    echo "  Admin: admin / admin123"
    echo "  Student: student / student123"
    echo ""
    echo "📊 Service Status:"
    sudo systemctl status lumanet --no-pager -l
    echo ""
    echo "📝 To view logs: sudo journalctl -u lumanet -f"
    echo "🛑 To stop: sudo systemctl stop lumanet"
    
else
    echo -e "${RED}❌ Failed to start LumaNet service${NC}"
    echo ""
    echo "🔍 Checking logs..."
    sudo journalctl -u lumanet -n 10 --no-pager
    echo ""
    echo "🔧 Try these fixes:"
    echo "  1. sudo systemctl restart lumanet"
    echo "  2. ./test-system.sh"
    echo "  3. Check logs: sudo journalctl -u lumanet -f"
    exit 1
fi
