/**
 * Project GOAT v1.0 — Exponential Backoff Retry Handler
 */

export class RetryHandler {
  async executeWithRetry<T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    baseDelayMs: number = 200
  ): Promise<T> {
    let attempt = 0;
    while (true) {
      try {
        return await fn();
      } catch (err) {
        attempt++;
        if (attempt >= maxRetries) {
          throw err;
        }
        const delay = baseDelayMs * Math.pow(2, attempt - 1);
        await new Promise((res) => setTimeout(res, delay));
      }
    }
  }
}

export const retryHandler = new RetryHandler();
