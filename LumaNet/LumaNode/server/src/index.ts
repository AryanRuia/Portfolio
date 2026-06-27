import express from 'express';
import cors from 'cors';
import path from 'path';
import dotenv from 'dotenv';
import pool from './db/pool';
import { startSyncService } from './sync/syncService';
import subjectsRouter from './api/subjects';
import materialsRouter from './api/materials';
import usersRouter from './api/users';
import authRouter from './api/auth';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Static file serving for uploads
app.use('/uploads', express.static(path.join(__dirname, 'storage/uploads')));

// Serve React frontend
app.use(express.static(path.join(__dirname, '../../client/dist')));

// API routes
app.use('/api/auth', authRouter);
app.use('/api/subjects', subjectsRouter);
app.use('/api/materials', materialsRouter);
app.use('/api/users', usersRouter);

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    nodeId: process.env.NODE_ID,
    timestamp: Date.now()
  });
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../../client/dist/index.html'));
});

// Start server
async function start() {
  try {
    // Test database connection
    await pool.query('SELECT NOW()');
    console.log('Database connected');

    // Start sync service
    await startSyncService();
    console.log('Sync service started');

    // Start HTTP server
    app.listen(PORT, () => {
      console.log(`LumaNet server running on port ${PORT}`);
      console.log(`Node ID: ${process.env.NODE_ID}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

start();
