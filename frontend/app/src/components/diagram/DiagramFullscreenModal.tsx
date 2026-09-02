/**
 * DiagramFullscreenModal Component
 * Fullscreen diagram viewer with zoom and pan controls
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Minus, Plus } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  Button,
  Separator,
} from '../ui';

interface DiagramFullscreenModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  projectName: string;
}

const MIN_SCALE = 0.25;
const MAX_SCALE = 4;
const SCALE_STEP = 0.25;

export function DiagramFullscreenModal({
  isOpen,
  onClose,
  imageUrl,
  projectName,
}: DiagramFullscreenModalProps) {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setScale(1);
      setPosition({ x: 0, y: 0 });
    }
  }, [isOpen]);

  // Zoom controls
  const handleZoomIn = useCallback(() => {
    setScale((s) => Math.min(MAX_SCALE, s + SCALE_STEP));
  }, []);

  const handleZoomOut = useCallback(() => {
    setScale((s) => Math.max(MIN_SCALE, s - SCALE_STEP));
  }, []);

  const handleFit = useCallback(() => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  }, []);

  const handleReset = useCallback(() => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  }, []);

  // Mouse wheel zoom
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -SCALE_STEP : SCALE_STEP;
    setScale((s) => Math.max(MIN_SCALE, Math.min(MAX_SCALE, s + delta)));
  }, []);

  // Pan handlers
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (scale > 1) {
        setIsDragging(true);
        setDragStart({
          x: e.clientX - position.x,
          y: e.clientY - position.y,
        });
      }
    },
    [scale, position]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDragging) return;
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    },
    [isDragging, dragStart]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case '+':
        case '=':
          handleZoomIn();
          break;
        case '-':
        case '_':
          handleZoomOut();
          break;
        case '0':
          handleReset();
          break;
        case 'f':
        case 'F':
          handleFit();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, handleZoomIn, handleZoomOut, handleReset, handleFit]);

  const zoomPercentage = Math.round(scale * 100);

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-none w-screen h-screen p-0 rounded-none border-0">
        <div className="h-full flex flex-col bg-slate-100 dark:bg-slate-950">
          {/* Header */}
          <DialogHeader className="px-4 py-3 bg-card border-b border-border flex-row items-center justify-between space-y-0">
            <DialogTitle>{projectName} - UML Diagram</DialogTitle>

            {/* Toolbar */}
            <div className="flex items-center gap-2">
              {/* Zoom controls */}
              <div className="flex items-center bg-muted rounded-lg p-1">
                <button
                  onClick={handleZoomOut}
                  disabled={scale <= MIN_SCALE}
                  className="p-2 rounded-md hover:bg-background disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  title="Zoom out (-)"
                >
                  <Minus className="h-4 w-4" />
                </button>

                <span className="px-3 text-sm font-medium min-w-[4rem] text-center tabular-nums">
                  {zoomPercentage}%
                </span>

                <button
                  onClick={handleZoomIn}
                  disabled={scale >= MAX_SCALE}
                  className="p-2 rounded-md hover:bg-background disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  title="Zoom in (+)"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>

              <Separator orientation="vertical" className="h-6" />

              <Button variant="ghost" size="sm" onClick={handleFit}>
                Fit
              </Button>
              <Button variant="ghost" size="sm" onClick={handleReset}>
                Reset
              </Button>
            </div>
          </DialogHeader>

          {/* Keyboard hints */}
          <div className="hidden sm:flex items-center justify-center gap-4 py-2 text-xs text-muted-foreground bg-muted/50 border-b border-border">
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-background rounded font-mono">+</kbd>
              <span>/</span>
              <kbd className="px-1.5 py-0.5 bg-background rounded font-mono">-</kbd>
              <span className="ml-1">Zoom</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-background rounded font-mono">0</kbd>
              <span className="ml-1">Reset</span>
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1.5 py-0.5 bg-background rounded font-mono">F</kbd>
              <span className="ml-1">Fit</span>
            </span>
            <span>Scroll to zoom • Drag to pan</span>
          </div>

          {/* Diagram container */}
          <div
            ref={containerRef}
            className={`
              flex-1 overflow-hidden
              flex items-center justify-center
              ${isDragging ? 'cursor-grabbing' : scale > 1 ? 'cursor-grab' : 'cursor-default'}
            `}
            onWheel={handleWheel}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseLeave}
          >
            {/* Checkered background pattern */}
            <div
              className="absolute inset-0 opacity-30"
              style={{
                backgroundImage: `
                  linear-gradient(45deg, #e2e8f0 25%, transparent 25%),
                  linear-gradient(-45deg, #e2e8f0 25%, transparent 25%),
                  linear-gradient(45deg, transparent 75%, #e2e8f0 75%),
                  linear-gradient(-45deg, transparent 75%, #e2e8f0 75%)
                `,
                backgroundSize: '20px 20px',
                backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px',
              }}
            />

            {/* Image */}
            <img
              ref={imageRef}
              src={imageUrl}
              alt={`UML diagram for ${projectName}`}
              className="relative select-none"
              style={{
                transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
                transition: isDragging ? 'none' : 'transform 0.15s ease-out',
                maxWidth: 'none',
                maxHeight: 'none',
              }}
              draggable={false}
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
