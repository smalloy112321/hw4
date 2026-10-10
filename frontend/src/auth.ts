import { createContext, useContext } from 'react'
import type * as api from './api'

export type AuthState = {
  user: api.User | null
  loading: boolean
  login: (email: string, password: string) => Promise<api.User>
  register: (input: api.RegisterInput) => Promise<api.User>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
