/**
 * Account API Service
 * User account management endpoints
 */

import { api, setAccessToken } from '../client';
import type { ChangePasswordRequest, DeleteAccountRequest } from '../types';

export const accountApi = {
  /**
   * Change user password
   * Note: All refresh tokens are revoked after password change
   */
  async changePassword(data: ChangePasswordRequest): Promise<{ status: string }> {
    return api.post<{ status: string }>('/account/password/change', data);
  },

  /**
   * Delete user account
   */
  async deleteAccount(data: DeleteAccountRequest): Promise<{ status: string }> {
    const response = await api.post<{ status: string }>('/account/delete', data);
    setAccessToken(null);
    return response;
  },
};
