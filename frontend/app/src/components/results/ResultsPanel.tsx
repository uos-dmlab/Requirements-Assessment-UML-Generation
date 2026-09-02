/**
 * ResultsPanel Component
 * Right column displaying validation and generation results
 */

import React from 'react';
import { Clipboard, FileText, Loader2, AlertCircle } from 'lucide-react';
import type { Run, Project } from '../../types';
import { ScrollArea } from '../ui';
import { ScoreCard } from './ScoreCard';
import { FeedbackCard } from './FeedbackCard';
import { DiagramSection } from './DiagramSection';

interface ResultsPanelProps {
  project: Project | null;
  selectedRun: Run | null;
}

export function ResultsPanel({ project, selectedRun }: ResultsPanelProps) {

  // No project selected
  if (!project) {
    return (
      <aside className="h-full flex flex-col bg-slate-50 dark:bg-slate-900 border-l border-border">
        <div className="border-b border-border p-4">
          <h2 className="text-lg font-semibold">Results</h2>
        </div>
        <EmptyState
          icon={<Clipboard className="w-8 h-8" />}
          title="Select a Project"
          description="Choose a project from the sidebar to see its validation and generation results."
        />
      </aside>
    );
  }

  // No run selected
  if (!selectedRun) {
    return (
      <aside className="h-full flex flex-col bg-slate-50 dark:bg-slate-900 border-l border-border">
        <div className="border-b border-border p-4">
          <h2 className="text-lg font-semibold">Results</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{project.name}</p>
        </div>
        <EmptyState
          icon={<FileText className="w-8 h-8" />}
          title="No Run Selected"
          description="Select or create a run to see validation scores, feedback, and diagrams."
        />
      </aside>
    );
  }

  return (
    <aside className="h-full flex flex-col bg-slate-50 dark:bg-slate-900 border-l border-border">
      {/* Header */}
      <div className="border-b border-border p-4">
        <h2 className="text-lg font-semibold">Results</h2>
        <p className="text-sm text-muted-foreground mt-0.5">{project.name}</p>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          {/* === Validation Section === */}
          <ValidationSection run={selectedRun} />

          {/* === Diagram/Generation Section === */}
          <GenerationSection run={selectedRun} projectName={project.name} />
        </div>
      </ScrollArea>
    </aside>
  );
}

/**
 * Validation section: spinner / results / error / empty
 */
function ValidationSection({ run }: { run: Run }) {
  if (run.validationStatus === 'running') {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Validating...</p>
        </div>
      </div>
    );
  }

  if (run.validationStatus === 'failed') {
    return (
      <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">
        <AlertCircle className="w-4 h-4 flex-shrink-0" />
        Validation failed. Please try again.
      </div>
    );
  }

  if (run.validationStatus === 'succeeded') {
    // Still loading result data
    if (!run.resultLoaded) {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading results...</p>
          </div>
        </div>
      );
    }

    if (run.validation) {
      return (
        <>
          <ScoreCard validation={run.validation} />
          <FeedbackCard feedback={run.validation.feedback} />
        </>
      );
    }
  }

  // No validation run yet
  return null;
}

/**
 * Generation/Diagram section: spinner / diagram / error / empty
 */
function GenerationSection({ run, projectName }: { run: Run; projectName: string }) {
  if (run.generationStatus === 'running') {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <Loader2 className="w-8 h-8 mx-auto mb-3 animate-spin text-muted-foreground" />
          <p className="text-sm text-muted-foreground">Generating diagram...</p>
        </div>
      </div>
    );
  }

  if (run.generationStatus === 'failed') {
    return (
      <div className="flex items-center gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm">
        <AlertCircle className="w-4 h-4 flex-shrink-0" />
        Generation failed. Please try again.
      </div>
    );
  }

  if (run.generationStatus === 'succeeded' && run.diagram) {
    return (
      <DiagramSection
        plantumlSource={run.diagram.plantumlSource}
        diagramImageUrl={run.diagramImageUrl}
        downloadArtifacts={run.diagram.downloadArtifacts}
        projectName={projectName}
      />
    );
  }

  return null;
}

/**
 * Empty State Component
 */
function EmptyState({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <div className="text-center max-w-xs">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center text-muted-foreground">
          {icon}
        </div>
        <h3 className="font-medium mb-2">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      </div>
    </div>
  );
}
