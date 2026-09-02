/**
 * AppLayout Component
 * Main 3-column desktop layout wrapper with collapsible sidebar and resizable panels
 */

import { useState } from 'react';
import { LogOut, User, PanelLeftClose, PanelLeft, Settings } from 'lucide-react';
import { useAuthStore } from '../../store/useAuthStore';
import {
  Button,
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../ui';
import { cn } from '@/lib/utils';

interface AppLayoutProps {
  sidebar: React.ReactNode;
  main: React.ReactNode;
  panel: React.ReactNode;
  onOpenSettings?: () => void;
}

export function AppLayout({ sidebar, main, panel, onOpenSettings }: AppLayoutProps) {
  const { user, logout } = useAuthStore();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="h-screen flex flex-col bg-muted">
      {/* Top navigation bar */}
      <header className="flex-shrink-0 h-14 bg-card border-b border-border px-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Sidebar toggle button */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                  className="h-8 w-8"
                >
                  {isSidebarCollapsed ? (
                    <PanelLeft className="h-4 w-4" />
                  ) : (
                    <PanelLeftClose className="h-4 w-4" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {isSidebarCollapsed ? 'Show projects' : 'Hide projects'}
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <h1 className="text-lg font-semibold">UML Generator</h1>
        </div>

        {/* Right side - user info and logout */}
        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm">
                <User className="h-4 w-4 text-muted-foreground" />
                <span className="text-muted-foreground">{user.name}</span>
              </div>
              {onOpenSettings && (
                <Button variant="ghost" size="sm" onClick={onOpenSettings}>
                  <Settings className="h-4 w-4" />
                  <span className="hidden sm:inline">Settings</span>
                </Button>
              )}
              <Button variant="ghost" size="sm" onClick={logout}>
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          )}
        </div>
      </header>

      {/* Main content area - 3 columns */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left sidebar - Projects (collapsible) */}
        <div
          className={cn(
            'flex-shrink-0 overflow-hidden transition-all duration-300 ease-in-out',
            isSidebarCollapsed ? 'w-0' : 'w-80'
          )}
        >
          <div className="w-80 h-full">{sidebar}</div>
        </div>

        {/* Resizable Center and Right panels */}
        <ResizablePanelGroup orientation="horizontal" className="flex-1">
          {/* Center - Requirements Editor */}
          <ResizablePanel defaultSize={55} minSize={30}>
            <div className="h-full overflow-hidden">{main}</div>
          </ResizablePanel>

          {/* Resize handle with visual grip */}
          <ResizableHandle withHandle />

          {/* Right panel - Results */}
          <ResizablePanel defaultSize={45} minSize={25}>
            <div className="h-full overflow-hidden">{panel}</div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </div>
  );
}
