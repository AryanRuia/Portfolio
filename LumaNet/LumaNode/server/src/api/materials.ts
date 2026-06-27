import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { v4 as uuidv4 } from 'uuid';
import pool from '../db/pool';
import { createEvent } from '../sync/eventLog';
import { broadcastEvent } from '../sync/syncService';

const router = express.Router();

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, '../storage/uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadsDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${Date.now()}-${Math.round(Math.random() * 1E9)}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const upload = multer({ 
  storage,
  limits: { fileSize: parseInt(process.env.MAX_FILE_SIZE || '52428800') }
});

// Get materials for a subject
router.get('/', async (req, res) => {
  try {
    const { subject } = req.query;
    const result = await pool.query(`
      SELECT m.*, u.full_name as uploaded_by_name 
      FROM materials m 
      LEFT JOIN users u ON m.uploaded_by = u.id 
      WHERE m.subject_id = $1 
      ORDER BY m.created_at DESC
    `, [subject]);
    res.json(result.rows);
  } catch (error) {
    console.error('Get materials error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Upload material
router.post('/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const metadata = JSON.parse(req.body.metadata);
    const id = uuidv4();
    const now = Date.now();

    await pool.query(`
      INSERT INTO materials (id, subject_id, title, filename, file_size, mime_type, storage_node, created_at, uploaded_by)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    `, [
      id,
      metadata.subject_id,
      metadata.title,
      req.file.filename,
      req.file.size,
      req.file.mimetype,
      process.env.NODE_ID,
      now,
      metadata.uploaded_by
    ]);

    // Create sync event
    const event = await createEvent('MATERIAL_UPLOADED', {
      id,
      subject_id: metadata.subject_id,
      title: metadata.title,
      filename: req.file.filename,
      file_size: req.file.size,
      mime_type: req.file.mimetype,
      storage_node: process.env.NODE_ID,
      created_at: now,
      uploaded_by: metadata.uploaded_by
    });
    
    // Broadcast to mesh
    await broadcastEvent(event);

    res.status(201).json({ 
      id, 
      title: metadata.title, 
      filename: req.file.filename,
      file_size: req.file.size,
      created_at: now 
    });
  } catch (error) {
    console.error('Upload material error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete material
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Get material info before deletion
    const materialResult = await pool.query('SELECT * FROM materials WHERE id = $1', [id]);
    if (materialResult.rows.length === 0) {
      return res.status(404).json({ error: 'Material not found' });
    }

    const material = materialResult.rows[0];

    // Delete from database
    await pool.query('DELETE FROM materials WHERE id = $1', [id]);

    // Create sync event
    const event = await createEvent('MATERIAL_DELETED', { id });
    
    // Broadcast to mesh
    await broadcastEvent(event);

    res.json({ message: 'Material deleted successfully' });
  } catch (error) {
    console.error('Delete material error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
