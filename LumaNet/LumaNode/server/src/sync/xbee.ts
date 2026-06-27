import { SerialPort } from 'serialport';
import { DelimiterParser } from '@serialport/parser-delimiter';

const XBEE_PORT = process.env.XBEE_PORT || '/dev/ttyUSB0';
const XBEE_BAUD = parseInt(process.env.XBEE_BAUD || '115200');
const MESSAGE_DELIMITER = '\n';
const MAX_PACKET_SIZE = 256; // XBee ZigBee limit

let port: SerialPort | null = null;
let parser: DelimiterParser | null = null;
let isConnected = false;

export async function initXBee(): Promise<void> {
  return new Promise((resolve, reject) => {
    port = new SerialPort({
      path: XBEE_PORT,
      baudRate: XBEE_BAUD,
      dataBits: 8,
      parity: 'none',
      stopBits: 1,
      autoOpen: false
    });

    parser = port.pipe(new DelimiterParser({ delimiter: MESSAGE_DELIMITER }));

    port.open((err) => {
      if (err) {
        console.error('Failed to open XBee port:', err);
        reject(err);
        return;
      }

      isConnected = true;
      console.log(`XBee connected on ${XBEE_PORT} at ${XBEE_BAUD} baud`);
      resolve();
    });

    port.on('error', (err) => {
      console.error('XBee error:', err);
      isConnected = false;
    });

    port.on('close', () => {
      console.warn('XBee connection closed');
      isConnected = false;
    });
  });
}

export function onXBeeMessage(callback: (data: Buffer) => void): void {
  if (!parser) {
    throw new Error('XBee not initialized');
  }
  parser.on('data', callback);
}

export async function sendXBeeMessage(data: string): Promise<boolean> {
  if (!port || !isConnected) {
    console.warn('XBee not connected, cannot send message');
    return false;
  }

  // Check packet size
  if (Buffer.byteLength(data) > MAX_PACKET_SIZE - MESSAGE_DELIMITER.length) {
    console.error('Message exceeds XBee packet size limit');
    return false;
  }

  return new Promise((resolve) => {
    port!.write(data + MESSAGE_DELIMITER, (err) => {
      if (err) {
        console.error('XBee write error:', err);
        resolve(false);
      } else {
        resolve(true);
      }
    });
  });
}

export function closeXBee(): void {
  if (port && port.isOpen) {
    port.close();
  }
  isConnected = false;
}

export function isXBeeConnected(): boolean {
  return isConnected;
}
