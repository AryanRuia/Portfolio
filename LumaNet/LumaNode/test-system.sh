#!/bin/bash

echo "🧪 LumaNet Complete System Test Suite"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# Function to run test with output
run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}Testing: $test_name${NC}"
    
    local output
    output=$(eval "$test_command" 2>&1)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        echo "Output: $output"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        echo "Error: $output"
        ((TESTS_FAILED++))
    fi
    echo ""
}

echo "🔍 Starting System Tests..."
echo ""

# Test 1: Node.js Installation
run_test "Node.js Installation" "node --version | grep -q 'v20'"

# Test 2: PostgreSQL Service
run_test "PostgreSQL Service" "systemctl is-active --quiet postgresql"

# Test 3: Database Connection
run_test_with_output "Database Connection" "sudo -u postgres psql -d lumanet -c 'SELECT 1;' -t"

# Test 4: Database Tables
run_test_with_output "Database Tables" "sudo -u postgres psql -d lumanet -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';\" -t"

# Test 5: Default Users
run_test_with_output "Default Admin User" "sudo -u postgres psql -d lumanet -c 'SELECT COUNT(*) FROM users;' -t"

# Test 6: LumaNet Service
run_test "LumaNet Service" "systemctl is-active --quiet lumanet"

# Test 7: HTTP Server Response
run_test_with_output "HTTP Server" "curl -s http://localhost:3000/health | grep -q 'healthy'"

# Test 8: Avahi Service
run_test "Avahi Service" "systemctl is-active --quiet avahi-daemon"

# Test 9: Network Resolution
run_test_with_output "Network Resolution" "avahi-resolve -n $(hostname).local"

# Test 10: XBee Hardware Detection
echo -e "${BLUE}Testing: XBee Hardware Detection${NC}"
if lsusb | grep -i ftdi > /dev/null; then
    echo -e "${GREEN}✅ PASS: XBee Hardware Detection${NC}"
    echo "FTDI device found"
    ((TESTS_PASSED++))
    
    # Test 11: XBee Serial Device
    if [ -e /dev/ttyUSB0 ]; then
        echo -e "${GREEN}✅ PASS: XBee Serial Device${NC}"
        echo "Device: /dev/ttyUSB0"
        ((TESTS_PASSED++))
        
        # Test 12: XBee Permissions
        if [ -r /dev/ttyUSB0 ] && [ -w /dev/ttyUSB0 ]; then
            echo -e "${GREEN}✅ PASS: XBee Permissions${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${YELLOW}⚠️  WARNING: XBee Permissions${NC}"
            echo "Run: sudo usermod -a -G dialout $USER"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${RED}❌ FAIL: XBee Serial Device${NC}"
        echo "/dev/ttyUSB0 not found"
        ((TESTS_FAILED++))
        ((TESTS_FAILED++)) # Skip permissions test too
    fi
else
    echo -e "${YELLOW}⚠️  WARNING: XBee Hardware Detection${NC}"
    echo "No FTDI device found - XBee may not be connected"
    ((TESTS_FAILED++))
    ((TESTS_FAILED++)) # Skip serial device test
    ((TESTS_FAILED++)) # Skip permissions test
fi
echo ""

# Test 13: Upload Directory
run_test "Upload Directory" "[ -d 'server/src/storage/uploads' ] && [ -w 'server/src/storage/uploads' ]"

# Test 14: API Endpoints
echo -e "${BLUE}Testing: API Endpoints${NC}"
api_tests=0
api_passed=0

# Health endpoint
if curl -s http://localhost:3000/health | grep -q "healthy"; then
    echo "✅ Health endpoint working"
    ((api_passed++))
else
    echo "❌ Health endpoint failed"
fi
((api_tests++))

# Subjects endpoint
if curl -s http://localhost:3000/api/subjects | grep -q "\[\]"; then
    echo "✅ Subjects endpoint working"
    ((api_passed++))
else
    echo "❌ Subjects endpoint failed"
