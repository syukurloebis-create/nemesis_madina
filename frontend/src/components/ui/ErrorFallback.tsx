/**
 * Error Fallback Component
 * Displayed when an error is caught by ErrorBoundary
 */
import React from 'react';
import { RefreshCw, AlertTriangle, Home, ChevronLeft } from 'lucide-react';

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
  className?: string;
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({
  error,
  resetError,
  className = '',
}) => {
  const handleReload = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleGoBack = () => {
    window.history.back();
  };

  return (
    <div className={`min-h-[400px] flex items-center justify-center p-6 ${className}`}>
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-lg w-full p-8 border border-gray-200 dark:border-gray-700">
        {/* Icon */}
        <div className="flex items-center justify-center w-16 h-16 mx-auto bg-red-100 dark:bg-red-900/20 rounded-full mb-4">
          <AlertTriangle className="w-8 h-8 text-red-600 dark:text-red-400" />
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-2">
          Something Went Wrong
        </h2>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 text-center mb-4">
          We apologize for the inconvenience. An unexpected error has occurred.
        </p>

        {/* Error Details */}
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 mb-6 overflow-auto max-h-32">
          <p className="text-sm font-mono text-red-600 dark:text-red-400 break-all">
            {error.message || 'Unknown error'}
          </p>
          {error.stack && (
            <details className="mt-2">
              <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                Show stack trace
              </summary>
              <pre className="text-xs text-gray-600 dark:text-gray-400 mt-2 whitespace-pre-wrap">
                {error.stack}
              </pre>
            </details>
          )}
        </div>

        {/* Error Code */}
        <div className="text-xs text-center text-gray-400 mb-6">
          Error ID: {Date.now().toString(36).toUpperCase()}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            onClick={resetError}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          
          <button
            onClick={handleGoBack}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-medium rounded-lg transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Go Back
          </button>
          
          <button
            onClick={handleGoHome}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-medium rounded-lg transition-colors"
          >
            <Home className="w-4 h-4" />
            Home
          </button>
        </div>

        {/* Support Link */}
        <p className="text-center text-sm text-gray-500 mt-4">
          Need help?{' '}
          <button
            onClick={() => {
              // Open support modal or redirect
              window.location.href = '/support';
            }}
            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
          >
            Contact Support
          </button>
        </p>
      </div>
    </div>
  );
};

export default ErrorFallback;