#!/bin/bash

echo "🚀 LumaNet Automated Installation Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Don't run this script as root (sudo)${NC}"
    echo "Run as regular user: ./quick-install.sh"
    exit 1
fi

# Get node configuration
echo -e "${BLUE}📝 Node Configuration${NC}"
read -p "Enter node number (1, 2, 3, etc.): " NODE_NUM
read -p "Enter node name (e.g., Main Campus, Library, Lab): " NODE_NAME

NODE_ID="lumanode$NODE_NUM"
HOSTNAME="lumanode$NODE_NUM"

echo ""
echo "Configuration:"
echo "  Node ID: $NODE_ID"
echo "  Hostname: $HOSTNAME"
echo "  Name: $NODE_NAME"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo -e "${BLUE}🔄 Step 1: System Update${NC}"
sudo apt update && sudo apt upgrade -y

echo ""
echo -e "${BLUE}📦 Step 2: Install Dependencies${NC}"
sudo apt install -y \
  git \
  curl \
  build-essential \
  postgresql \
  postgresql-contrib \
  avahi-daemon \
  avahi-utils \
  minicom \
  screen \
  htop \
  nano \
  bc

echo ""
echo -e "${BLUE}🟢 Step 3: Install Node.js${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt install -y nodejs

echo ""
echo -e "${BLUE}🔧 Step 4: Configure Services${NC}"
sudo systemctl enable postgresql avahi-daemon
sudo systemctl start postgresql avahi-daemon

echo ""
echo -e "${BLUE}🌐 Step 5: Configure Network${NC}"
sudo hostnamectl set-hostname $HOSTNAME

# Update /etc/hosts
sudo sed -i "/127.0.1.1/d" /etc/hosts
echo "127.0.1.1    $HOSTNAME" | sudo tee -a /etc/hosts

# Configure Avahi
sudo tee /etc/avahi/avahi-daemon.conf > /dev/null << EOF
[server]
host-name=$HOSTNAME
domain-name=local
use-ipv4=yes
use-ipv6=no

[publish]
publish-addresses=yes
publish-workstation=yes
EOF

sudo systemctl restart avahi-daemon

echo ""
echo -e "${BLUE}📥 Step 6: Clone Repository${NC}"
if [ ! -d "LumaNodeV2" ]; then
    git clone https://github.com/Nihal-Gorthi/LumaNodeV2.git
fi
cd LumaNodeV2

echo ""
echo -e "${BLUE}📦 Step 7: Install Dependencies${NC}"
echo "Installing server dependencies..."
cd server
npm install
echo "Installing client dependencies..."
cd ../client
npm install
echo "Building client..."
npm run build
cd ..

echo ""
echo -e "${BLUE}🗄️ Step 8: Setup Database${NC}"
chmod +x init-db.sh
./init-db.sh

echo ""
echo -e "${BLUE}⚙️ Step 9: Configure LumaNet${NC}"
# Create environment file
cat > server/.env << EOF
# Node configuration
NODE_ENV=production
PORT=3000

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lumanet
DB_USER=lumanet_user
DB_PASSWORD=lumanet123

# Authentication
JWT_SECRET=lumanet-super-secret-key-$(date +%s)-mesh-network-jwt
ADMIN_PASSWORD=admin123

# Node identification
NODE_ID=$NODE_ID
NODE_NAME=$NODE_NAME

# XBee serial configuration
XBEE_PORT=/dev/ttyUSB0
XBEE_BAUD=115200

# File storage
UPLOAD_DIR=/home/$USER/LumaNodeV2/server/src/storage/uploads
MAX_FILE_SIZE=52428800
EOF

# Create upload directory
mkdir -p server/src/storage/uploads

echo ""
echo -e "${BLUE}🔨 Step 10: Build Server${NC}"
cd server
npm run build
cd ..

echo ""
echo -e "${BLUE}🚀 Step 11: Setup System Service${NC}"
# Update service file
sed -i "s|User=pi|User=$USER|g" lumanet.service
sed -i "s|/home/pi/|/home/$USER/|g" lumanet.service

sudo cp lumanet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lumanet

echo ""
echo -e "${BLUE}👥 Step 12: Fix Permissions${NC}"
sudo usermod -a -G dialout $USER

echo ""
echo -e "${BLUE}🚀 Step 13: Start LumaNet${NC}"
sudo systemctl start lumanet

echo ""
echo -e "${BLUE}🧪 Step 14: Run Tests${NC}"
chmod +x test-system.sh
./test-system.sh

echo ""
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo ""
echo "📋 System Information:"
echo "  Node ID: $NODE_ID"
echo "  Hostname: $HOSTNAME"
echo "  Name: $NODE_NAME"
echo ""
echo "🌐 Access URLs:"
echo "  Local: http://localhost:3000"
echo "  Network: http://$HOSTNAME.local:3000"
echo ""
echo "🔑 Default Login:"
echo "  Admin: admin / admin123"
echo "  Student: student / student123"
echo ""
echo "🔧 Useful Commands:"
echo "  Check status: sudo systemctl status lumanet"
echo "  View logs: sudo journalctl -u lumanet -f"
echo "  Test system: ./test-system.sh"
echo "  Configure XBee: ./xbee-setup.sh"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Logout and login again to apply group permissions${NC}"
echo -e "${YELLOW}   Then connect XBee hardware and run: ./xbee-setup.sh${NC}"
echo ""
echo -e "${GREEN}Your LumaNet node is ready! 🚀${NC}"
