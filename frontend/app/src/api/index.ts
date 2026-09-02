/**
 * API Layer - Main Exports
 *
 * This file serves as the single integration point for backend communication.
 */

// Client utilities
export {
  api,
  ApiException,
  setAccessToken,
  getAccessToken,
  refreshAccessToken,
  authenticatedRequest,
} from './client';

// API Services
export {
  authApi,
  projectsApi,
  runsApi,
  artifactsApi,
  accountApi,
} from './services';

// Types
export type {
  // Common
  PaginatedResponse,
  // Auth
  User,
  AuthResponse,
  RegisterRequest,
  LoginRequest,
  RefreshResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  // Projects
  ProjectStatus,
  ProjectScore,
  Project,
  CreateProjectRequest,
  UpdateProjectRequest,
  ListProjectsParams,
  // Runs
  DiagramType,
  DetailLevel,
  RunPhaseStatus,
  DownloadArtifact,
  RunDiagram,
  RunOut,
  CreateRunRequest,
  UpdateRunRequest,
  ListRunsParams,
  // Run Results
  ResultMetric,
  IssueSeverity,
  ResultIssue,
  ResultValidation,
  RunResult,
  // Account
  ChangePasswordRequest,
  DeleteAccountRequest,
} from './types';
