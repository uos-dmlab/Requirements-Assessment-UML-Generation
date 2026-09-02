/**
 * CodeViewer Component
 * Read-only code display with copy and download functionality
 */

import { useState, useCallback } from 'react';
import { Copy, Check, Download } from 'lucide-react';
import { Button } from '../ui';

interface CodeViewerProps {
  code: string;
  language?: string;
  onDownload: () => void;
}

export function CodeViewer({ code, language = 'plantuml', onDownload }: CodeViewerProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [code]);

  // Count lines
  const lineCount = code.split('\n').length;

  return (
    <div className="space-y-3">
      {/* Code container */}
      <div className="relative">
        {/* Header bar */}
        <div className="flex items-center justify-between px-4 py-2 bg-slate-800 rounded-t-lg border-b border-slate-700">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {language}
          </span>
          <span className="text-xs text-slate-500">{lineCount} lines</span>
        </div>

        {/* Code area */}
        <div className="bg-slate-900 rounded-b-lg overflow-hidden">
          <div className="flex">
            {/* Line numbers */}
            <div className="flex-shrink-0 px-3 py-4 text-right select-none border-r border-slate-800">
              {code.split('\n').map((_, i) => (
                <div key={i} className="text-xs text-slate-600 font-mono leading-relaxed">
                  {i + 1}
                </div>
              ))}
            </div>

            {/* Code content */}
            <pre className="flex-1 p-4 overflow-x-auto">
              <code className="text-sm font-mono text-slate-300 leading-relaxed whitespace-pre">
                {code}
              </code>
            </pre>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={handleCopy}
        >
          {copied ? (
            <Check className="h-4 w-4 text-emerald-500" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
          {copied ? 'Copied!' : 'Copy Code'}
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={onDownload}
        >
          <Download className="h-4 w-4" />
          Download .puml
        </Button>
      </div>
    </div>
  );
}
