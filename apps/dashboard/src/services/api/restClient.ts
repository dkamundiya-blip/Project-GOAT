/**
 * Project GOAT v1.1 — Dashboard REST Client Implementation
 *
 * Production REST API client making live HTTP requests to backend gateway.
 * Zero mock returns or dummy payloads.
 */

import { requestBuilder } from './requestBuilder';
import { responseParser, ParsedResponse } from './responseParser';
import { errorHandler } from './errorHandler';
import { retryHandler } from './retryHandler';
import { timeoutManager } from './timeoutManager';

export class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string, params?: Record<string, string | number>): Promise<ParsedResponse<T>> {
    return retryHandler.executeWithRetry(async () => {
      const options = requestBuilder.build({
        method: 'GET',
        url: `${this.baseUrl}${endpoint}`,
        params,
      });

      try {
        const fetchPromise = fetch(options.url, {
          method: 'GET',
          headers: options.headers,
        }).then(async (res) => {
          if (!res.ok) {
            throw new Error(`HTTP Error (${res.status} ${res.statusText})`);
          }
          return await res.json();
        });

        const rawData = await timeoutManager.withTimeout(fetchPromise, 10000);
        return responseParser.parse<T>(rawData);
      } catch (err) {
        throw errorHandler.handle(err);
      }
    });
  }

  async post<T>(endpoint: string, body: unknown): Promise<ParsedResponse<T>> {
    return retryHandler.executeWithRetry(async () => {
      const options = requestBuilder.build({
        method: 'POST',
        url: `${this.baseUrl}${endpoint}`,
        body,
      });

      try {
        const fetchPromise = fetch(options.url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...options.headers },
          body: JSON.stringify(body),
        }).then(async (res) => {
          if (!res.ok) {
            throw new Error(`HTTP Error (${res.status} ${res.statusText})`);
          }
          return await res.json();
        });

        const rawData = await timeoutManager.withTimeout(fetchPromise, 10000);
        return responseParser.parse<T>(rawData, 201);
      } catch (err) {
        throw errorHandler.handle(err);
      }
    });
  }
}

export const apiClient = new APIClient();
export const restClient = apiClient;
