/**
 * User domain types and zustand store
 */
import {create} from 'zustand';
import {UserResponse} from '@/shared/api/client/testConstructorAPI.schemas';

interface UserState {
  user: UserResponse | null;
  setUser: (u: UserResponse | null) => void;
  token: string | null;
  setToken: (t: string | null) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  token: localStorage.getItem('access_token'),
  setUser: (user) => set({user}),
  setToken: (token) => {
    if (token) localStorage.setItem('access_token', token);
    else localStorage.removeItem('access_token');
    set({token});
  },
  logout: () => {
    localStorage.removeItem('access_token');
    set({user: null, token: null});
  },
}));
