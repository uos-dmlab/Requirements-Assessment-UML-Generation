/**
 * RequirementsEditor Component
 * Center column: text editor with save/validate/generate actions
 */

import { Terminal, AlertCircle } from 'lucide-react';
import type { Run, Project } from '../../types';
import { RequirementsInput } from './RequirementsInput';

interface RequirementsEditorProps {
  project: Project | null;
  selectedRun: Run | null;
  onSave: (text: string) => void;
  onValidate: () => void;
  onGenerate: () => void;
  error: string | null;
}

export function RequirementsEditor({
  project,
  selectedRun,
  onSave,
  onValidate,
  onGenerate,
  error,
}: RequirementsEditorProps) {
  // No project selected state
  if (!project) {
    return (
      <div className="h-full flex flex-col bg-card">
        <div className="border-b border-border p-4">
          <h2 className="text-lg font-semibold">Requirements Editor</h2>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-muted to-muted/50 flex items-center justify-center">
              <Terminal className="w-12 h-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Select a Project</h3>
            <p className="text-muted-foreground leading-relaxed">
              Choose a project from the sidebar or create a new one to start
              validating requirements and generating UML diagrams.
            </p>
          </div>
        </div>
      </div>
    );
  }

  // No run selected
  if (!selectedRun) {
    return (
      <div className="h-full flex flex-col bg-card">
        <div className="border-b border-border p-4">
          <h2 className="text-lg font-semibold">Requirements Editor</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{project.name}</p>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center max-w-md">
            <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-muted to-muted/50 flex items-center justify-center">
              <Terminal className="w-12 h-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">Create a Run</h3>
            <p className="text-muted-foreground leading-relaxed">
              Click "+ New Run" in the sidebar to start writing requirements.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-card">
      {/* Header */}
      <div className="border-b border-border p-4">
        <div>
          <h2 className="text-lg font-semibold">Requirements Editor</h2>
          <p className="text-sm text-muted-foreground mt-0.5">{project.name}</p>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="mx-4 mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-center gap-2 text-red-700 dark:text-red-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Input area — takes up remaining space */}
      <RequirementsInput
        selectedRun={selectedRun}
        onSave={onSave}
        onValidate={onValidate}
        onGenerate={onGenerate}
      />
    </div>
  );
}
