/**
 * Project GOAT v1.0 — Dashboard Authentication Placeholder Service
 */

export interface AuthSession {
  user: string;
  role: 'OPERATOR' | 'RESEARCHER' | 'ADMIN';
  token: string;
  expiresAt: string;
}

export class AuthClient {
  private session: AuthSession = {
    user: 'Institutional Operator',
    role: 'OPERATOR',
    token: 'GOAT_SESSION_TOKEN_MOCK',
    expiresAt: '2099-12-31T23:59:59Z',
  };

  getSession(): AuthSession {
    return this.session;
  }

  isAuthenticated(): boolean {
    return true;
  }
}

export const authClient = new AuthClient();
