import express from 'express';
import { v4 as uuidv4 } from 'uuid';
import pool from '../db/pool';
import { createEvent } from '../sync/eventLog';
import { broadcastEvent } from '../sync/syncService';

const router = express.Router();

// Get all subjects
router.get('/', async (req, res) => {
  try {
    const result = await pool.query(`
      SELECT s.*, u.full_name as teacher_name 
      FROM subjects s 
      LEFT JOIN users u ON s.teacher_id = u.id 
      WHERE s.is_active = true 
      ORDER BY s.created_at DESC
    `);
    res.json(result.rows);
  } catch (error) {
    console.error('Get subjects error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create subject
router.post('/', async (req, res) => {
  try {
    const { name, description, teacher_id, school_id } = req.body;
    const id = uuidv4();
    const now = Date.now();

    await pool.query(`
      INSERT INTO subjects (id, name, description, teacher_id, school_id, created_at, updated_at)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
    `, [id, name, description, teacher_id, school_id, now, now]);

    // Create sync event
    const event = await createEvent('SUBJECT_CREATED', {
      id, name, description, teacher_id, school_id, created_at: now, updated_at: now
    });
    
    // Broadcast to mesh
    await broadcastEvent(event);

    res.status(201).json({ id, name, description, teacher_id, school_id, created_at: now, updated_at: now });
  } catch (error) {
    console.error('Create subject error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete subject
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Delete associated materials first
    await pool.query('DELETE FROM materials WHERE subject_id = $1', [id]);
    
    // Delete the subject
    await pool.query('DELETE FROM subjects WHERE id = $1', [id]);

    // Create sync event
    const event = await createEvent('SUBJECT_DELETED', { id });
    
    // Broadcast to mesh
    await broadcastEvent(event);

    res.json({ message: 'Subject deleted successfully' });
  } catch (error) {
    console.error('Delete subject error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
