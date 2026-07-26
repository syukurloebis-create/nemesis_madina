/**
 * Retry Hook
 * Provides retry logic for operations
 */
import { useState, useCallback, useRef } from 'react';

interface UseRetryOptions<T> {
  maxRetries?: number;
  retryDelay?: (retryCount: number) => number;
  onRetry?: (retryCount: number) => void;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  initialData?: T;
}

interface UseRetryReturn<T> {
  data: T | undefined;
  loading: boolean;
  error: Error | null;
  retryCount: number;
  execute: (...args: any[]) => Promise<T | undefined>;
  reset: () => void;
  cancel: () => void;
}

export function useRetry<T>(
  fn: (...args: any[]) => Promise<T>,
  options: UseRetryOptions<T> = {}
): UseRetryReturn<T> {
  const {
    maxRetries = 3,
    retryDelay = (retryCount) => Math.min(1000 * Math.pow(2, retryCount), 30000),
    onRetry,
    onSuccess,
    onError,
    initialData
  } = options;

  const [data, setData] = useState<T | undefined>(initialData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const cancelRef = useRef<boolean>(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const reset = useCallback(() => {
    setData(initialData);
    setError(null);
    setRetryCount(0);
    cancelRef.current = false;
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, [initialData]);

  const cancel = useCallback(() => {
    cancelRef.current = true;
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  const execute = useCallback(
    async (...args: any[]): Promise<T | undefined> => {
      // Reset state on new execution
      if (retryCount === 0) {
        setError(null);
        setData(undefined);
      }
      setLoading(true);

      try {
        const result = await fn(...args);
        if (!cancelRef.current) {
          setData(result);
          setError(null);
          setRetryCount(0);
          onSuccess?.(result);
        }
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        
        // Check if we should retry
        const shouldRetry = 
          !cancelRef.current && 
          retryCount < maxRetries &&
          this.shouldRetry(error);

        if (shouldRetry) {
          setRetryCount((prev) => prev + 1);
          onRetry?.(retryCount + 1);

          // Wait for delay
          await new Promise((resolve) => {
            timeoutRef.current = setTimeout(resolve, retryDelay(retryCount));
          });

          // Retry
          return execute(...args);
        }

        // No more retries
        if (!cancelRef.current) {
          setError(error);
          onError?.(error);
        }
        return undefined;
      } finally {
        if (!cancelRef.current) {
          setLoading(false);
        }
      }
    },
    [fn, maxRetries, retryCount, retryDelay, onRetry, onSuccess, onError]
  );

  return {
    data,
    loading,
    error,
    retryCount,
    execute,
    reset,
    cancel
  };
}

// Helper function to determine if error is retryable
function shouldRetry(error: Error): boolean {
  // Network errors
  if (error.message === 'Network Error') return true;
  
  // Timeout errors
  if (error.message.includes('timeout')) return true;
  
  // Server errors (5xx)
  const match = error.message.match(/status (\d{3})/);
  if (match) {
    const status = parseInt(match[1]);
    return status >= 500 && status < 600;
  }
  
  return false;
}

export default useRetry;