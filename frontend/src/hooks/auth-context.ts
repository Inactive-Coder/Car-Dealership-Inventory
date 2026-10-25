import { createContext } from 'react';
import type { User } from '../types/api';
import type { Session } from '../services/auth';

export interface AuthContextValue {
  session: Session | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<User>;
  signOut: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
