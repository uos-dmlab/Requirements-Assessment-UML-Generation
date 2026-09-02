/**
 * Artifacts API Service
 * Download generated artifacts (diagrams, etc.)
 */

import { getAccessToken } from '../client';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const artifactsApi = {
  /**
   * Get artifact download URL
   */
  getDownloadUrl(artifactId: string): string {
    return `${API_BASE_URL}/artifacts/${artifactId}`;
  },

  /**
   * Download artifact as blob
   */
  async download(artifactId: string): Promise<Blob> {
    const token = getAccessToken();
    const response = await fetch(`${API_BASE_URL}/artifacts/${artifactId}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Failed to download artifact: ${response.status}`);
    }

    return response.blob();
  },

  /**
   * Download artifact and create object URL
   */
  async getObjectUrl(artifactId: string): Promise<string> {
    const blob = await this.download(artifactId);
    return URL.createObjectURL(blob);
  },

  /**
   * Download artifact and trigger browser download
   */
  async downloadToFile(artifactId: string, filename: string): Promise<void> {
    const blob = await this.download(artifactId);
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    URL.revokeObjectURL(url);
  },
};
