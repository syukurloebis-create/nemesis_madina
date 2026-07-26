/**
 * WebSocket Service
 * Real-time communication with server
 */
type WebSocketEvent = {
  type: string;
  payload: any;
  timestamp: string;
};

type EventHandler = (data: any) => void;

class WebSocketService {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private handlers: Map<string, Set<EventHandler>> = new Map();
  private isConnecting = false;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private url: string;

  private constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_WS_HOST || window.location.host;
    const path = import.meta.env.VITE_WS_PATH || '/ws';
    this.url = `${protocol}//${host}${path}`;
  }

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      // Get auth token
      const token = localStorage.getItem('access_token');
      const wsUrl = token ? `${this.url}?token=${token}` : this.url;
      
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.isConnecting = false;
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnecting = false;
    this.reconnectAttempts = 0;
  }

  private handleOpen(): void {
    console.log('✅ WebSocket connected');
    this.isConnecting = false;
    this.reconnectAttempts = 0;

    // Start heartbeat
    this.startHeartbeat();

    // Emit connection event
    this.emit('connection', { status: 'connected', timestamp: new Date().toISOString() });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data) as WebSocketEvent;
      this.processMessage(data);
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private processMessage(data: WebSocketEvent): void {
    const handlers = this.handlers.get(data.type);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data.payload);
        } catch (error) {
          console.error(`Error in handler for ${data.type}:`, error);
        }
      });
    }

    // Also handle wildcard listeners
    const wildcardHandlers = this.handlers.get('*');
    if (wildcardHandlers) {
      wildcardHandlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error('Error in wildcard handler:', error);
        }
      });
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket disconnected:', event.code, event.reason);
    this.isConnecting = false;
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }

    // Don't reconnect if closed intentionally
    if (event.code !== 1000) {
      this.scheduleReconnect();
    }
  }

  private handleError(error: Event): void {
    console.error('WebSocket error:', error);
    this.isConnecting = false;
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts);
      this.reconnectTimeout = setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnect attempts reached');
      this.emit('connection', { status: 'failed', error: 'Max reconnect attempts reached' });
    }
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', payload: { timestamp: new Date().toISOString() } });
      }
    }, 30000); // 30 seconds
  }

  send(data: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected, message queued');
      // Queue message for when connection is restored
      setTimeout(() => this.send(data), 1000);
    }
  }

  on(event: string, handler: EventHandler): () => void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(event);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.handlers.delete(event);
        }
      }
    };
  }

  private emit(event: string, payload: any): void {
    const data: WebSocketEvent = {
      type: event,
      payload,
      timestamp: new Date().toISOString()
    };
    this.processMessage(data);
  }

  // Subscribe to specific event types
  subscribe(eventType: string, handler: EventHandler): () => void {
    return this.on(eventType, handler);
  }

  // Subscribe to all events
  subscribeAll(handler: EventHandler): () => void {
    return this.on('*', handler);
  }

  // Convenience methods for specific events
  onAlert(handler: (alert: any) => void): () => void {
    return this.on('alert', handler);
  }

  onCaseUpdate(handler: (caseData: any) => void): () => void {
    return this.on('case_update', handler);
  }

  onGraphUpdate(handler: (graphData: any) => void): () => void {
    return this.on('graph_update', handler);
  }

  onRiskUpdate(handler: (riskData: any) => void): () => void {
    return this.on('risk_update', handler);
  }

  onFraudDetection(handler: (fraudData: any) => void): () => void {
    return this.on('fraud_detection', handler);
  }
}

export default WebSocketService.getInstance();