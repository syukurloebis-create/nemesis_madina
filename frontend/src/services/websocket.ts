/**
 * WebSocket Service
 */
type EventHandler = (data: any) => void;

export class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<EventHandler>> = new Map();

  private constructor() {}

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  connect(): void {
    // Simplified
  }

  disconnect(): void {
    // Simplified
  }

  send(data: any): void {
    // Simplified
  }

  on(event: string, handler: EventHandler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);
    return () => {
      const handlers = this.handlers.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) this.handlers.delete(event);
      }
    };
  }

  onAlert(handler: (data: any) => void): () => void {
    return this.on('alert', handler);
  }
}

const wsService = WebSocketService.getInstance();

export default wsService;
export { wsService };
