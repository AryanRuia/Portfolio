# 🚀 LumaNet - Mesh Learning Management System

**Beautiful responsive UI with real PostgreSQL backend and XBee mesh networking**

## ⚡ Quick Start (3 Commands Only!)

```bash
git clone https://github.com/Nihal-Gorthi/LumaNodeV2.git
cd LumaNodeV2
./master-install.sh
```

**That's it! The installer does everything automatically.**

## 🎯 After Installation

### Start LumaNet:
```bash
./start.sh
```

### Stop LumaNet:
```bash
./stop.sh
```

### Test System:
```bash
./test-system.sh
```

### Configure XBee:
```bash
./xbee-setup.sh
```

## 🌐 Access Your System

- **Local**: http://localhost:3000
- **Network**: http://lumanode1.local:3000
- **Login**: admin / admin123 or student / student123

## 📋 What You Get

- ✅ **Beautiful responsive UI** with blue theme and dark mode
- ✅ **Real PostgreSQL database** (no mock data)
- ✅ **XBee mesh networking** for offline operation
- ✅ **File upload/download** with cross-node sync
- ✅ **User management** (admin/student accounts)
- ✅ **Course creation** with real-time sync
- ✅ **Auto-start service** (runs on boot)
- ✅ **Mobile responsive** design

## 🔧 Useful Commands

```bash
# Check status
sudo systemctl status lumanet

# View logs
sudo journalctl -u lumanet -f

# Restart service
sudo systemctl restart lumanet

# Quick status check
./check-status.sh
```

## 📖 Full Documentation

- **MASTER_INSTALLATION_GUIDE.md** - Complete step-by-step guide
- **FINAL_INSTALLATION_GUIDE.md** - Alternative detailed guide

## 🎉 Features

### Beautiful UI
- Responsive design works on desktop and mobile
- Dark mode toggle
- Hover-expandable sidebar
- Blue color scheme (no purple gradients)
- Montserrat and Bricolage Grotesque fonts

### Real Backend
- PostgreSQL database with proper schemas
- JWT authentication
- File upload with multer
- RESTful API endpoints
- Event-driven sync system

### Mesh Networking
- XBee 3 Pro support
- Automatic data synchronization
- Offline-first operation
- Multi-node mesh topology
- Event propagation system

**Your mesh-networked LMS is ready! 🚀**
