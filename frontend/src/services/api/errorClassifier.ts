/**
 * Error Classifier Service
 * Classifies errors for retry decision
 */
export enum ErrorType {
  NETWORK = 'network',
  SERVER = 'server',
  RATE_LIMIT = 'rate_limit',
  AUTHENTICATION = 'authentication',
  CLIENT = 'client',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown'
}

export interface ClassificationResult {
  type: ErrorType;
  shouldRetry: boolean;
  retryable: boolean;
  statusCode?: number;
}

class ErrorClassifier {
  private static instance: ErrorClassifier;

  private constructor() {}

  static getInstance(): ErrorClassifier {
    if (!ErrorClassifier.instance) {
      ErrorClassifier.instance = new ErrorClassifier();
    }
    return ErrorClassifier.instance;
  }

  classify(error: any): ClassificationResult {
    // Check if error has response (axios error)
    if (error.response) {
      const status = error.response.status;

      // 4xx errors
      if (status >= 400 && status < 500) {
        return {
          type: this.classifyClientError(status),
          shouldRetry: this.isRetryableClientError(status),
          retryable: this.isRetryableClientError(status),
          statusCode: status
        };
      }

      // 5xx errors
      if (status >= 500 && status < 600) {
        return {
          type: ErrorType.SERVER,
          shouldRetry: true,
          retryable: true,
          statusCode: status
        };
      }
    }

    // Network errors
    if (error.message === 'Network Error' || error.code === 'ECONNABORTED') {
      return {
        type: ErrorType.NETWORK,
        shouldRetry: true,
        retryable: true
      };
    }

    // Timeout errors
    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      return {
        type: ErrorType.TIMEOUT,
        shouldRetry: true,
        retryable: true
      };
    }

    // Authentication errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      return {
        type: ErrorType.AUTHENTICATION,
        shouldRetry: false,
        retryable: false,
        statusCode: error.response.status
      };
    }

    // Rate limit errors
    if (error.response?.status === 429) {
      return {
        type: ErrorType.RATE_LIMIT,
        shouldRetry: true,
        retryable: true,
        statusCode: 429
      };
    }

    // Unknown
    return {
      type: ErrorType.UNKNOWN,
      shouldRetry: false,
      retryable: false
    };
  }

  private classifyClientError(status: number): ErrorType {
    if (status === 401 || status === 403) {
      return ErrorType.AUTHENTICATION;
    }
    if (status === 429) {
      return ErrorType.RATE_LIMIT;
    }
    if (status >= 400 && status < 500) {
      return ErrorType.CLIENT;
    }
    return ErrorType.UNKNOWN;
  }

  private isRetryableClientError(status: number): boolean {
    // Retry on rate limit and some other client errors
    return status === 429 || status === 408 || status === 425;
  }

  getRetryDelay(retryCount: number): number {
    // Exponential backoff: 1s, 2s, 4s, 8s, 16s, 32s
    const baseDelay = 1000;
    const delay = baseDelay * Math.pow(2, retryCount);
    // Cap at 30 seconds
    return Math.min(delay, 30000);
  }

  getMaxRetries(): number {
    return 5;
  }

  shouldRetry(error: any, retryCount: number): boolean {
    const classification = this.classify(error);
    if (!classification.shouldRetry) {
      return false;
    }
    return retryCount < this.getMaxRetries();
  }
}

export default ErrorClassifier.getInstance();