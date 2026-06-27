#!/bin/bash

# Database initialization script for LumaNet
echo "🚀 Initializing LumaNet Database..."

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL is not running. Starting..."
    sudo systemctl start postgresql
fi

# Create database and user using proper PostgreSQL syntax
echo "📊 Creating database and user..."
sudo -u postgres psql << 'EOF'
SELECT 'CREATE DATABASE lumanet' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lumanet')\gexec
DO
$do$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'lumanet_user') THEN
      CREATE USER lumanet_user WITH PASSWORD 'lumanet123';
   END IF;
END
$do$;
GRANT ALL PRIVILEGES ON DATABASE lumanet TO lumanet_user;
ALTER USER lumanet_user CREATEDB;
\q
EOF

# Run schema
echo "🏗️  Creating tables..."
sudo -u postgres psql -d lumanet -f server/src/db/schema.sql

# Grant permissions on all tables and sequences
echo "🔐 Setting up database permissions..."
sudo -u postgres psql -d lumanet << 'EOF'
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lumanet_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO lumanet_user;
GRANT USAGE ON SCHEMA public TO lumanet_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO lumanet_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO lumanet_user;
\q
EOF

# Create ONLY admin user - students will be created by admin
echo "👤 Creating admin user only..."
sudo -u postgres psql -d lumanet << 'EOF'
INSERT INTO users (id, username, password_hash, role, full_name, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'admin',
  '$2b$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
  'admin',
  'System Administrator',
  extract(epoch from now()) * 1000,
  extract(epoch from now()) * 1000
) ON CONFLICT (username) DO NOTHING;
\q
EOF

echo "✅ Database initialization complete!"
echo "🔑 Admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 Note: Student accounts must be created by admin through the web interface"
