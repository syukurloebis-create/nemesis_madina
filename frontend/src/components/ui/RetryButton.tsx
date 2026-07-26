/**
 * Retry Button Component
 * Button with retry functionality
 */
import React, { useState } from 'react';
import { RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

interface RetryButtonProps {
  onRetry: () => Promise<void> | void;
  children?: React.ReactNode;
  className?: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  showStatus?: boolean;
  successDuration?: number;
}

export const RetryButton: React.FC<RetryButtonProps> = ({
  onRetry,
  children = 'Retry',
  className = '',
  variant = 'primary',
  size = 'md',
  disabled = false,
  showStatus = true,
  successDuration = 2000
}) => {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const variantStyles = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white'
  };

  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };

  const handleClick = async () => {
    if (loading || disabled) return;

    setLoading(true);
    setStatus('idle');
    setErrorMessage(null);

    try {
      await onRetry();
      setStatus('success');
      
      // Reset after success duration
      setTimeout(() => {
        setStatus('idle');
      }, successDuration);
    } catch (error) {
      setStatus('error');
      setErrorMessage(error instanceof Error ? error.message : 'Retry failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <button
        onClick={handleClick}
        disabled={loading || disabled || status === 'success'}
        className={`
          inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${loading ? 'opacity-70 cursor-wait' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${status === 'success' ? '!bg-green-600' : ''}
          ${status === 'error' ? '!bg-red-600' : ''}
          ${className}
        `}
      >
        {loading ? (
          <>
            <RefreshCw className="w-4 h-4 animate-spin" />
            Retrying...
          </>
        ) : status === 'success' ? (
          <>
            <CheckCircle className="w-4 h-4" />
            Success
          </>
        ) : status === 'error' ? (
          <>
            <AlertCircle className="w-4 h-4" />
            Failed
          </>
        ) : (
          <>
            <RefreshCw className="w-4 h-4" />
            {children}
          </>
        )}
      </button>

      {showStatus && errorMessage && status === 'error' && (
        <span className="text-xs text-red-600 dark:text-red-400 mt-1">
          {errorMessage}
        </span>
      )}
    </div>
  );
};

export default RetryButton;