fi
((api_tests++))

# Users endpoint
if curl -s http://localhost:3000/api/users | grep -q "admin"; then
    echo "✅ Users endpoint working"
    ((api_passed++))
else
    echo "❌ Users endpoint failed"
fi
((api_tests++))

if [ $api_passed -eq $api_tests ]; then
    echo -e "${GREEN}✅ PASS: API Endpoints${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL: API Endpoints${NC}"
    echo "Passed: $api_passed/$api_tests"
    ((TESTS_FAILED++))
fi
echo ""

# Test 15: Authentication
echo -e "${BLUE}Testing: Authentication${NC}"
auth_response=$(curl -s -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

if echo "$auth_response" | grep -q "token"; then
    echo -e "${GREEN}✅ PASS: Authentication${NC}"
    echo "Admin login successful"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL: Authentication${NC}"
    echo "Response: $auth_response"
    ((TESTS_FAILED++))
fi
echo ""

# Test 16: File System Permissions
echo -e "${BLUE}Testing: File System Permissions${NC}"
perm_tests=0
perm_passed=0

# Server directory
if [ -r "server" ] && [ -x "server" ]; then
    echo "✅ Server directory accessible"
    ((perm_passed++))
else
    echo "❌ Server directory not accessible"
fi
((perm_tests++))

# Client build directory
if [ -r "client/dist" ] && [ -x "client/dist" ]; then
    echo "✅ Client build directory accessible"
    ((perm_passed++))
else
    echo "❌ Client build directory not accessible"
fi
((perm_tests++))

# Database files
if sudo -u postgres test -r /var/lib/postgresql; then
    echo "✅ Database files accessible"
    ((perm_passed++))
else
    echo "❌ Database files not accessible"
fi
((perm_tests++))

if [ $perm_passed -eq $perm_tests ]; then
    echo -e "${GREEN}✅ PASS: File System Permissions${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ FAIL: File System Permissions${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# Test 17: System Resources
echo -e "${BLUE}Testing: System Resources${NC}"
resource_tests=0
resource_passed=0

# Memory usage
memory_usage=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
if (( $(echo "$memory_usage < 80" | bc -l) )); then
    echo "✅ Memory usage OK (${memory_usage}%)"
    ((resource_passed++))
else
    echo "⚠️  High memory usage (${memory_usage}%)"
fi
((resource_tests++))

# Disk space
disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo "✅ Disk space OK (${disk_usage}% used)"
    ((resource_passed++))
else
    echo "⚠️  Low disk space (${disk_usage}% used)"
fi
((resource_tests++))

# CPU load
cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
if (( $(echo "$cpu_load < 2.0" | bc -l) )); then
    echo "✅ CPU load OK ($cpu_load)"
    ((resource_passed++))
else
    echo "⚠️  High CPU load ($cpu_load)"
fi
((resource_tests++))

if [ $resource_passed -eq $resource_tests ]; then
    echo -e "${GREEN}✅ PASS: System Resources${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠️  WARNING: System Resources${NC}"
    ((TESTS_PASSED++)) # Don't fail for resource warnings
fi
echo ""

# Summary
echo "🏁 Test Results Summary"
echo "======================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $(($TESTS_PASSED + $TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! LumaNet is ready to use!${NC}"
    echo ""
    echo "🌐 Access your system:"
    echo "  Local: http://localhost:3000"
    echo "  Network: http://$(hostname).local:3000"
    echo ""
    echo "🔑 Default login:"
    echo "  Admin: admin / admin123"
    echo "  Student: student / student123"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please check the issues above.${NC}"
    echo ""
    echo "🔧 Common fixes:"
    echo "  - Restart services: sudo systemctl restart lumanet postgresql avahi-daemon"
    echo "  - Check logs: sudo journalctl -u lumanet -f"
    echo "  - Verify XBee connection: lsusb | grep -i ftdi"
    echo "  - Fix permissions: sudo usermod -a -G dialout $USER"
    exit 1
fi
