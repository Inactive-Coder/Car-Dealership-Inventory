import { apiRequest } from './api';
import type { TokenResponse, User } from '../types/api';

const TOKEN_KEY = 'car-inventory-token';
const USER_KEY = 'car-inventory-user';

export interface Session {
  token: string;
  user: User;
}

export async function login(email: string, password: string): Promise<Session> {
  const result = await apiRequest<TokenResponse>(
    '/api/auth/login',
    { method: 'POST', body: JSON.stringify({ email, password }) },
    false,
  );
  const session = { token: result.access_token, user: result.user };
  localStorage.setItem(TOKEN_KEY, session.token);
  localStorage.setItem(USER_KEY, JSON.stringify(session.user));
  return session;
}

export async function register(email: string, password: string): Promise<User> {
  return apiRequest<User>(
    '/api/auth/register',
    { method: 'POST', body: JSON.stringify({ email, password }) },
    false,
  );
}

export function loadSession(): Session | null {
  const token = localStorage.getItem(TOKEN_KEY);
  const serializedUser = localStorage.getItem(USER_KEY);
  if (!token || !serializedUser) return null;
  try {
    return { token, user: JSON.parse(serializedUser) as User };
  } catch {
    logout();
    return null;
  }
}

export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}
