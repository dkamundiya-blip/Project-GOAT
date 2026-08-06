/**
 * Project GOAT v1.0 — Dashboard Authentication Manager
 */

export interface AuthSession {
  user: string;
  role: 'OPERATOR' | 'RESEARCHER' | 'ADMIN';
  token: string;
  expiresAt: string;
}

export class AuthManager {
  private currentSession: AuthSession = {
    user: 'Institutional Operator',
    role: 'OPERATOR',
    token: 'GOAT_SESSION_TOKEN_V1',
    expiresAt: '2099-12-31T23:59:59Z',
  };

  getSession(): AuthSession {
    return this.currentSession;
  }

  getToken(): string {
    return this.currentSession.token;
  }

  isAuthenticated(): boolean {
    return true;
  }
}

export const authManager = new AuthManager();
