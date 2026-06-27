import express from 'express';
import bcrypt from 'bcrypt';
import { v4 as uuidv4 } from 'uuid';
import pool from '../db/pool';
import { createEvent } from '../sync/eventLog';
import { broadcastEvent } from '../sync/syncService';

const router = express.Router();

// Get all users
router.get('/', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT id, username, role, full_name, created_at, is_active 
      FROM users 
      WHERE is_active = true 
      ORDER BY created_at DESC
    `);
    res.json(result.rows);
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create user
router.post('/', async (req, res) => {
  try {
    const { username, password, role, full_name, school_id } = req.body;
    const id = uuidv4();
    const now = Date.now();
    const password_hash = await bcrypt.hash(password, 10);

    await pool.query(`
      INSERT INTO users (id, username, password_hash, role, full_name, school_id, created_at, updated_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    `, [id, username, password_hash, role, full_name, school_id, now, now]);

    // Create sync event
    const event = await createEvent('USER_CREATED', {
      id, username, password_hash, role, full_name, school_id, created_at: now, updated_at: now
    });
    
    // Broadcast to mesh
    await broadcastEvent(event);

    res.status(201).json({ 
      id, username, role, full_name, created_at: now 
    });
  } catch (error) {
    console.error('Create user error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete user
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Don't allow deleting admin users
    const userCheck = await pool.query('SELECT role FROM users WHERE id = $1', [id]);
    if (userCheck.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }
    
    if (userCheck.rows[0].role === 'admin') {
      return res.status(403).json({ error: 'Cannot delete admin users' });
    }

    await pool.query('DELETE FROM users WHERE id = $1', [id]);

    // Create sync event
    const event = await createEvent('USER_DELETED', { id });
    
    // Broadcast to mesh
    await broadcastEvent(event);

    res.json({ message: 'User deleted successfully' });
  } catch (error) {
    console.error('Create user error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
