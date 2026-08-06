/**
 * Project GOAT v1.0 — API Error Handler
 */

export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class ErrorHandler {
  handle(error: unknown): APIError {
    if (error instanceof APIError) return error;
    if (error instanceof Error) {
      return new APIError(500, 'INTERNAL_CLIENT_ERROR', error.message);
    }
    return new APIError(500, 'UNKNOWN_ERROR', 'An unhandled communication error occurred.');
  }
}

export const errorHandler = new ErrorHandler();
