#!/bin/bash

echo "🛑 Stopping LumaNet System"
echo "=========================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Stop LumaNet service
echo "🔄 Stopping LumaNet service..."
sudo systemctl stop lumanet

# Wait for service to stop
sleep 2

# Check if service is stopped
if ! systemctl is-active --quiet lumanet; then
    echo -e "${GREEN}✅ LumaNet service stopped successfully${NC}"
    echo ""
    echo "📊 Service Status:"
    sudo systemctl status lumanet --no-pager -l
else
    echo -e "${RED}❌ Failed to stop LumaNet service${NC}"
    echo ""
    echo "🔧 Force stop:"
    echo "  sudo systemctl kill lumanet"
    exit 1
fi

echo ""
echo "🔄 To start again: ./start.sh"
