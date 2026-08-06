/**
 * Project GOAT v1.0 — REST Request Builder
 */

export interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  url: string;
  headers?: Record<string, string>;
  params?: Record<string, string | number>;
  body?: unknown;
  timeoutMs?: number;
}

export class RequestBuilder {
  build(options: RequestOptions): RequestInit & { url: string } {
    const headers = {
      'Content-Type': 'application/json',
      'X-Goat-Client-Version': '1.0.0',
      ...(options.headers || {}),
    };

    let fullUrl = options.url;
    if (options.params) {
      const query = new URLSearchParams(
        Object.entries(options.params).reduce((acc, [k, v]) => ({ ...acc, [k]: String(v) }), {})
      ).toString();
      fullUrl += `?${query}`;
    }

    return {
      url: fullUrl,
      method: options.method,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    };
  }
}

export const requestBuilder = new RequestBuilder();
