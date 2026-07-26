/**
 * Validation Error Component
 * Displays validation error messages
 */
import React from 'react';
import { AlertCircle, X } from 'lucide-react';

interface ValidationErrorProps {
  message: string;
  className?: string;
  onDismiss?: () => void;
  size?: 'sm' | 'md' | 'lg';
}

export const ValidationError: React.FC<ValidationErrorProps> = ({
  message,
  className = '',
  onDismiss,
  size = 'md'
}) => {
  const sizeStyles = {
    sm: 'text-xs py-1 px-2',
    md: 'text-sm py-1.5 px-3',
    lg: 'text-base py-2 px-4'
  };

  if (!message) return null;

  return (
    <div className={`
      flex items-start gap-2 text-red-600 dark:text-red-400
      ${sizeStyles[size]}
      ${className}
    `}>
      <AlertCircle className="flex-shrink-0 w-4 h-4 mt-0.5" />
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 hover:text-red-800 dark:hover:text-red-300 transition-colors"
          type="button"
        >
          <X className="w-3 h-3" />
        </button>
      )}
    </div>
  );
};

export default ValidationError;