import pool from '../db/pool';
import { SyncEvent } from './eventLog';

export async function applyEvent(event: SyncEvent): Promise<void> {
  switch (event.event_type) {
    case 'USER_CREATED':
      await applyUserCreated(event.payload);
      break;
    case 'SUBJECT_CREATED':
      await applySubjectCreated(event.payload);
      break;
    case 'MATERIAL_UPLOADED':
      await applyMaterialUploaded(event.payload);
      break;
    case 'PROGRESS_UPDATED':
      await applyProgressUpdated(event.payload);
      break;
    default:
      console.warn(`Unknown event type: ${event.event_type}`);
  }
}

async function applyUserCreated(payload: any): Promise<void> {
  const query = `
    INSERT INTO users (id, username, password_hash, role, full_name, school_id, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    ON CONFLICT (id) DO NOTHING
  `;

  await pool.query(query, [
    payload.id,
    payload.username,
    payload.password_hash,
    payload.role,
    payload.full_name,
    payload.school_id,
    payload.created_at,
    payload.updated_at
  ]);
}

async function applySubjectCreated(payload: any): Promise<void> {
  const query = `
    INSERT INTO subjects (id, name, description, teacher_id, school_id, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6, $7)
    ON CONFLICT (id) DO NOTHING
  `;

  await pool.query(query, [
    payload.id,
    payload.name,
    payload.description,
    payload.teacher_id,
    payload.school_id,
    payload.created_at,
    payload.updated_at
  ]);
}

async function applyMaterialUploaded(payload: any): Promise<void> {
  const query = `
    INSERT INTO materials (id, subject_id, title, filename, file_size, mime_type, storage_node, created_at, uploaded_by)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    ON CONFLICT (id) DO NOTHING
  `;

  await pool.query(query, [
    payload.id,
    payload.subject_id,
    payload.title,
    payload.filename,
    payload.file_size,
    payload.mime_type,
    payload.storage_node,
    payload.created_at,
    payload.uploaded_by
  ]);
}

async function applyProgressUpdated(payload: any): Promise<void> {
  const query = `
    INSERT INTO progress (user_id, material_id, completed, completion_date, updated_at)
    VALUES ($1, $2, $3, $4, $5)
    ON CONFLICT (user_id, material_id) DO UPDATE
    SET completed = EXCLUDED.completed,
        completion_date = EXCLUDED.completion_date,
        updated_at = EXCLUDED.updated_at
  `;

  await pool.query(query, [
    payload.user_id,
    payload.material_id,
    payload.completed,
    payload.completion_date,
    payload.updated_at
  ]);
}
