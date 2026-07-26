/**
 * Error Tracking Service
 * Centralized error logging and tracking
 */
interface ErrorContext {
  componentName?: string;
  userId?: string;
  sessionId?: string;
  url?: string;
  timestamp?: string;
  extra?: Record<string, any>;
}

interface ErrorLog {
  id: string;
  message: string;
  stack?: string;
  componentStack?: string;
  context: ErrorContext;
  timestamp: string;
}

class ErrorTracker {
  private static instance: ErrorTracker;
  private errors: ErrorLog[] = [];
  private maxErrors: number = 100;
  private sessionId: string;

  private constructor() {
    this.sessionId = this.generateSessionId();
  }

  static getInstance(): ErrorTracker {
    if (!ErrorTracker.instance) {
      ErrorTracker.instance = new ErrorTracker();
    }
    return ErrorTracker.instance;
  }

  private generateSessionId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  }

  private generateErrorId(): string {
    return 'ERR_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 8);
  }

  logError(
    error: Error | string,
    context: Partial<ErrorContext> = {}
  ): void {
    const errorMessage = typeof error === 'string' ? error : error.message;
    const errorStack = typeof error === 'string' ? undefined : error.stack;

    const errorLog: ErrorLog = {
      id: this.generateErrorId(),
      message: errorMessage,
      stack: errorStack,
      componentStack: context.extra?.componentStack,
      context: {
        componentName: context.componentName || 'Unknown',
        userId: context.userId || this.getUserId(),
        sessionId: this.sessionId,
        url: context.url || window.location.href,
        timestamp: context.timestamp || new Date().toISOString(),
        extra: context.extra || {}
      },
      timestamp: new Date().toISOString()
    };

    // Store error
    this.errors.unshift(errorLog);
    if (this.errors.length > this.maxErrors) {
      this.errors.pop();
    }

    // Send to backend if configured
    this.sendToBackend(errorLog);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.group('🔴 Error Logged');
      console.log('ID:', errorLog.id);
      console.log('Message:', errorLog.message);
      console.log('Context:', errorLog.context);
      console.groupEnd();
    }
  }

  private getUserId(): string {
    try {
      const user = localStorage.getItem('user_data');
      if (user) {
        const parsed = JSON.parse(user);
        return parsed.id?.toString() || 'unknown';
      }
    } catch {
      // Ignore
    }
    return 'anonymous';
  }

  private async sendToBackend(errorLog: ErrorLog): Promise<void> {
    // Check if error tracking is enabled
    if (!import.meta.env.VITE_ERROR_TRACKING_ENABLED) {
      return;
    }

    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/v1/errors/log`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify(errorLog)
      });
    } catch {
      // Silent fail - don't let error tracking cause more errors
    }
  }

  getErrors(): ErrorLog[] {
    return [...this.errors];
  }

  clearErrors(): void {
    this.errors = [];
  }

  // Track API errors
  trackApiError(
    error: Error,
    endpoint: string,
    method: string,
    statusCode?: number
  ): void {
    this.logError(error, {
      componentName: 'API',
      extra: {
        endpoint,
        method,
        statusCode,
        response: error.message
      }
    });
  }

  // Track React component errors
  trackComponentError(
    error: Error,
    componentName: string,
    errorInfo?: React.ErrorInfo
  ): void {
    this.logError(error, {
      componentName,
      extra: {
        componentStack: errorInfo?.componentStack
      }
    });
  }
}

// Export singleton instance
export const errorTracker = ErrorTracker.getInstance();

// Convenience function
export const logError = (
  error: Error | string,
  context?: Partial<ErrorContext>
): void => {
  errorTracker.logError(error, context);
};

export default errorTracker;