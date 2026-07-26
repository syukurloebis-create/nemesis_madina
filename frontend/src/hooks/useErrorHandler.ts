/**
 * Error Handling Hook
 * Provides error handling utilities for components
 */
import { useState, useCallback } from 'react';
import { logError } from '../services/errorTracker';

interface ErrorState {
  error: Error | null;
  hasError: boolean;
  message: string | null;
}

interface ErrorHandlerOptions {
  componentName?: string;
  onError?: (error: Error) => void;
  silenceErrors?: boolean;
}

export function useErrorHandler(options: ErrorHandlerOptions = {}) {
  const [errorState, setErrorState] = useState<ErrorState>({
    error: null,
    hasError: false,
    message: null
  });

  const handleError = useCallback(
    (error: Error | string, context?: Record<string, any>) => {
      const errorObj = typeof error === 'string' ? new Error(error) : error;

      setErrorState({
        error: errorObj,
        hasError: true,
        message: errorObj.message
      });

      // Log error to tracking service
      if (!options.silenceErrors) {
        logError(errorObj, {
          componentName: options.componentName || 'UnknownComponent',
          extra: context
        });
      }

      // Call custom error handler
      if (options.onError) {
        options.onError(errorObj);
      }

      return errorObj;
    },
    [options]
  );

  const clearError = useCallback(() => {
    setErrorState({
      error: null,
      hasError: false,
      message: null
    });
  }, []);

  const wrapAsync = useCallback(
    async <T>(
      fn: () => Promise<T>,
      errorContext?: Record<string, any>
    ): Promise<T | undefined> => {
      try {
        return await fn();
      } catch (error) {
        handleError(error as Error, errorContext);
        return undefined;
      }
    },
    [handleError]
  );

  return {
    error: errorState.error,
    hasError: errorState.hasError,
    message: errorState.message,
    handleError,
    clearError,
    wrapAsync
  };
}

export default useErrorHandler;