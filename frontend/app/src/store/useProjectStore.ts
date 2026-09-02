/**
 * Project Store
 * Centralized state management using Zustand
 * Projects and workspace-based runs synced with backend API
 */

import { create } from 'zustand';
import type { Project, Run, DiagramType, DetailLevel } from '../types';
import { projectsApi, runsApi, artifactsApi, ApiException } from '../api';
import type { Project as ApiProject } from '../api';
import { mapApiRunToRun, mapRunResultToValidation } from '../utils/mappers';

// ---------------------------------------------------------------------------
// Polling abort — per-run AbortControllers
// ---------------------------------------------------------------------------

const pollingAborts = new Map<string, AbortController>();

function abortPolling(runId: string) {
  pollingAborts.get(runId)?.abort();
  pollingAborts.delete(runId);
}

function abortAllPolling() {
  for (const controller of pollingAborts.values()) {
    controller.abort();
  }
  pollingAborts.clear();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mapApiProject(p: ApiProject): Project {
  return {
    id: p.id,
    name: p.name,
    description: p.description ?? undefined,
    status: p.status,
    createdAt: p.created_at,
    updatedAt: p.updated_at,
    runsCount: p.runs_count,
    latestScore: p.latest_score,
    latestRunId: p.latest_run_id,
  };
}

function errorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiException) return error.message;
  if (error instanceof Error) return error.message;
  return fallback;
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ProjectState {
  // Data
  projects: Project[];
  selectedProjectId: string | null;
  selectedRunId: string | null;
  isLoading: boolean;
  error: string | null;

  // Per-project run cache
  runsByProject: Record<string, Run[]>;

  // API Actions — projects
  fetchProjects: () => Promise<void>;
  addProject: (name: string, description?: string) => Promise<Project | null>;
  deleteProject: (id: string) => Promise<void>;

  // API Actions — runs
  fetchRuns: (projectId: string) => Promise<void>;
  createRun: (projectId: string, requirementsText: string, diagramType?: DiagramType, detailLevel?: DetailLevel) => Promise<Run | null>;
  updateRunRequirements: (runId: string, text: string) => Promise<void>;
  validateRun: (runId: string) => Promise<void>;
  generateRun: (runId: string) => Promise<void>;
  deleteRun: (runId: string) => Promise<void>;
  fetchRunResult: (runId: string) => Promise<void>;

  // Local Actions
  selectProject: (id: string | null) => void;
  selectRun: (id: string | null) => void;
  updateProject: (id: string, updates: Partial<Project>) => void;
  reset: () => void;
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------

export const useProjectStore = create<ProjectState>()((set, get) => ({
  projects: [],
  selectedProjectId: null,
  selectedRunId: null,
  isLoading: false,
  error: null,
  runsByProject: {},

  // -----------------------------------------------------------------------
  // Projects
  // -----------------------------------------------------------------------

  fetchProjects: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await projectsApi.list({ limit: 100 });
      set({
        projects: response.items.map(mapApiProject),
        isLoading: false,
      });
    } catch (error) {
      set({ isLoading: false, error: errorMessage(error, 'Failed to load projects') });
    }
  },

  addProject: async (name, description) => {
    try {
      const apiProject = await projectsApi.create({ name, description });
      const project = mapApiProject(apiProject);
      set((state) => ({
        projects: [project, ...state.projects],
      }));
      get().selectProject(project.id);
      return project;
    } catch (error) {
      set({ error: errorMessage(error, 'Failed to create project') });
      return null;
    }
  },

  deleteProject: async (id) => {
    try {
      await projectsApi.delete(id);
      set((state) => {
        const { [id]: _runs, ...restRuns } = state.runsByProject;
        return {
          projects: state.projects.filter((p) => p.id !== id),
          selectedProjectId:
            state.selectedProjectId === id ? null : state.selectedProjectId,
          selectedRunId:
            state.selectedProjectId === id ? null : state.selectedRunId,
          runsByProject: restRuns,
        };
      });
    } catch (error) {
      set({ error: errorMessage(error, 'Failed to delete project') });
    }
  },

  // -----------------------------------------------------------------------
  // Runs
  // -----------------------------------------------------------------------

  fetchRuns: async (projectId) => {
    try {
      const response = await runsApi.list(projectId, { limit: 50 });
      const existingRuns = get().runsByProject[projectId] ?? [];

      // Merge: keep any locally-enriched runs (with resultLoaded data)
      const enrichedById = new Map(
        existingRuns.filter((r) => r.resultLoaded).map((r) => [r.id, r])
      );

      const runs = response.items.map((apiRun) => {
        const mapped = mapApiRunToRun(apiRun);
        const enriched = enrichedById.get(mapped.id);
        return enriched
          ? { ...mapped, resultLoaded: enriched.resultLoaded, validation: enriched.validation, diagramImageUrl: enriched.diagramImageUrl }
          : mapped;
      });

      set((state) => ({
        runsByProject: { ...state.runsByProject, [projectId]: runs },
      }));
    } catch (error) {
      set({ error: errorMessage(error, 'Failed to load runs') });
    }
  },

  createRun: async (projectId, requirementsText, diagramType, detailLevel) => {
    set({ error: null });
    try {
      const apiRun = await runsApi.create(projectId, { requirements_text: requirementsText, diagram_type: diagramType, detail_level: detailLevel });
      const run = mapApiRunToRun(apiRun);

      set((state) => {
        const existing = state.runsByProject[projectId] ?? [];
        return {
          runsByProject: {
            ...state.runsByProject,
            [projectId]: [run, ...existing],
          },
          selectedRunId: run.id,
        };
      });

      return run;
    } catch (error) {
      set({ error: errorMessage(error, 'Failed to create run') });
      return null;
    }
  },

  updateRunRequirements: async (runId, text) => {
    set({ error: null });
    try {
      const apiRun = await runsApi.update(runId, { requirements_text: text });
      const updated = mapApiRunToRun(apiRun);

      set((state) => {
        const newRunsByProject = { ...state.runsByProject };
        for (const [pid, runs] of Object.entries(newRunsByProject)) {
          const idx = runs.findIndex((r) => r.id === runId);
          if (idx !== -1) {
            const updatedRuns = [...runs];
            // Reset result data since requirements changed
            updatedRuns[idx] = { ...updated, resultLoaded: false };
            newRunsByProject[pid] = updatedRuns;
            break;
          }
        }
        return { runsByProject: newRunsByProject };
      });
    } catch (error) {
      set({ error: errorMessage(error, 'Failed to save requirements') });
    }
  },

  validateRun: async (runId) => {
    set({ error: null });

    // Abort any previous polling for this run
    abortPolling(runId);
    const controller = new AbortController();
    pollingAborts.set(runId, controller);

    try {
      // Trigger validation
      const apiRun = await runsApi.validate(runId);
      const run = mapApiRunToRun(apiRun);

      // Update run in store immediately (validation_status = 'running')
      _updateRunInStore(set, get, runId, run);

      // Poll until settled
      const finalApiRun = await runsApi.pollUntilSettled(runId, {
        signal: controller.signal,
        onProgress: (progressRun) => {
          _updateRunInStore(set, get, runId, mapApiRunToRun(progressRun));
        },
      });

      const finalRun = mapApiRunToRun(finalApiRun);
      _updateRunInStore(set, get, runId, { ...finalRun, resultLoaded: false });

      // Auto-fetch result on success
      if (finalApiRun.validation_status === 'succeeded') {
        await get().fetchRunResult(runId);
      }

      // Refresh project summary
      _refreshProject(set, get, finalRun.projectId);
    } catch (error) {
      if (controller.signal.aborted) return;
      set({ error: errorMessage(error, 'Validation failed') });
    } finally {
      pollingAborts.delete(runId);
    }
  },

  generateRun: async (runId) => {
    set({ error: null });

    abortPolling(runId);
    const controller = new AbortController();
    pollingAborts.set(runId, controller);

    try {
      const apiRun = await runsApi.generate(runId);
      const run = mapApiRunToRun(apiRun);
      _updateRunInStore(set, get, runId, run);

      const finalApiRun = await runsApi.pollUntilSettled(runId, {
        signal: controller.signal,
        onProgress: (progressRun) => {
          _updateRunInStore(set, get, runId, mapApiRunToRun(progressRun));
        },
      });

      const finalRun = mapApiRunToRun(finalApiRun);
      _updateRunInStore(set, get, runId, { ...finalRun, resultLoaded: false });

      if (finalApiRun.generation_status === 'succeeded') {
        await get().fetchRunResult(runId);
      }

      _refreshProject(set, get, finalRun.projectId);
    } catch (error) {
      if (controller.signal.aborted) return;
      set({ error: errorMessage(error, 'Generation failed') });
    } finally {
      pollingAborts.delete(runId);
    }
  },

  deleteRun: async (runId) => {
    try {
      abortPolling(runId);
      await runsApi.delete(runId);

      set((state) => {
        const newRunsByProject = { ...state.runsByProject };
        let newSelectedRunId = state.selectedRunId;

        for (const [pid, runs] of Object.entries(newRunsByProject)) {
          const idx = runs.findIndex((r) => r.id === runId);
          if (idx !== -1) {
            const updatedRuns = runs.filter((r) => r.id !== runId);
            newRunsByProject[pid] = updatedRuns;

            // Auto-select adjacent run if deleted run was selected
            if (state.selectedRunId === runId) {
              if (updatedRuns.length > 0) {
                const nextIdx = Math.min(idx, updatedRuns.length - 1);
                newSelectedRunId = updatedRuns[nextIdx].id;
              } else {
                newSelectedRunId = null;
              }
            }
            break;
          }
        }

        return {
          runsByProject: newRunsByProject,
          selectedRunId: newSelectedRunId,
        };
      });
    } catch (error) {
      set({ error: errorMessage(error, 'Failed to delete run') });
    }
  },

  fetchRunResult: async (runId) => {
    try {
      const result = await runsApi.getResult(runId);
      const validation = mapRunResultToValidation(result);

      let diagramImageUrl: string | undefined;
      // Get diagram image from the run's diagram data (already in RunOut),
      // but also check result.diagram for preview artifact
      const diagramData = result.diagram;
      if (diagramData?.preview_artifact_id) {
        try {
          diagramImageUrl = await artifactsApi.getObjectUrl(
            diagramData.preview_artifact_id
          );
        } catch {
          // diagram download failed — continue without it
        }
      }

      set((state) => {
        const newRunsByProject = { ...state.runsByProject };
        for (const [pid, runs] of Object.entries(newRunsByProject)) {
          const idx = runs.findIndex((r) => r.id === runId);
          if (idx !== -1) {
            const updated = [...runs];
            updated[idx] = {
              ...updated[idx],
              validation: validation ?? undefined,
              diagramImageUrl,
              resultLoaded: true,
            };
            newRunsByProject[pid] = updated;
            break;
          }
        }
        return { runsByProject: newRunsByProject };
      });
    } catch (error) {
      // Mark resultLoaded so the UI doesn't keep retrying
      set((state) => {
        const newRunsByProject = { ...state.runsByProject };
        for (const [pid, runs] of Object.entries(newRunsByProject)) {
          const idx = runs.findIndex((r) => r.id === runId);
          if (idx !== -1) {
            const updated = [...runs];
            updated[idx] = { ...updated[idx], resultLoaded: true };
            newRunsByProject[pid] = updated;
            break;
          }
        }
        return {
          runsByProject: newRunsByProject,
          error: errorMessage(error, 'Failed to load run result'),
        };
      });
    }
  },

  // -----------------------------------------------------------------------
  // Local actions
  // -----------------------------------------------------------------------

  selectProject: (id) => {
    set({ selectedProjectId: id, selectedRunId: null, error: null });

    if (id) {
      const state = get();
      // Fetch runs if not cached
      if (!state.runsByProject[id]) {
        state.fetchRuns(id).then(() => {
          // Auto-select first run
          const runs = get().runsByProject[id];
          if (runs && runs.length > 0) {
            get().selectRun(runs[0].id);
          }
        });
      } else {
        // Auto-select first run from cache
        const runs = state.runsByProject[id];
        if (runs && runs.length > 0) {
          set({ selectedRunId: runs[0].id });
        }
      }
    }
  },

  selectRun: (id) => {
    set({ selectedRunId: id, error: null });

    if (id) {
      // Lazy-load result if run has succeeded validation/generation and result not loaded
      const state = get();
      for (const runs of Object.values(state.runsByProject)) {
        const run = runs.find((r) => r.id === id);
        if (run && !run.resultLoaded &&
            (run.validationStatus === 'succeeded' || run.generationStatus === 'succeeded')) {
          state.fetchRunResult(id);
        }
      }
    }
  },

  updateProject: (id, updates) => {
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === id
          ? { ...p, ...updates, updatedAt: new Date().toISOString() }
          : p
      ),
    }));
  },

  reset: () => {
    abortAllPolling();

    // Revoke any blob URLs
    const state = get();
    for (const runs of Object.values(state.runsByProject)) {
      for (const run of runs) {
        if (run.diagramImageUrl?.startsWith('blob:')) {
          URL.revokeObjectURL(run.diagramImageUrl);
        }
      }
    }

    set({
      projects: [],
      selectedProjectId: null,
      selectedRunId: null,
      isLoading: false,
      error: null,
      runsByProject: {},
    });
  },
}));

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

