/**
 * User domain types and zustand store
 */
import {create} from 'zustand';
import {persist} from 'zustand/middleware';
import type { UserResponse } from '@/shared/api'

interface UserState {
  user: UserResponse | null;
  setUser: (u: UserResponse | null) => void;
  token: string | null;
  setToken: (t: string | null) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({user}),
      setToken: (token) => set({token}),
      logout: () => {
        localStorage.clear()
        set({user: null, token: null})
      },
    }),
    {
      name: 'user-store',
      partialize: (state) => ({user: state.user, token: state.token}),
    },
  ),
);
