/**
 * Project GOAT v1.0 — Dashboard REST Client Implementation
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
        const mockPayload = { message: `GET response for ${options.url}` } as unknown as T;
        const res = await timeoutManager.withTimeout(Promise.resolve(mockPayload), 5000);
        return responseParser.parse<T>(res);
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
        const mockPayload = { message: `POST response for ${options.url}`, body } as unknown as T;
        const res = await timeoutManager.withTimeout(Promise.resolve(mockPayload), 5000);
        return responseParser.parse<T>(res, 201);
      } catch (err) {
        throw errorHandler.handle(err);
      }
    });
  }
}

export const apiClient = new APIClient();
export const restClient = apiClient;