type SetFn = (fn: (state: ProjectState) => Partial<ProjectState>) => void;
type GetFn = () => ProjectState;

function _updateRunInStore(set: SetFn, _get: GetFn, runId: string, updates: Partial<Run>) {
  set((state) => {
    const newRunsByProject = { ...state.runsByProject };
    for (const [pid, runs] of Object.entries(newRunsByProject)) {
      const idx = runs.findIndex((r) => r.id === runId);
      if (idx !== -1) {
        const updated = [...runs];
        updated[idx] = { ...updated[idx], ...updates };
        newRunsByProject[pid] = updated;
        break;
      }
    }
    return { runsByProject: newRunsByProject };
  });
}

async function _refreshProject(set: SetFn, _get: GetFn, projectId: string) {
  try {
    const apiProject = await projectsApi.get(projectId);
    const updated = mapApiProject(apiProject);
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === projectId ? { ...p, ...updated } : p
      ),
    }));
  } catch {
    // non-critical
  }
}

// ---------------------------------------------------------------------------
// Selector hooks
// ---------------------------------------------------------------------------

export const useProjects = () => useProjectStore((state) => state.projects);

export const useSelectedProjectId = () =>
  useProjectStore((state) => state.selectedProjectId);

export const useSelectedProject = () => {
  const projects = useProjectStore((state) => state.projects);
  const selectedId = useProjectStore((state) => state.selectedProjectId);
  return projects.find((p) => p.id === selectedId) || null;
};

export const useSelectedProjectRuns = (): Run[] => {
  const runsByProject = useProjectStore((state) => state.runsByProject);
  const selectedId = useProjectStore((state) => state.selectedProjectId);
  if (!selectedId) return [];
  return runsByProject[selectedId] ?? [];
};

export const useSelectedRun = (): Run | null => {
  const runsByProject = useProjectStore((state) => state.runsByProject);
  const selectedProjectId = useProjectStore((state) => state.selectedProjectId);
  const selectedRunId = useProjectStore((state) => state.selectedRunId);
  if (!selectedProjectId || !selectedRunId) return null;
  const runs = runsByProject[selectedProjectId] ?? [];
  return runs.find((r) => r.id === selectedRunId) ?? null;
};
