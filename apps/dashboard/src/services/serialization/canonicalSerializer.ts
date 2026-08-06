/**
 * Project GOAT v1.0 — Canonical Serializer & Parser
 */

export class CanonicalSerializer {
  serialize(data: unknown): string {
    return JSON.stringify(data, Object.keys(data as object).sort());
  }

  deserialize<T>(jsonStr: string): T {
    return JSON.parse(jsonStr) as T;
  }
}

export const canonicalSerializer = new CanonicalSerializer();
