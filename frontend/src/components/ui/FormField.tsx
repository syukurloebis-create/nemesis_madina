/**
 * Form Field Component
 * Reusable form field with validation
 */
import React, { InputHTMLAttributes, TextareaHTMLAttributes } from 'react';
import ValidationError from './ValidationError';

interface FormFieldProps {
  label: string;
  name: string;
  value: any;
  onChange: (e: React.ChangeEvent<any>) => void;
  onBlur?: (e: React.FocusEvent<any>) => void;
  error?: string;
  touched?: boolean;
  type?: 'text' | 'password' | 'email' | 'number' | 'textarea' | 'select';
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  inputClassName?: string;
  labelClassName?: string;
  options?: Array<{ value: string; label: string }>;
  rows?: number;
}

export const FormField: React.FC<FormFieldProps> = ({
  label,
  name,
  value,
  onChange,
  onBlur,
  error,
  touched,
  type = 'text',
  placeholder = '',
  required = false,
  disabled = false,
  className = '',
  inputClassName = '',
  labelClassName = '',
  options = [],
  rows = 3,
  ...props
}) => {
  const hasError = touched && error;
  
  const baseInputStyles = `
    w-full px-4 py-2.5 bg-white dark:bg-gray-800
    border rounded-lg
    transition-colors duration-200
    focus:outline-none focus:ring-2
    disabled:opacity-50 disabled:cursor-not-allowed
    ${hasError 
      ? 'border-red-500 focus:ring-red-500/20 focus:border-red-500' 
      : 'border-gray-300 dark:border-gray-600 focus:ring-blue-500/20 focus:border-blue-500'
    }
    ${inputClassName}
  `;

  const renderInput = () => {
    switch (type) {
      case 'textarea':
        return (
          <textarea
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            onBlur={onBlur}
            placeholder={placeholder}
            disabled={disabled}
            required={required}
            rows={rows}
            className={baseInputStyles}
            {...props as TextareaHTMLAttributes<HTMLTextAreaElement>}
          />
        );
      
      case 'select':
        return (
          <select
            id={name}
            name={name}
            value={value}
            onChange={onChange}
            onBlur={onBlur}
            disabled={disabled}
            required={required}
            className={baseInputStyles}
          >
            <option value="">Select an option...</option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      default:
        return (
          <input
            id={name}
            name={name}
            type={type}
            value={value}
            onChange={onChange}
            onBlur={onBlur}
            placeholder={placeholder}
            disabled={disabled}
            required={required}
            className={baseInputStyles}
            {...props as InputHTMLAttributes<HTMLInputElement>}
          />
        );
    }
  };

  return (
    <div className={`space-y-1.5 ${className}`}>
      <label
        htmlFor={name}
        className={`
          block text-sm font-medium text-gray-700 dark:text-gray-300
          ${required ? "after:content-['*'] after:ml-0.5 after:text-red-500" : ''}
          ${labelClassName}
        `}
      >
        {label}
      </label>
      
      {renderInput()}
      
      {hasError && (
        <ValidationError message={error} size="sm" />
      )}
    </div>
  );
};

export default FormField;