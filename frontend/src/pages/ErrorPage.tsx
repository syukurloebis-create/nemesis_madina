/**
 * Error Page
 * Dedicated page for displaying errors
 */
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { RefreshCw, Home, AlertTriangle } from 'lucide-react';

interface ErrorPageProps {
  statusCode?: number;
  title?: string;
  message?: string;
}

export const ErrorPage: React.FC<ErrorPageProps> = ({
  statusCode = 500,
  title = 'Something went wrong',
  message = 'An unexpected error occurred. Please try again later.'
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Extract error from location state if available
  const stateError = location.state?.error as Error | undefined;

  const handleRefresh = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    navigate('/');
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-6">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full p-12 border border-gray-200 dark:border-gray-700">
        {/* Status Code */}
        <div className="text-center">
          <div className="text-9xl font-bold text-red-500 dark:text-red-400">
            {statusCode}
          </div>
        </div>

        {/* Icon */}
        <div className="flex justify-center mt-4">
          <div className="bg-red-100 dark:bg-red-900/20 rounded-full p-6">
            <AlertTriangle className="w-16 h-16 text-red-600 dark:text-red-400" />
          </div>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white mt-6">
          {title}
        </h1>

        {/* Message */}
        <p className="text-gray-600 dark:text-gray-400 text-center mt-3">
          {message}
        </p>

        {/* Error Details (if available) */}
        {stateError && (
          <div className="mt-6 bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 overflow-auto max-h-40">
            <p className="text-sm font-mono text-red-600 dark:text-red-400">
              {stateError.message}
            </p>
            {stateError.stack && (
              <details className="mt-2">
                <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                  Stack trace
                </summary>
                <pre className="text-xs text-gray-600 dark:text-gray-400 mt-2 whitespace-pre-wrap">
                  {stateError.stack}
                </pre>
              </details>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 mt-8">
          <button
            onClick={handleRefresh}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            <RefreshCw className="w-5 h-5" />
            Try Again
          </button>

          <button
            onClick={handleGoBack}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-medium rounded-lg transition-colors"
          >
            Go Back
          </button>

          <button
            onClick={handleGoHome}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-medium rounded-lg transition-colors"
          >
            <Home className="w-5 h-5" />
            Home
          </button>
        </div>

        {/* Error ID */}
        <div className="text-xs text-center text-gray-400 mt-6">
          Error ID: {Date.now().toString(36).toUpperCase()}
        </div>
      </div>
    </div>
  );
};

export default ErrorPage;