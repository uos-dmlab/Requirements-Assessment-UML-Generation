/**
 * UI Components - Barrel Export
 * Re-exports shadcn components and custom extensions
 */

// shadcn components
export { Button, buttonVariants } from './button';
export { Badge, badgeVariants } from './badge';
export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
} from './dialog';
export { Tabs, TabsList, TabsTrigger, TabsContent } from './tabs';
export { Progress } from './progress';
export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
} from './card';
export { Input } from './input';
export { Textarea } from './textarea';
export { Label } from './label';
export { ScrollArea, ScrollBar } from './scroll-area';
export { Separator } from './separator';
export {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from './tooltip';
export {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from './resizable';

// Custom components
export { ScoreBadge } from './score-badge';
export { ProgressBar, CircularProgress } from './progress-bar';
