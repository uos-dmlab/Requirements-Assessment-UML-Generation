/**
 * Authentication Store
 * Manages user authentication state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import {
  authApi,
  accountApi,
  ApiException,
  setAccessToken,
} from '../api';
import type { User as ApiUser } from '../api';
import { useProjectStore } from './useProjectStore';

interface User {
  id: string;
  email: string;
  name: string;
  emailVerified?: boolean;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (email: string, password: string) => Promise<boolean>;
  register: (name: string, email: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
  clearError: () => void;
  changePassword: (currentPassword: string, newPassword: string) => Promise<boolean>;
  deleteAccount: (password: string, confirmText: string) => Promise<boolean>;
  initializeAuth: () => Promise<void>;
  getGoogleAuthUrl: () => string;
}

type AuthStore = AuthState & AuthActions;

function mapUser(apiUser: ApiUser): User {
  return {
    id: apiUser.id,
    email: apiUser.email,
    name: apiUser.full_name,
    emailVerified: apiUser.email_verified,
  };
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await authApi.login({ email, password });
          const user = mapUser(response.user);
          set({ user, isAuthenticated: true, isLoading: false, error: null });
          return true;
        } catch (error) {
          const message =
            error instanceof ApiException
              ? error.message
              : 'Login failed. Please try again.';
          set({ isLoading: false, error: message });
          return false;
        }
      },

      register: async (name: string, email: string, password: string) => {
        set({ isLoading: true, error: null });

        try {
          const response = await authApi.register({
            email,
            full_name: name,
            password,
            password_confirm: password,
          });
          const user = mapUser(response.user);
          set({ user, isAuthenticated: true, isLoading: false, error: null });
          return true;
        } catch (error) {
          const message =
            error instanceof ApiException
              ? error.message
              : 'Registration failed. Please try again.';
          set({ isLoading: false, error: message });
          return false;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch {
          // Ignore logout errors
        } finally {
          setAccessToken(null);
          useProjectStore.getState().reset();
          set({ user: null, isAuthenticated: false, error: null });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      changePassword: async (currentPassword: string, newPassword: string) => {
        set({ isLoading: true, error: null });

        try {
          await accountApi.changePassword({
            current_password: currentPassword,
            new_password: newPassword,
            new_password_confirm: newPassword,
          });
          set({ isLoading: false, error: null });
          return true;
        } catch (error) {
          const message =
            error instanceof ApiException
              ? error.message
              : 'Failed to change password. Please try again.';
          set({ isLoading: false, error: message });
          return false;
        }
      },

      deleteAccount: async (password: string, confirmText: string) => {
        set({ isLoading: true, error: null });

        try {
          await accountApi.deleteAccount({
            password,
            confirm_text: confirmText,
          });
          setAccessToken(null);
          set({ user: null, isAuthenticated: false, isLoading: false, error: null });
          return true;
        } catch (error) {
          const message =
            error instanceof ApiException
              ? error.message
              : 'Failed to delete account. Please try again.';
          set({ isLoading: false, error: message });
          return false;
        }
      },

      initializeAuth: async () => {
        const { isAuthenticated } = get();
        if (!isAuthenticated) return;

        try {
          await authApi.refresh();
          const { user: apiUser } = await authApi.me();
          const user = mapUser(apiUser);
          set({ user, isAuthenticated: true });
        } catch {
          setAccessToken(null);
          set({ user: null, isAuthenticated: false });
        }
      },

      getGoogleAuthUrl: () => {
        return authApi.getGoogleAuthUrl();
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
