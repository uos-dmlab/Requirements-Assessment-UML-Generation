/**
 * ProgressBar Component
 * Enhanced progress bar with label, value display, and color coding
 */

import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number;
  max: number;
  label?: string;
  showValue?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: { bar: 'h-1.5', text: 'text-xs' },
  md: { bar: 'h-2', text: 'text-sm' },
  lg: { bar: 'h-3', text: 'text-sm' },
};

function getColorClass(percentage: number): string {
  if (percentage >= 0.8) return 'bg-emerald-500';
  if (percentage >= 0.6) return 'bg-blue-500';
  if (percentage >= 0.4) return 'bg-amber-500';
  return 'bg-red-500';
}

export function ProgressBar({
  value,
  max,
  label,
  showValue = true,
  size = 'md',
  className,
}: ProgressBarProps) {
  const percentage = Math.min(1, Math.max(0, value / max));
  const colorClass = getColorClass(percentage);
  const { bar, text } = sizeClasses[size];

  return (
    <div className={className}>
      {(label || showValue) && (
        <div className={cn('flex justify-between items-center mb-1.5', text)}>
          {label && (
            <span className="font-medium text-slate-700 dark:text-slate-300">
              {label}
            </span>
          )}
          {showValue && (
            <span className="text-slate-500 dark:text-slate-400 tabular-nums">
              {value}/{max}
            </span>
          )}
        </div>
      )}
      <div
        className={cn(
          'w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden',
          bar
        )}
      >
        <div
          className={cn(
            'rounded-full transition-all duration-300 ease-out',
            bar,
            colorClass
          )}
          style={{ width: `${percentage * 100}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
}

/**
 * Circular Progress
 * Radial progress indicator for total score
 */
interface CircularProgressProps {
  value: number;
  max: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function CircularProgress({
  value,
  max,
  size = 80,
  strokeWidth = 6,
  className,
}: CircularProgressProps) {
  const percentage = Math.min(1, Math.max(0, value / max));
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - percentage * circumference;

  const colorClass = getColorClass(percentage);
  const strokeColor = colorClass.includes('emerald')
    ? '#10b981'
    : colorClass.includes('blue')
    ? '#3b82f6'
    : colorClass.includes('amber')
    ? '#f59e0b'
    : '#ef4444';

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-200 dark:text-slate-700"
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500 ease-out"
        />
      </svg>
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xl font-bold text-slate-900 dark:text-white tabular-nums">
          {value}
        </span>
        <span className="text-xs text-slate-500 dark:text-slate-400">/ {max}</span>
      </div>
    </div>
  );
}
