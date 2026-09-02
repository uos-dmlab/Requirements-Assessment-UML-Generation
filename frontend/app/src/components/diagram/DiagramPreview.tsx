/**
 * DiagramPreview Component
 * Thumbnail preview of generated UML diagram
 */

import { Maximize2, Download, ZoomIn } from 'lucide-react';
import { Button } from '../ui';

interface DiagramPreviewProps {
  imageUrl: string;
  projectName: string;
  onViewFullscreen: () => void;
  onDownload: () => void;
}

export function DiagramPreview({
  imageUrl,
  projectName,
  onViewFullscreen,
  onDownload,
}: DiagramPreviewProps) {
  return (
    <div className="space-y-3">
      {/* Image container */}
      <div
        className="
          relative group
          bg-muted
          border border-border
          rounded-lg overflow-hidden
          cursor-pointer
        "
        onClick={onViewFullscreen}
      >
        {/* Image */}
        <img
          src={imageUrl}
          alt={`UML diagram for ${projectName}`}
          className="w-full h-48 object-contain p-2"
        />

        {/* Hover overlay */}
        <div
          className="
            absolute inset-0
            bg-black/0 group-hover:bg-black/40
            flex items-center justify-center
            opacity-0 group-hover:opacity-100
            transition-all duration-200
          "
        >
          <div className="flex items-center gap-2 text-white font-medium">
            <ZoomIn className="h-5 w-5" />
            <span>View Full Size</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={onViewFullscreen}
        >
          <Maximize2 className="h-4 w-4" />
          Fullscreen
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={onDownload}
        >
          <Download className="h-4 w-4" />
          Download
        </Button>
      </div>
    </div>
  );
}
