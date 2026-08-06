/**
 * Project GOAT v1.0 — Request and Response Interceptors
 */

export type RequestInterceptor = (config: unknown) => unknown;
export type ResponseInterceptor = (response: unknown) => unknown;

export class InterceptorRegistry {
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];

  useRequest(fn: RequestInterceptor): void {
    this.requestInterceptors.push(fn);
  }

  useResponse(fn: ResponseInterceptor): void {
    this.responseInterceptors.push(fn);
  }

  applyRequest(config: unknown): unknown {
    return this.requestInterceptors.reduce((acc, fn) => fn(acc), config);
  }

  applyResponse(response: unknown): unknown {
    return this.responseInterceptors.reduce((acc, fn) => fn(acc), response);
  }
}

export const interceptorRegistry = new InterceptorRegistry();
