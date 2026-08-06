/**
 * Project GOAT v1.0 — Dashboard Query Cache Manager
 */

export class QueryCacheManager {
  private cache: Map<string, { data: unknown; timestamp: number }> = new Map();
  private readonly defaultTTL = 30000; // 30 seconds

  set(key: string, data: unknown, ttlMs: number = this.defaultTTL): void {
    this.cache.set(key, { data, timestamp: Date.now() + ttlMs });
  }

  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    if (Date.now() > cached.timestamp) {
      this.cache.delete(key);
      return null;
    }
    return cached.data as T;
  }

  clear(): void {
    this.cache.clear();
  }
}

export const queryCache = new QueryCacheManager();
