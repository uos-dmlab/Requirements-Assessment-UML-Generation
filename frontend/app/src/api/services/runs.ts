/**
 * Runs API Service
 * Workspace-based run endpoints
 */

import { api } from '../client';
import type {
  RunOut,
  RunResult,
  CreateRunRequest,
  UpdateRunRequest,
  PaginatedResponse,
  ListRunsParams,
} from '../types';

export const runsApi = {
  /**
   * List runs for a project
   */
  async list(projectId: string, params?: ListRunsParams): Promise<PaginatedResponse<RunOut>> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.set('limit', String(params.limit));
    if (params?.cursor) searchParams.set('cursor', params.cursor);

    const query = searchParams.toString();
    return api.get<PaginatedResponse<RunOut>>(
      `/projects/${projectId}/runs${query ? `?${query}` : ''}`
    );
  },

  /**
   * Create a new run
   */
  async create(projectId: string, data: CreateRunRequest): Promise<RunOut> {
    return api.post<RunOut>(`/projects/${projectId}/runs`, data);
  },

  /**
   * Get a run by ID
   */
  async get(runId: string): Promise<RunOut> {
    return api.get<RunOut>(`/runs/${runId}`);
  },

  /**
   * Update run requirements text
   */
  async update(runId: string, data: UpdateRunRequest): Promise<RunOut> {
    return api.patch<RunOut>(`/runs/${runId}`, data);
  },

  /**
   * Delete a run
   */
  async delete(runId: string): Promise<void> {
    return api.delete(`/runs/${runId}`);
  },

  /**
   * Trigger validation for a run
   */
  async validate(runId: string): Promise<RunOut> {
    return api.post<RunOut>(`/runs/${runId}/validate`);
  },

  /**
   * Trigger generation for a run
   */
  async generate(runId: string): Promise<RunOut> {
    return api.post<RunOut>(`/runs/${runId}/generate`);
  },

  /**
   * Get run result (validation scores + diagram)
   */
  async getResult(runId: string): Promise<RunResult> {
    return api.get<RunResult>(`/runs/${runId}/result`);
  },

  /**
   * Poll run until no phase is 'running'
   */
  async pollUntilSettled(
    runId: string,
    options?: {
      intervalMs?: number;
      timeoutMs?: number;
      maxErrors?: number;
      signal?: AbortSignal;
      onProgress?: (run: RunOut) => void;
    }
  ): Promise<RunOut> {
    const { intervalMs = 1500, timeoutMs = 300000, maxErrors = 5, signal, onProgress } = options || {};
    const startTime = Date.now();
    let consecutiveErrors = 0;

    while (true) {
      if (signal?.aborted) {
        throw new Error('Polling aborted');
      }

      let run: RunOut;
      try {
        run = await this.get(runId);
        consecutiveErrors = 0;
      } catch (error) {
        consecutiveErrors++;
        if (consecutiveErrors >= maxErrors) {
          throw error;
        }
        await new Promise((resolve) => setTimeout(resolve, intervalMs));
        continue;
      }

      if (onProgress) {
        onProgress(run);
      }

      if (run.validation_status !== 'running' && run.generation_status !== 'running') {
        return run;
      }

      if (Date.now() - startTime > timeoutMs) {
        throw new Error('Run timed out');
      }

      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
  },
};
