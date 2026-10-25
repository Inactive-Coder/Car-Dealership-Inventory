import { useMemo, useState, type ReactNode } from 'react';
import { loadSession, login, logout, register, type Session } from '../services/auth';
import { AuthContext, type AuthContextValue } from './auth-context';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(() => loadSession());

  const value = useMemo<AuthContextValue>(() => ({
    session,
    async signIn(email, password) {
      setSession(await login(email, password));
    },
    signUp: register,
    signOut() {
      logout();
      setSession(null);
    },
  }), [session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
