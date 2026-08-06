/**
 * Project GOAT v1.0 — Request Timeout Manager
 */

export class TimeoutManager {
  withTimeout<T>(promise: Promise<T>, timeoutMs: number = 5000): Promise<T> {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error(`Request timed out after ${timeoutMs}ms`));
      }, timeoutMs);

      promise
        .then((res) => {
          clearTimeout(timer);
          resolve(res);
        })
        .catch((err) => {
          clearTimeout(timer);
          reject(err);
        });
    });
  }
}

export const timeoutManager = new TimeoutManager();
