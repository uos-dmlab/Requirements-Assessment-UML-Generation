/**
 * Domain Types
 * Core business entities for the UML Generator application
 */

/**
 * Phase status for validation/generation
 */
export type PhaseStatus = 'running' | 'succeeded' | 'failed';

/**
 * Diagram type for a run
 */
export type DiagramType = 'class' | 'use_case';

export type DetailLevel = 'domain' | 'design';

export function formatDiagramType(type: DiagramType): string {
  return type === 'class' ? 'Class Diagram' : 'Use Case Diagram';
}

export function formatDetailLevel(level: DetailLevel): string {
  return level === 'domain' ? 'Domain Model' : 'Design Model';
}

/**
 * Project status indicators
 */
export type ProjectStatus = 'in_progress' | 'completed' | 'draft' | 'archived';

/**
 * Structured validation data from run result
 */
export interface ValidationData {
  score: { value: number; max: number };
  metrics: Array<{ key: string; label: string; value: number; max: number; tooltip?: string }>;
  summaryBadge: { level: 'success' | 'warning' | 'error'; text: string };
  feedback: Array<{ level: 'info' | 'warning' | 'error'; code: string; message: string }>;
}

/**
 * A workspace-based run
 */
export interface Run {
  id: string;
  projectId: string;
  diagramType: DiagramType;
  detailLevel: DetailLevel;
  requirementsText: string;
  requirementsUpdatedAt: string | null;
  validationStatus: PhaseStatus | null;
  validationScore: number | null;
  validatedAt: string | null;
  generationStatus: PhaseStatus | null;
  generatedAt: string | null;
  diagram: {
    available: boolean;
    plantumlSource: string | null;
    previewArtifactId: string | null;
    downloadArtifacts: Array<{ id: string; kind: string; contentType: string }>;
  } | null;
  createdAt: string;
  updatedAt: string;
  // Lazy-loaded from GET /runs/{id}/result
  resultLoaded?: boolean;
  validation?: ValidationData;
  diagramImageUrl?: string;
}

/**
 * A project containing multiple runs
 */
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  createdAt: string;
  updatedAt: string;
  runsCount: number;
  latestScore: { value: number; max: number } | null;
  latestRunId: string | null;
}

/**
 * Get status badge color classes
 */
export function getStatusColor(status: ProjectStatus): string {
  switch (status) {
    case 'completed':
      return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400';
    case 'in_progress':
      return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400';
    case 'draft':
      return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400';
    default:
      return 'bg-slate-100 text-slate-600';
  }
}

/**
 * Format status for display
 */
export function formatStatus(status: ProjectStatus): string {
  switch (status) {
    case 'completed':
      return 'Completed';
    case 'in_progress':
      return 'In Progress';
    case 'draft':
      return 'Draft';
    default:
      return status;
  }
}

/**
 * Get score quality level
 */
export function getScoreQuality(score: number, maxScore: number = 100): 'excellent' | 'good' | 'fair' | 'poor' {
  const percentage = score / maxScore;
  if (percentage >= 0.8) return 'excellent';
  if (percentage >= 0.6) return 'good';
  if (percentage >= 0.4) return 'fair';
  return 'poor';
}

/**
 * Get score color classes based on quality
 */
export function getScoreColor(score: number, maxScore: number = 100): string {
  const quality = getScoreQuality(score, maxScore);
  switch (quality) {
    case 'excellent':
      return 'text-emerald-600 dark:text-emerald-400';
    case 'good':
      return 'text-blue-600 dark:text-blue-400';
    case 'fair':
      return 'text-amber-600 dark:text-amber-400';
    case 'poor':
      return 'text-red-600 dark:text-red-400';
  }
}
