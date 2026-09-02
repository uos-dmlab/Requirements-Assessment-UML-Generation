/**
 * UmlGeneratorPage
 * Main application page that orchestrates the 3-column layout
 * and wires store actions for workspace-based runs.
 */

import { useCallback } from 'react';

// Store
import {
  useProjectStore,
  useProjects,
  useSelectedProject,
  useSelectedProjectRuns,
  useSelectedRun,
} from '../store/useProjectStore';
import type { DiagramType, DetailLevel } from '../types';

// Components
import { AppLayout } from '../components/layout';
import { RunsSidebar } from '../components/sidebar';
import { RequirementsEditor } from '../components/requirements';
import { ResultsPanel } from '../components/results';

interface UmlGeneratorPageProps {
  onOpenSettings?: () => void;
}

export function UmlGeneratorPage({ onOpenSettings }: UmlGeneratorPageProps) {
  // Store selectors
  const projects = useProjects();
  const selectedProject = useSelectedProject();
  const runs = useSelectedProjectRuns();
  const selectedRun = useSelectedRun();

  const {
    selectProject,
    addProject,
    deleteProject,
    selectRun,
    createRun,
    updateRunRequirements,
    validateRun,
    generateRun,
    deleteRun,
    error,
  } = useProjectStore();

  // --- Sidebar handlers ---

  const handleSelectProject = useCallback(
    (projectId: string) => {
      selectProject(projectId);
    },
    [selectProject]
  );

  const handleCreateProject = useCallback(
    async (name: string, description?: string) => {
      await addProject(name, description);
    },
    [addProject]
  );

  const handleDeleteProject = useCallback(
    (projectId: string) => {
      deleteProject(projectId);
    },
    [deleteProject]
  );

  const handleSelectRun = useCallback(
    (runId: string) => {
      selectRun(runId);
    },
    [selectRun]
  );

  const handleCreateRun = useCallback((diagramType: DiagramType, detailLevel?: DetailLevel) => {
    if (!selectedProject) return;
    createRun(selectedProject.id, '', diagramType, detailLevel);
  }, [selectedProject, createRun]);

  const handleDeleteRun = useCallback(
    (runId: string) => {
      deleteRun(runId);
    },
    [deleteRun]
  );

  // --- Editor handlers ---

  const handleSave = useCallback(
    (text: string) => {
      if (!selectedRun) return;
      updateRunRequirements(selectedRun.id, text);
    },
    [selectedRun, updateRunRequirements]
  );

  const handleValidate = useCallback(() => {
    if (!selectedRun) return;
    validateRun(selectedRun.id);
  }, [selectedRun, validateRun]);

  const handleGenerate = useCallback(() => {
    if (!selectedRun) return;
    generateRun(selectedRun.id);
  }, [selectedRun, generateRun]);

  return (
    <AppLayout
      onOpenSettings={onOpenSettings}
      sidebar={
        <RunsSidebar
          projects={projects}
          selectedProject={selectedProject}
          runs={runs}
          selectedRunId={selectedRun?.id ?? null}
          onSelectProject={handleSelectProject}
          onCreateProject={handleCreateProject}
          onDeleteProject={handleDeleteProject}
          onSelectRun={handleSelectRun}
          onCreateRun={handleCreateRun}
          onDeleteRun={handleDeleteRun}
        />
      }
      main={
        <RequirementsEditor
          project={selectedProject}
          selectedRun={selectedRun}
          onSave={handleSave}
          onValidate={handleValidate}
          onGenerate={handleGenerate}
          error={error}
        />
      }
      panel={
        <ResultsPanel
          project={selectedProject}
          selectedRun={selectedRun}
        />
      }
    />
  );
}
