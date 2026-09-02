/**
 * API Types
 * TypeScript types matching backend API responses
 */

// ============================================================================
// Common
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  next_cursor: string | null;
}

// ============================================================================
// Auth
// ============================================================================

export interface User {
  id: string;
  full_name: string;
  email: string;
  email_verified: boolean;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface RegisterRequest {
  email: string;
  full_name: string;
  password: string;
  password_confirm: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
  new_password_confirm: string;
}

// ============================================================================
// Projects
// ============================================================================

export type ProjectStatus = 'draft' | 'in_progress' | 'completed' | 'archived';

export interface ProjectScore {
  value: number;
  max: number;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  status: ProjectStatus;
  runs_count: number;
  latest_score: ProjectScore | null;
  latest_run_id: string | null;
  updated_at: string;
  created_at: string;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: ProjectStatus;
}

export interface ListProjectsParams {
  limit?: number;
  cursor?: string;
  q?: string;
  status?: ProjectStatus;
}

// ============================================================================
// Runs
// ============================================================================

export type DiagramType = 'class' | 'use_case';

export type DetailLevel = 'domain' | 'design';

export type RunPhaseStatus = 'running' | 'succeeded' | 'failed';

export interface DownloadArtifact {
  id: string;
  kind: string;
  content_type: string;
}

export interface RunDiagram {
  available: boolean;
  plantuml_source: string | null;
  preview_artifact_id: string | null;
  download_artifacts: DownloadArtifact[];
}

export interface RunOut {
  id: string;
  project_id: string;
  diagram_type: DiagramType;
  detail_level: DetailLevel;
  requirements_text: string;
  requirements_updated_at: string | null;
  validation_status: RunPhaseStatus | null;
  validation_score: number | null;
  validated_at: string | null;
  generation_status: RunPhaseStatus | null;
  generated_at: string | null;
  diagram: RunDiagram | null;
  created_at: string;
  updated_at: string;
}

export interface CreateRunRequest {
  requirements_text: string;
  diagram_type?: DiagramType;
  detail_level?: DetailLevel;
}

export interface UpdateRunRequest {
  requirements_text: string;
}

export interface ListRunsParams {
  limit?: number;
  cursor?: string;
}

// ============================================================================
// Run Results
// ============================================================================

export interface ResultMetric {
  name: string;
  label: string;
  score: number;
  max_score: number;
  source: string;
  description: string;
}

export type IssueSeverity = 'info' | 'warning' | 'error';

export interface ResultIssue {
  layer: string;
  category: string;
  severity: IssueSeverity;
  message: string;
  sentence_index: number;
  sentence_text: string;
  suggestion: string;
}

export interface ResultValidation {
  score: number;
  metrics: ResultMetric[];
  issues: ResultIssue[];
  feedback: string;
  can_generate: boolean;
  readability_grade: number;
  total_sentences: number;
  total_words: number;
}

export interface RunResult {
  run_id: string;
  project_id: string;
  validation: ResultValidation | null;
  diagram: RunDiagram | null;
}

// ============================================================================
// Account
// ============================================================================

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface DeleteAccountRequest {
  password: string;
  confirm_text: string;
}
