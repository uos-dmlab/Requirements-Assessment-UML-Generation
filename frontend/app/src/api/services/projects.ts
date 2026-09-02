/**
 * Projects API Service
 * Project management endpoints
 */

import { api } from '../client';
import type {
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  PaginatedResponse,
  ListProjectsParams,
} from '../types';

export const projectsApi = {
  /**
   * List user's projects
   */
  async list(params?: ListProjectsParams): Promise<PaginatedResponse<Project>> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.cursor) searchParams.set('cursor', params.cursor);
    if (params?.q) searchParams.set('q', params.q);
    if (params?.status) searchParams.set('status', params.status);

    const query = searchParams.toString();
    return api.get<PaginatedResponse<Project>>(`/projects${query ? `?${query}` : ''}`);
  },

  /**
   * Create a new project
   */
  async create(data: CreateProjectRequest): Promise<Project> {
    return api.post<Project>('/projects', data);
  },

  /**
   * Get a project by ID
   */
  async get(projectId: string): Promise<Project> {
    return api.get<Project>(`/projects/${projectId}`);
  },

  /**
   * Update a project
   */
  async update(projectId: string, data: UpdateProjectRequest): Promise<Project> {
    return api.patch<Project>(`/projects/${projectId}`, data);
  },

  /**
   * Delete a project
   */
  async delete(projectId: string): Promise<void> {
    return api.delete(`/projects/${projectId}`);
  },
};
