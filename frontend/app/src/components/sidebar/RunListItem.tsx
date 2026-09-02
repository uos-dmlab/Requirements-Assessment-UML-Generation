/**
 * RunListItem Component
 * Individual run entry in the sidebar run list
 */

import { Trash2, Loader2, CheckCircle, XCircle, ImageIcon } from 'lucide-react';
import type { Run } from '../../types';
import { ScoreBadge } from '../ui';
import { cn } from '@/lib/utils';

interface RunListItemProps {
  run: Run;
  isSelected: boolean;
  onClick: () => void;
  onDelete: () => void;
}

export function RunListItem({ run, isSelected, onClick, onDelete }: RunListItemProps) {
  const isAnyPhaseRunning =
    run.validationStatus === 'running' || run.generationStatus === 'running';

  // Text preview: first ~60 chars
  const preview = run.requirementsText.length > 60
    ? run.requirementsText.slice(0, 57) + '...'
    : run.requirementsText || 'Empty run';

  // Format timestamp
  const timeStr = new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }).format(new Date(run.createdAt));

  return (
    <div
      onClick={onClick}
      className={cn(
        'group relative cursor-pointer rounded-lg p-3 transition-all duration-150 border-2',
        isSelected
          ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-500 dark:border-blue-400'
          : 'border-transparent hover:border-slate-200 dark:hover:border-slate-700 hover:bg-accent/50'
      )}
    >
      {/* Text preview */}
      <p className="text-sm line-clamp-2 pr-6">{preview}</p>

      {/* Status row */}
      <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
        {/* Spinner if running */}
        {isAnyPhaseRunning && (
          <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-500" />
        )}

        {/* Validation status icon */}
        {run.validationStatus === 'succeeded' && !isAnyPhaseRunning && (
          <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
        )}
        {run.validationStatus === 'failed' && !isAnyPhaseRunning && (
          <XCircle className="h-3.5 w-3.5 text-red-500" />
        )}

        {/* Score badge */}
        {run.validationScore != null && (
          <ScoreBadge score={run.validationScore} maxScore={100} />
        )}

        {/* Diagram indicator */}
        {run.diagram?.available && (
          <ImageIcon className="h-3.5 w-3.5 text-blue-500" />
        )}

        {/* Diagram type badge */}
        <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium">
          {run.diagramType === 'use_case'
            ? 'Use Case'
            : run.detailLevel === 'design'
              ? 'Class / Design'
              : 'Class / Domain'}
        </span>

        {/* Timestamp */}
        <span className="ml-auto">{timeStr}</span>
      </div>

      {/* Delete button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className={cn(
          'absolute top-2 right-2 p-1 rounded hover:bg-red-100 dark:hover:bg-red-900/30 text-muted-foreground hover:text-red-600 dark:hover:text-red-400 transition-colors',
          'opacity-0 group-hover:opacity-100',
          isSelected && 'opacity-100'
        )}
        title="Delete run"
      >
        <Trash2 className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}
