/**
 * Score Badge Component
 * Specialized badge for displaying scores with automatic color coding
 */

import { Badge } from './badge';
import { cn } from '@/lib/utils';

interface ScoreBadgeProps {
  score: number;
  maxScore: number;
  className?: string;
}

export function ScoreBadge({ score, maxScore, className }: ScoreBadgeProps) {
  const percentage = score / maxScore;

  let colorClasses: string;
  if (percentage >= 0.8) {
    colorClasses = 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800';
  } else if (percentage >= 0.6) {
    colorClasses = 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200 dark:border-blue-800';
  } else if (percentage >= 0.4) {
    colorClasses = 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200 dark:border-amber-800';
  } else {
    colorClasses = 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400 border-red-200 dark:border-red-800';
  }

  return (
    <Badge variant="outline" className={cn(colorClasses, className)}>
      {score}/{maxScore}
    </Badge>
  );
}
