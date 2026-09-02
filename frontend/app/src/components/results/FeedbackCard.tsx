/**
 * FeedbackCard Component
 * Displays structured AI feedback with level-based coloring
 */

import { Card, CardHeader, CardTitle, CardContent } from '../ui';
import { cn } from '@/lib/utils';

interface FeedbackItem {
  level: 'info' | 'warning' | 'error';
  code: string;
  message: string;
}

interface FeedbackCardProps {
  feedback: FeedbackItem[];
}

export function FeedbackCard({ feedback }: FeedbackCardProps) {
  if (feedback.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider">
          AI Feedback
        </CardTitle>
      </CardHeader>

      <CardContent>
        <div className="space-y-3 text-sm leading-relaxed">
          {feedback.map((item, index) => (
            <FeedbackLine key={index} item={item} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function FeedbackLine({ item }: { item: FeedbackItem }) {
  let bgColor: string;
  let textColor: string;
  let borderColor: string;

  switch (item.level) {
    case 'error':
      bgColor = 'bg-red-50 dark:bg-red-900/20';
      textColor = 'text-red-700 dark:text-red-400';
      borderColor = 'border-l-red-500';
      break;
    case 'warning':
      bgColor = 'bg-amber-50 dark:bg-amber-900/20';
      textColor = 'text-amber-700 dark:text-amber-400';
      borderColor = 'border-l-amber-500';
      break;
    default:
      bgColor = 'bg-blue-50 dark:bg-blue-900/20';
      textColor = 'text-blue-700 dark:text-blue-400';
      borderColor = 'border-l-blue-500';
      break;
  }

  return (
    <div
      className={cn(
        'p-3 rounded-lg rounded-l-none border-l-4',
        borderColor,
        bgColor,
        textColor
      )}
    >
      {item.message}
    </div>
  );
}
