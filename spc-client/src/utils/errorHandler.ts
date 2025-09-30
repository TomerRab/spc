/**
 * Centralized error handling utilities for the React application
 */

export interface APIError {
  message: string;
  status_code?: number;
  details?: Record<string, unknown>;
}

export interface NetworkError {
  type: 'network';
  message: string;
  originalError: Error;
}

export interface ValidationError {
  type: 'validation';
  message: string;
  field?: string;
  details?: Record<string, unknown>;
}

export interface APIErrorResponse {
  type: 'api';
  message: string;
  status_code: number;
  details?: Record<string, unknown>;
}

export type AppError = NetworkError | ValidationError | APIErrorResponse;

/**
 * Parse API error responses into a consistent format
 */
export const parseAPIError = (error: unknown): AppError => {
  // Network/connection errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      type: 'network',
      message: 'Unable to connect to the server. Please check your internet connection.',
      originalError: error
    };
  }

  // Response parsing errors
  if (error instanceof SyntaxError) {
    return {
      type: 'network',
      message: 'Invalid response from server. Please try again.',
      originalError: error
    };
  }

  // API error responses (our standardized format)
  if (typeof error === 'object' && error !== null) {
    const errorObj = error as Record<string, unknown>;
    
    if ('message' in errorObj && 'status_code' in errorObj) {
      return {
        type: 'api',
        message: String(errorObj.message),
        status_code: Number(errorObj.status_code) || 500,
        details: errorObj.details as Record<string, unknown>
      };
    }

    // Handle fetch response errors
    if ('status' in errorObj && 'statusText' in errorObj) {
      const status = Number(errorObj.status);
      return {
        type: 'api',
        message: getStatusMessage(status),
        status_code: status
      };
    }
  }

  // Fallback for unknown errors
  return {
    type: 'api',
    message: 'An unexpected error occurred. Please try again.',
    status_code: 500
  };
};

/**
 * Get user-friendly message for HTTP status codes
 */
const getStatusMessage = (status: number): string => {
  switch (status) {
    case 400:
      return 'Invalid request. Please check your input and try again.';
    case 401:
      return 'Authentication required. Please log in again.';
    case 403:
      return 'Access denied. You do not have permission for this action.';
    case 404:
      return 'The requested resource was not found.';
    case 422:
      return 'Validation failed. Please check your input.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    case 500:
      return 'Server error. Please try again later.';
    case 502:
    case 503:
    case 504:
      return 'Service temporarily unavailable. Please try again later.';
    default:
      return `An error occurred (${status}). Please try again.`;
  }
};

/**
 * Format error message for display to users
 */
export const formatErrorMessage = (error: AppError): string => {
  switch (error.type) {
    case 'network':
      return error.message;
    case 'validation':
      return error.field ? `${error.field}: ${error.message}` : error.message;
    case 'api':
      return error.message;
    default:
      return 'An unexpected error occurred.';
  }
};

/**
 * Get error severity level for UI styling
 */
export const getErrorSeverity = (error: AppError): 'error' | 'warning' | 'info' => {
  if (error.type === 'network') {
    return 'error';
  }
  
  if (error.type === 'api') {
    if (error.status_code >= 500) return 'error';
    if (error.status_code >= 400) return 'warning';
  }
  
  if (error.type === 'validation') {
    return 'warning';
  }
  
  return 'error';
};

/**
 * Check if error requires user re-authentication
 */
export const isAuthError = (error: AppError): boolean => {
  return error.type === 'api' && (error.status_code === 401 || error.status_code === 403);
};

/**
 * Check if error is retryable
 */
export const isRetryableError = (error: AppError): boolean => {
  if (error.type === 'network') return true;
  if (error.type === 'api' && error.status_code >= 500) return true;
  if (error.type === 'api' && error.status_code === 429) return true;
  return false;
};

/**
 * Log error for debugging (sanitized for security)
 */
export const logError = (error: AppError, context?: string): void => {
  const sanitizedError = {
    type: error.type,
    message: error.message,
    status_code: error.type === 'api' ? error.status_code : undefined,
    context
  };
  
  console.error('Application Error:', sanitizedError);
  
  // In production, you might want to send this to a logging service
  // Don't log sensitive information like tokens or personal data
};

/**
 * Create a validation error
 */
export const createValidationError = (message: string, field?: string): ValidationError => ({
  type: 'validation',
  message,
  field
});

/**
 * Handle async operations with consistent error handling
 */
export const handleAsync = async <T>(
  operation: () => Promise<T>,
  context?: string
): Promise<[T | null, AppError | null]> => {
  try {
    const result = await operation();
    return [result, null];
  } catch (error) {
    const appError = parseAPIError(error);
    logError(appError, context);
    return [null, appError];
  }
};