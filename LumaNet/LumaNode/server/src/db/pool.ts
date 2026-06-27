import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'lumanet',
  user: process.env.DB_USER || 'lumanet_user',
  password: String(process.env.DB_PASSWORD || 'lumanet123'),
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

pool.on('error', (err: any) => {
  console.error('Unexpected database error:', err);
  process.exit(-1);
});

export default pool;
