/**
 * Project GOAT v1.0 — REST Response Parser
 */

export interface ParsedResponse<T> {
  data: T;
  status: number;
  headers: Record<string, string>;
  timestamp: string;
}

export class ResponseParser {
  parse<T>(rawPayload: unknown, status: number = 200): ParsedResponse<T> {
    return {
      data: rawPayload as T,
      status,
      headers: { 'content-type': 'application/json' },
      timestamp: new Date().toISOString(),
    };
  }
}

export const responseParser = new ResponseParser();
