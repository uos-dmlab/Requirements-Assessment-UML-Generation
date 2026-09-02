/**
 * RequirementsInput Component
 * Textarea with Save, Validate, and Generate buttons
 */

import React, { useState, useCallback, useEffect } from 'react';
import { Save, CheckCircle, Image, AlertTriangle } from 'lucide-react';
import { Button, Textarea } from '../ui';
import type { Run } from '../../types';
import { formatDiagramType, formatDetailLevel } from '../../types';

interface RequirementsInputProps {
  selectedRun: Run;
  onSave: (text: string) => void;
  onValidate: () => void;
  onGenerate: () => void;
}

export function RequirementsInput({
  selectedRun,
  onSave,
  onValidate,
  onGenerate,
}: RequirementsInputProps) {
  const [localText, setLocalText] = useState(selectedRun.requirementsText);

  // Sync local text when selected run changes
  useEffect(() => {
    setLocalText(selectedRun.requirementsText);
  }, [selectedRun.id, selectedRun.requirementsText]);

  const hasChanges = localText !== selectedRun.requirementsText;
  const isEmpty = localText.trim().length === 0;
  const isValidationRunning = selectedRun.validationStatus === 'running';
  const isGenerationRunning = selectedRun.generationStatus === 'running';
  const isAnyRunning = isValidationRunning || isGenerationRunning;

  // Warnings
  const hasUnsavedWithResults = hasChanges && (selectedRun.validationStatus === 'succeeded' || selectedRun.generationStatus === 'succeeded');
  const lowScore = selectedRun.validationScore != null && selectedRun.validationScore < 50;

  const handleSave = useCallback(() => {
    if (!hasChanges || isAnyRunning) return;
    onSave(localText);
  }, [localText, hasChanges, isAnyRunning, onSave]);

  const handleValidate = useCallback(() => {
    if (hasChanges || isEmpty || isValidationRunning) return;
    onValidate();
  }, [hasChanges, isEmpty, isValidationRunning, onValidate]);

  const handleGenerate = useCallback(() => {
    if (hasChanges || selectedRun.validationStatus !== 'succeeded' || isGenerationRunning) return;
    onGenerate();
  }, [hasChanges, selectedRun.validationStatus, isGenerationRunning, onGenerate]);

  // Keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'Enter') {
        e.preventDefault();
        handleValidate();
      }
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key === 'Enter') {
        e.preventDefault();
        handleGenerate();
      }
    },
    [handleSave, handleValidate, handleGenerate]
  );

  return (
    <div className="flex-1 flex flex-col p-4 min-h-0">
      {/* Diagram type badges */}
      <div className="mb-2 flex items-center gap-1.5">
        <span className="inline-block rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
          {formatDiagramType(selectedRun.diagramType)}
        </span>
        {selectedRun.diagramType === 'class' && (
          <span className="inline-block rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
            {formatDetailLevel(selectedRun.detailLevel)}
          </span>
        )}
      </div>

      {/* Textarea — fills available space */}
      <div className="relative flex-1 mb-3 min-h-0">
        <Textarea
          value={localText}
          onChange={(e) => setLocalText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe your system requirements...

Example: The system has User, Product, and Order classes. Users can register and login. Each User can place multiple Orders. An Order contains one or more Products with quantities."
          disabled={isAnyRunning}
          className="h-full resize-none text-sm leading-relaxed"
        />
        {/* Character count */}
        <div className="absolute bottom-2 right-3 text-xs text-muted-foreground">
          {localText.length} chars
        </div>
      </div>

      {/* Warnings */}
      {hasUnsavedWithResults && (
        <div className="mb-3 flex items-center gap-2 p-2.5 rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 text-xs">
          <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
          Save and re-validate to update results
        </div>
      )}
      {!hasChanges && lowScore && selectedRun.validationStatus === 'succeeded' && (
        <div className="mb-3 flex items-center gap-2 p-2.5 rounded-lg bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 text-xs">
          <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
          Low score — diagram quality may be poor
        </div>
      )}

      {/* Actions row */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {hasChanges ? 'Unsaved changes' : 'Saved'}
        </p>

        <div className="flex gap-2">
          {/* Save — only visible when there are changes */}
          {hasChanges && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              disabled={isAnyRunning}
              leftIcon={<Save className="h-4 w-4" />}
            >
              Save
            </Button>
          )}

          {/* Validate */}
          <Button
            variant="success"
            size="sm"
            onClick={handleValidate}
            isLoading={isValidationRunning}
            disabled={hasChanges || isEmpty || isGenerationRunning}
            leftIcon={!isValidationRunning ? <CheckCircle className="h-4 w-4" /> : undefined}
          >
            Validate
          </Button>

          {/* Generate */}
          <Button
            size="sm"
            onClick={handleGenerate}
            isLoading={isGenerationRunning}
            disabled={hasChanges || selectedRun.validationStatus !== 'succeeded' || isValidationRunning}
            leftIcon={!isGenerationRunning ? <Image className="h-4 w-4" /> : undefined}
          >
            Generate
          </Button>
        </div>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">Ctrl</kbd>
          <span>+</span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">S</kbd>
          <span className="ml-1">Save</span>
        </span>
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">Ctrl</kbd>
          <span>+</span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">Shift</kbd>
          <span>+</span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">Enter</kbd>
          <span className="ml-1">Validate</span>
        </span>
        <span className="flex items-center gap-1">
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">Ctrl</kbd>
          <span>+</span>
          <kbd className="px-1.5 py-0.5 bg-muted rounded font-mono">Enter</kbd>
          <span className="ml-1">Generate</span>
        </span>
      </div>
    </div>
  );
}
