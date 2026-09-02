/**
 * ProjectSelector Component
 * Dropdown at top of sidebar for switching between projects
 */

import { useState } from 'react';
import { ChevronDown, Plus, FolderOpen, Trash2 } from 'lucide-react';
import type { Project } from '../../types';
import { cn } from '@/lib/utils';

interface ProjectSelectorProps {
  projects: Project[];
  selectedProject: Project | null;
  onSelectProject: (id: string) => void;
  onCreateProject: () => void;
  onDeleteProject: (id: string) => void;
}

export function ProjectSelector({
  projects,
  selectedProject,
  onSelectProject,
  onCreateProject,
  onDeleteProject,
}: ProjectSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      {/* Trigger button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg text-left',
          'bg-muted/50 hover:bg-muted transition-colors',
          'border border-border',
          isOpen && 'ring-2 ring-ring'
        )}
      >
        <div className="flex items-center gap-2 min-w-0">
          <FolderOpen className="h-4 w-4 text-muted-foreground flex-shrink-0" />
          <span className="text-sm font-medium truncate">
            {selectedProject?.name ?? 'Select project'}
          </span>
        </div>
        <ChevronDown
          className={cn(
            'h-4 w-4 text-muted-foreground transition-transform flex-shrink-0',
            isOpen && 'rotate-180'
          )}
        />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div className="absolute left-0 right-0 top-full mt-1 z-50 bg-popover border border-border rounded-lg shadow-lg overflow-hidden">
            <div className="max-h-60 overflow-y-auto py-1">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className={cn(
                    'group flex items-center gap-1 px-3 py-2 text-sm hover:bg-accent transition-colors',
                    project.id === selectedProject?.id &&
                      'bg-accent font-medium'
                  )}
                >
                  <button
                    onClick={() => {
                      onSelectProject(project.id);
                      setIsOpen(false);
                    }}
                    className="flex-1 text-left min-w-0"
                  >
                    <span className="truncate block">{project.name}</span>
                    {project.description && (
                      <span className="text-xs text-muted-foreground truncate block">
                        {project.description}
                      </span>
                    )}
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      const confirmed = window.confirm(
                        `Delete "${project.name}"?\n\nAll runs and diagrams will be permanently deleted.`
                      );
                      if (!confirmed) return;
                      onDeleteProject(project.id);
                    }}
                    className="flex-shrink-0 p-1 rounded text-muted-foreground hover:text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 opacity-0 group-hover:opacity-100 transition-all"
                    title="Delete project"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}

              {projects.length === 0 && (
                <div className="px-3 py-4 text-center text-sm text-muted-foreground">
                  No projects yet
                </div>
              )}
            </div>

            {/* Create new project option */}
            <div className="border-t border-border">
              <button
                onClick={() => {
                  onCreateProject();
                  setIsOpen(false);
                }}
                className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-primary hover:bg-accent transition-colors"
              >
                <Plus className="h-4 w-4" />
                Create new project
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
