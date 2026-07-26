/**
 * Retry Interceptor
 * Implements retry logic with exponential backoff
 */
import { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import errorClassifier, { ErrorType } from './errorClassifier';

export interface RetryConfig {
  maxRetries?: number;
  retryDelay?: (retryCount: number) => number;
  retryCondition?: (error: AxiosError) => boolean;
  onRetry?: (retryCount: number, error: AxiosError) => void;
}

export interface RetryableRequest extends InternalAxiosRequestConfig {
  _retryCount?: number;
  _retryConfig?: RetryConfig;
}

class RetryInterceptor {
  private static instance: RetryInterceptor;
  private defaultConfig: RetryConfig = {
    maxRetries: 3,
    retryDelay: (retryCount: number) => {
      // Exponential backoff with jitter
      const baseDelay = 1000;
      const delay = baseDelay * Math.pow(2, retryCount);
      const jitter = delay * (Math.random() * 0.2);
      return Math.min(delay + jitter, 30000);
    },
    retryCondition: (error: AxiosError) => {
      const classification = errorClassifier.classify(error);
      return classification.shouldRetry;
    },
    onRetry: (retryCount: number, error: AxiosError) => {
      console.log(`🔄 Retry attempt ${retryCount + 1}:`, error.message);
    }
  };

  private constructor() {}

  static getInstance(): RetryInterceptor {
    if (!RetryInterceptor.instance) {
      RetryInterceptor.instance = new RetryInterceptor();
    }
    return RetryInterceptor.instance;
  }

  setup(apiClient: AxiosInstance, customConfig?: RetryConfig): void {
    const config = { ...this.defaultConfig, ...customConfig };

    apiClient.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const request = error.config as RetryableRequest;

        // Skip if request was cancelled
        if (error.code === 'ECONNABORTED' && request?.signal?.aborted) {
          return Promise.reject(error);
        }

        // Skip if no request
        if (!request) {
          return Promise.reject(error);
        }

        // Initialize retry count
        request._retryCount = request._retryCount || 0;

        // Check if we should retry
        const shouldRetry = config.retryCondition?.(error) ?? false;
        const maxRetries = config.maxRetries ?? 3;

        if (shouldRetry && request._retryCount < maxRetries) {
          // Increment retry count
          request._retryCount++;

          // Call onRetry callback
          config.onRetry?.(request._retryCount, error);

          // Calculate delay
          const delay = config.retryDelay?.(request._retryCount) ?? 1000;

          // Wait for delay
          await new Promise((resolve) => setTimeout(resolve, delay));

          // Retry request
          return apiClient(request);
        }

        // No more retries, reject
        return Promise.reject(error);
      }
    );
  }
}

export default RetryInterceptor.getInstance();