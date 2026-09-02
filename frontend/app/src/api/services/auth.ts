/**
 * Auth API Service
 * Authentication endpoints
 */

import { api, setAccessToken } from '../client';
import type {
  AuthResponse,
  RegisterRequest,
  LoginRequest,
  RefreshResponse,
  User,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '../types';

export const authApi = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/register', data);
    setAccessToken(response.access_token);
    return response;
  },

  /**
   * Login with email and password
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', data);
    setAccessToken(response.access_token);
    return response;
  },

  /**
   * Get current user
   */
  async me(): Promise<{ user: User }> {
    return api.get<{ user: User }>('/auth/me');
  },

  /**
   * Refresh access token (uses HttpOnly cookie)
   */
  async refresh(): Promise<RefreshResponse> {
    const response = await api.post<RefreshResponse>('/auth/refresh');
    setAccessToken(response.access_token);
    return response;
  },

  /**
   * Logout (clears refresh cookie)
   */
  async logout(): Promise<void> {
    await api.post('/auth/logout');
    setAccessToken(null);
  },

  /**
   * Request password reset email
   */
  async forgotPassword(data: ForgotPasswordRequest): Promise<{ status: string }> {
    return api.post<{ status: string }>('/auth/password/forgot', data);
  },

  /**
   * Reset password with token
   */
  async resetPassword(data: ResetPasswordRequest): Promise<{ status: string }> {
    return api.post<{ status: string }>('/auth/password/reset', data);
  },

  /**
   * Get Google OAuth authorization URL
   */
  getGoogleAuthUrl(): string {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1';
    return `${baseUrl}/auth/oauth/google/authorize`;
  },
};
