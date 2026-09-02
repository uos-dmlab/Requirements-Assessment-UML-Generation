/**
 * Mappers — convert API types to domain types
 */

import type { RunOut, RunResult } from '../api/types';
import type { Run, ValidationData } from '../types';

/**
 * Map an API RunOut to the domain Run used by UI components.
 */
export function mapApiRunToRun(apiRun: RunOut): Run {
  return {
    id: apiRun.id,
    projectId: apiRun.project_id,
    diagramType: apiRun.diagram_type,
    detailLevel: apiRun.detail_level,
    requirementsText: apiRun.requirements_text,
    requirementsUpdatedAt: apiRun.requirements_updated_at,
    validationStatus: apiRun.validation_status,
    validationScore: apiRun.validation_score,
    validatedAt: apiRun.validated_at,
    generationStatus: apiRun.generation_status,
    generatedAt: apiRun.generated_at,
    diagram: apiRun.diagram
      ? {
          available: apiRun.diagram.available,
          plantumlSource: apiRun.diagram.plantuml_source,
          previewArtifactId: apiRun.diagram.preview_artifact_id,
          downloadArtifacts: apiRun.diagram.download_artifacts.map((a) => ({
            id: a.id,
            kind: a.kind,
            contentType: a.content_type,
          })),
        }
      : null,
    createdAt: apiRun.created_at,
    updatedAt: apiRun.updated_at,
  };
}

/** Backend total score is always out of 100. */
const MAX_TOTAL_SCORE = 100;

/**
 * Derive a summary badge from the score percentage.
 */
function deriveSummaryBadge(score: number, maxScore: number): ValidationData['summaryBadge'] {
  const pct = maxScore > 0 ? score / maxScore : 0;
  if (pct >= 0.8) return { level: 'success', text: 'Excellent' };
  if (pct >= 0.6) return { level: 'warning', text: 'Needs Improvement' };
  return { level: 'error', text: 'Significant Issues' };
}

/**
 * Metric display overrides: rename labels, add tooltips, invert scores.
 */
const METRIC_CONFIG: Record<string, { label: string; tooltip: string }> = {
  vagueness: {
    label: 'Specificity',
    tooltip: "Measures absence of vague terms like 'some', 'many', 'quickly', 'appropriate', 'etc.'",
  },
  completeness_markers: {
    label: 'Modal Strength',
    tooltip: 'Presence of strong modal verbs (shall, must, will) that clearly define requirements.',
  },
  clarity: {
    label: 'Clarity',
    tooltip: 'Simple, understandable language without jargon or overly complex sentences.',
  },
  structure: {
    label: 'Structure',
    tooltip: "Requirements follow Subject-Verb-Object pattern: 'The user clicks the button' rather than passive voice.",
  },
  readability: {
    label: 'Readability',
    tooltip: 'Sentence length and complexity. Shorter sentences score higher.',
  },
  modelability: {
    label: 'Modelability',
    tooltip: 'Contains concrete nouns, verbs, and attributes that can be extracted into UML elements.',
  },
  completeness: {
    label: 'Completeness',
    tooltip: 'All necessary details are specified: actors, attributes, relationships, constraints.',
  },
  consistency: {
    label: 'Consistency',
    tooltip: 'Same terms used throughout. No contradictions between requirements.',
  },
};

/**
 * Extract ValidationData from a RunResult.
 * Returns null if result has no validation data.
 */
export function mapRunResultToValidation(result: RunResult): ValidationData | null {
  if (!result.validation) return null;

  const v = result.validation;
  const metrics = v.metrics ?? [];

  return {
    score: { value: v.score, max: MAX_TOTAL_SCORE },
    metrics: metrics.map((m) => {
      const config = METRIC_CONFIG[m.name];
      return {
        key: m.name,
        label: config?.label ?? m.label,
        value: m.score,
        max: m.max_score,
        tooltip: config?.tooltip,
      };
    }),
    summaryBadge: deriveSummaryBadge(v.score, MAX_TOTAL_SCORE),
    feedback: (v.issues ?? []).map((issue) => ({
      level: issue.severity === 'error' ? 'error' as const
        : issue.severity === 'warning' ? 'warning' as const
        : 'info' as const,
      code: issue.category,
      message: issue.suggestion || issue.message,
    })),
  };
}
