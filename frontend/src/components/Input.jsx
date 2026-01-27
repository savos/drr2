import { forwardRef } from 'react';
import { Icon } from '../utils/icons';

/**
 * Enhanced Input component with icon support, validation states, and accessibility
 *
 * @param {string} label - Label text for the input
 * @param {string} error - Error message to display
 * @param {string} success - Success message to display
 * @param {string} icon - Icon name to display on the left side
 * @param {string} helperText - Helper text to display below input
 * @param {boolean} required - Whether the field is required
 * @param {string} className - Additional classes for the input wrapper
 * @param {object} ...props - All other input props (type, value, onChange, etc.)
 */
export const Input = forwardRef(({
  label,
  error,
  success,
  icon,
  helperText,
  required,
  className = '',
  ...props
}, ref) => {
  // Determine validation state classes
  const getValidationClasses = () => {
    if (error) {
      return 'border-red-500 dark:border-red-400 bg-red-50 dark:bg-red-900/10 focus:border-red-500 dark:focus:border-red-400 focus:ring-red-100 dark:focus:ring-red-900/50';
    }
    if (success) {
      return 'border-emerald-500 dark:border-emerald-400 bg-emerald-50 dark:bg-emerald-900/10 focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-emerald-100 dark:focus:ring-emerald-900/50';
    }
    return 'border-zinc-300 dark:border-zinc-600 bg-white dark:bg-zinc-900 focus:border-indigo-500 dark:focus:border-indigo-400 focus:ring-indigo-100 dark:focus:ring-indigo-900/50';
  };

  return (
    <div className={`form-group ${className}`}>
      {label && (
        <label
          htmlFor={props.id}
          className="text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-1.5 block"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      <div className="relative">
        {/* Icon on the left */}
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <Icon
              name={icon}
              size="sm"
              className={`${error ? 'text-red-500' : success ? 'text-emerald-500' : 'text-zinc-400 dark:text-zinc-500'}`}
            />
          </div>
        )}

        {/* Input field */}
        <input
          ref={ref}
          className={`
            w-full px-4 py-3
            ${icon ? 'pl-10' : ''}
            border rounded-lg text-base
            text-zinc-900 dark:text-zinc-100
            transition-all duration-200 outline-none
            placeholder:text-zinc-400 dark:placeholder:text-zinc-500
            disabled:opacity-60 disabled:cursor-not-allowed
            ${getValidationClasses()}
          `}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={
            error ? `${props.id}-error` :
            success ? `${props.id}-success` :
            helperText ? `${props.id}-helper` :
            undefined
          }
          {...props}
        />

        {/* Validation icon on the right */}
        {(error || success) && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <Icon
              name={error ? 'warning' : 'check'}
              variant="solid"
              size="sm"
              className={error ? 'text-red-500' : 'text-emerald-500'}
            />
          </div>
        )}
      </div>

      {/* Helper text */}
      {helperText && !error && !success && (
        <p id={`${props.id}-helper`} className="text-xs mt-1.5 text-zinc-500 dark:text-zinc-400">
          {helperText}
        </p>
      )}

      {/* Error message */}
      {error && (
        <p id={`${props.id}-error`} className="text-xs mt-1.5 font-medium text-red-600 dark:text-red-400 flex items-center gap-1">
          {error}
        </p>
      )}

      {/* Success message */}
      {success && (
        <p id={`${props.id}-success`} className="text-xs mt-1.5 font-medium text-emerald-600 dark:text-emerald-400 flex items-center gap-1">
          {success}
        </p>
      )}
    </div>
  );
});

Input.displayName = 'Input';
