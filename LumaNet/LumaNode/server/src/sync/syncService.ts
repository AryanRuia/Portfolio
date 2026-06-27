import { initXBee, onXBeeMessage, sendXBeeMessage } from './xbee';
import { createEvent, saveEvent, eventExists, getUnappliedEvents, markEventApplied, SyncEvent } from './eventLog';
import { applyEvent } from './applyEvent';

const SYNC_INTERVAL = 30000; // 30 seconds
const BATCH_SIZE = 10;

export async function startSyncService(): Promise<void> {
  try {
    // Initialize XBee
    await initXBee();
    console.log('XBee mesh initialized');

    // Listen for incoming events
    onXBeeMessage(handleIncomingMessage);

    // Periodic sync of unapplied events
    setInterval(processUnappliedEvents, SYNC_INTERVAL);

    console.log('Sync service running');
  } catch (error) {
    console.error('Failed to start sync service:', error);
    // Continue without XBee if it fails (graceful degradation)
  }
}

function handleIncomingMessage(data: Buffer): void {
  try {
    const message = data.toString().trim();
    if (!message) return;

    const event: SyncEvent = JSON.parse(message);

    // Validate event structure
    if (!event.id || !event.event_type || !event.payload) {
      console.warn('Invalid event received, skipping');
      return;
    }

    // Check for duplicates
    eventExists(event.id).then(exists => {
      if (exists) {
        console.log(`Event ${event.id} already exists, skipping`);
        return;
      }

      console.log(`Received event: ${event.event_type} from ${event.source_node}`);

      // Save and apply event
      saveEvent(event)
        .then(() => applyEvent(event))
        .then(() => markEventApplied(event.id))
        .then(() => {
          console.log(`Applied event: ${event.id}`);
          // Rebroadcast to mesh (flood protocol)
          rebroadcastEvent(event);
        })
        .catch(err => {
          console.error('Error processing event:', err);
        });
    });
  } catch (error) {
    console.error('Error parsing incoming message:', error);
  }
}

async function processUnappliedEvents(): Promise<void> {
  try {
    const events = await getUnappliedEvents();
    for (const event of events.slice(0, BATCH_SIZE)) {
      await applyEvent(event);
      await markEventApplied(event.id);
      console.log(`Applied queued event: ${event.id}`);
    }
  } catch (error) {
    console.error('Error processing unapplied events:', error);
  }
}

export async function broadcastEvent(event: SyncEvent): Promise<void> {
  const message = JSON.stringify(event);
  const sent = await sendXBeeMessage(message);
  
  if (sent) {
    console.log(`Broadcasted event: ${event.event_type} (${event.id})`);
  } else {
    console.warn(`Failed to broadcast event: ${event.id}`);
  }
}

async function rebroadcastEvent(event: SyncEvent): Promise<void> {
  // Only rebroadcast events from other nodes
  if (event.source_node === process.env.NODE_ID) {
    return;
  }
  
  await broadcastEvent(event);
}
