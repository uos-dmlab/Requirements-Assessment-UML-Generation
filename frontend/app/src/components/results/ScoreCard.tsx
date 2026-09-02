/**
 * ScoreCard Component
 * Displays validation metrics with visual indicators
 */

import React from 'react';
import { CheckCircle, ThumbsUp, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import type { ValidationData } from '../../types';
import {
  Card, CardHeader, CardTitle, CardDescription, CardContent,
  ProgressBar, CircularProgress,
  Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,
} from '../ui';
import { cn } from '@/lib/utils';

interface ScoreCardProps {
  validation: ValidationData;
}

export function ScoreCard({ validation }: ScoreCardProps) {
  const { score, metrics } = validation;

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-sm font-semibold uppercase tracking-wider">
              Quality Score
            </CardTitle>
            <CardDescription className="mt-0.5">
              Based on {metrics.length} metrics
            </CardDescription>
          </div>
          <CircularProgress
            value={score.value}
            max={score.max}
            size={72}
            strokeWidth={6}
          />
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        <TooltipProvider>
          {metrics.map((metric) => (
            <div key={metric.key}>
              <div className="flex justify-between items-center mb-1.5 text-xs">
                <span className="font-medium text-slate-700 dark:text-slate-300 flex items-center gap-1">
                  {metric.label}
                  {metric.tooltip && (
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button type="button" className="text-muted-foreground hover:text-foreground">
                          <Info className="h-3 w-3" />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-60 p-2">
                        {metric.tooltip}
                      </TooltipContent>
                    </Tooltip>
                  )}
                </span>
                <span className="text-slate-500 dark:text-slate-400 tabular-nums">
                  {metric.value}/{metric.max}
                </span>
              </div>
              <ProgressBar
                value={metric.value}
                max={metric.max}
                showValue={false}
                size="sm"
              />
            </div>
          ))}
        </TooltipProvider>

        <div className="pt-4 border-t border-border">
          <QualityIndicator score={score.value} maxScore={score.max} />
        </div>
      </CardContent>
    </Card>
  );
}

function QualityIndicator({ score, maxScore }: { score: number; maxScore: number }) {
  const percentage = score / maxScore;

  let label: string;
  let Icon: React.ElementType;
  let bgColor: string;
  let textColor: string;

  if (percentage >= 0.8) {
    label = 'Excellent Quality';
    bgColor = 'bg-emerald-50 dark:bg-emerald-900/20';
    textColor = 'text-emerald-700 dark:text-emerald-400';
    Icon = CheckCircle;
  } else if (percentage >= 0.6) {
    label = 'Good Quality';
    bgColor = 'bg-blue-50 dark:bg-blue-900/20';
    textColor = 'text-blue-700 dark:text-blue-400';
    Icon = ThumbsUp;
  } else if (percentage >= 0.4) {
    label = 'Needs Improvement';
    bgColor = 'bg-amber-50 dark:bg-amber-900/20';
    textColor = 'text-amber-700 dark:text-amber-400';
    Icon = AlertTriangle;
  } else {
    label = 'Significant Issues';
    bgColor = 'bg-red-50 dark:bg-red-900/20';
    textColor = 'text-red-700 dark:text-red-400';
    Icon = AlertCircle;
  }

  return (
    <div className={cn('flex items-center gap-2 p-3 rounded-lg', bgColor)}>
      <Icon className={cn('w-5 h-5', textColor)} />
      <span className={cn('text-sm font-medium', textColor)}>{label}</span>
    </div>
  );
}
