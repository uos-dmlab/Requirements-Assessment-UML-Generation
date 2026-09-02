/**
 * RunsSidebar Component
 * Left sidebar with project selector and run list
 */

import { useState } from 'react';
import { Plus, FileText, Info } from 'lucide-react';
import { Button, ScrollArea, Separator, Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui';
import { ProjectSelector } from './ProjectSelector';
import { RunListItem } from './RunListItem';
import { NewProjectModal } from '../projects/NewProjectModal';
import type { Project, Run, DiagramType, DetailLevel } from '../../types';

interface RunsSidebarProps {
  projects: Project[];
  selectedProject: Project | null;
  runs: Run[];
  selectedRunId: string | null;
  onSelectProject: (id: string) => void;
  onCreateProject: (name: string, description?: string) => void;
  onDeleteProject: (id: string) => void;
  onSelectRun: (id: string) => void;
  onCreateRun: (diagramType: DiagramType, detailLevel?: DetailLevel) => void;
  onDeleteRun: (id: string) => void;
}

export function RunsSidebar({
  projects,
  selectedProject,
  runs,
  selectedRunId,
  onSelectProject,
  onCreateProject,
  onDeleteProject,
  onSelectRun,
  onCreateRun,
  onDeleteRun,
}: RunsSidebarProps) {
  const [isNewProjectModalOpen, setIsNewProjectModalOpen] = useState(false);
  const [newRunDiagramType, setNewRunDiagramType] = useState<DiagramType>('class');
  const [newRunDetailLevel, setNewRunDetailLevel] = useState<DetailLevel>('domain');

  return (
    <>
      <aside className="h-full flex flex-col bg-slate-50 dark:bg-slate-900 border-r border-border">
        {/* Project Selector */}
        <div className="p-4 border-b border-border">
          <ProjectSelector
            projects={projects}
            selectedProject={selectedProject}
            onSelectProject={onSelectProject}
            onCreateProject={() => setIsNewProjectModalOpen(true)}
            onDeleteProject={onDeleteProject}
          />
        </div>

        {/* New Run controls */}
        {selectedProject && (
          <div className="px-4 pt-3 pb-1 space-y-2">
            <select
              value={newRunDiagramType}
              onChange={(e) => setNewRunDiagramType(e.target.value as DiagramType)}
              className="w-full rounded-md border border-border bg-background px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
            >
              <option value="class">Class Diagram</option>
              <option value="use_case">Use Case Diagram</option>
            </select>
            {newRunDiagramType === 'class' && (
              <div className="flex items-center gap-1.5">
                <select
                  value={newRunDetailLevel}
                  onChange={(e) => setNewRunDetailLevel(e.target.value as DetailLevel)}
                  className="flex-1 rounded-md border border-border bg-background px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="domain">Domain Model</option>
                  <option value="design">Design Model</option>
                </select>
                <TooltipProvider>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <button type="button" className="flex-shrink-0 p-1 rounded text-muted-foreground hover:text-foreground">
                        <Info className="h-3.5 w-3.5" />
                      </button>
                    </TooltipTrigger>
                    <TooltipContent side="right" className="max-w-60 space-y-2 p-3">
                      <div>
                        <p className="font-semibold">Domain Model</p>
                        <p>Classes and relationships only. No methods. For requirements analysis.</p>
                      </div>
                      <div>
                        <p className="font-semibold">Design Model</p>
                        <p>Includes methods and visibility. For system design and development.</p>
                      </div>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            )}
            <Button
              size="sm"
              className="w-full"
              onClick={() => onCreateRun(newRunDiagramType, newRunDiagramType === 'class' ? newRunDetailLevel : undefined)}
            >
              <Plus className="h-4 w-4 mr-1" />
              New Run
            </Button>
          </div>
        )}

        {/* Run List */}
        <ScrollArea className="flex-1">
          <div className="p-3 space-y-1">
            {!selectedProject ? (
              <div className="text-center py-12 px-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                  <FileText className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="font-medium mb-1">No project selected</h3>
                <p className="text-sm text-muted-foreground">
                  Select or create a project to get started
                </p>
              </div>
            ) : runs.length === 0 ? (
              <div className="text-center py-12 px-4">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                  <FileText className="w-8 h-8 text-muted-foreground" />
                </div>
                <h3 className="font-medium mb-1">No runs yet</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Create a new run to start writing requirements
                </p>
              </div>
            ) : (
              runs.map((run) => (
                <RunListItem
                  key={run.id}
                  run={run}
                  isSelected={run.id === selectedRunId}
                  onClick={() => onSelectRun(run.id)}
                  onDelete={() => onDeleteRun(run.id)}
                />
              ))
            )}
          </div>
        </ScrollArea>

        {/* Footer */}
        <Separator />
        <div className="p-4">
          <div className="text-xs text-muted-foreground text-center">
            {runs.length} {runs.length === 1 ? 'run' : 'runs'}
          </div>
        </div>
      </aside>

      {/* New Project Modal */}
      <NewProjectModal
        isOpen={isNewProjectModalOpen}
        onClose={() => setIsNewProjectModalOpen(false)}
        onCreate={onCreateProject}
      />
    </>
  );
}
