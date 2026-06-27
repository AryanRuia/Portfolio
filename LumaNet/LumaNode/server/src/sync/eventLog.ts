import { v4 as uuidv4 } from 'uuid';
import pool from '../db/pool';

export interface SyncEvent {
  id: string;
  event_type: string;
  payload: any;
  timestamp: number;
  source_node: string;
}

export async function createEvent(
  eventType: string,
  payload: any
): Promise<SyncEvent> {
  const event: SyncEvent = {
    id: uuidv4(),
    event_type: eventType,
    payload,
    timestamp: Date.now(),
    source_node: process.env.NODE_ID || 'unknown'
  };

  await saveEvent(event);
  return event;
}

export async function saveEvent(event: SyncEvent): Promise<void> {
  const query = `
    INSERT INTO sync_events (id, event_type, payload, timestamp, source_node, created_at)
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (id) DO NOTHING
  `;

  await pool.query(query, [
    event.id,
    event.event_type,
    JSON.stringify(event.payload),
    event.timestamp,
    event.source_node,
    Date.now()
  ]);
}

export async function eventExists(eventId: string): Promise<boolean> {
  const result = await pool.query(
    'SELECT 1 FROM sync_events WHERE id = $1',
    [eventId]
  );
  return (result.rowCount || 0) > 0;
}

export async function getUnappliedEvents(): Promise<SyncEvent[]> {
  const result = await pool.query(`
    SELECT id, event_type, payload, timestamp, source_node
    FROM sync_events
    WHERE applied = FALSE
    ORDER BY timestamp ASC
    LIMIT 100
  `);

  return result.rows.map(row => ({
    ...row,
    payload: typeof row.payload === 'string' ? JSON.parse(row.payload) : row.payload
  }));
}

export async function markEventApplied(eventId: string): Promise<void> {
  await pool.query(
    'UPDATE sync_events SET applied = TRUE, applied_at = $1 WHERE id = $2',
    [Date.now(), eventId]
  );
}
