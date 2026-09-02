/**
 * DiagramSection Component
 * Tabbed section showing diagram preview and PlantUML code
 */

import { useState, useCallback } from 'react';
import { ImageIcon, Code } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Tabs, TabsList, TabsTrigger, TabsContent } from '../ui';
import { DiagramPreview, DiagramFullscreenModal, CodeViewer } from '../diagram';
import { downloadPlantUml, downloadImage, generateFilename } from '../../utils/download';
import { artifactsApi } from '../../api';

interface DiagramSectionProps {
  plantumlSource: string | null;
  diagramImageUrl?: string;
  downloadArtifacts: Array<{ id: string; kind: string; contentType: string }>;
  projectName: string;
}

export function DiagramSection({
  plantumlSource,
  diagramImageUrl,
  downloadArtifacts,
  projectName,
}: DiagramSectionProps) {
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);

  const handleDownloadImage = useCallback(async () => {
    // Try artifact download first
    const imageArtifact = downloadArtifacts.find((a) => a.contentType.startsWith('image/'));
    if (imageArtifact) {
      const ext = imageArtifact.contentType === 'image/svg+xml' ? 'svg' : 'png';
      const filename = generateFilename(projectName, ext);
      try {
        await artifactsApi.downloadToFile(imageArtifact.id, filename);
        return;
      } catch {
        // fallback to blob URL
      }
    }

    // Fallback to blob URL download
    if (diagramImageUrl) {
      const filename = generateFilename(projectName, 'svg');
      try {
        await downloadImage(diagramImageUrl, filename);
      } catch (err) {
        console.error('Download failed:', err);
      }
    }
  }, [diagramImageUrl, downloadArtifacts, projectName]);

  const handleDownloadCode = useCallback(() => {
    const source = plantumlSource ?? '';
    // Try artifact download first
    const codeArtifact = downloadArtifacts.find((a) => a.kind === 'plantuml' || a.contentType === 'text/plain');
    if (codeArtifact) {
      const filename = generateFilename(projectName, 'puml');
      artifactsApi.downloadToFile(codeArtifact.id, filename).catch(() => {
        // fallback to local download
        downloadPlantUml(source, filename);
      });
      return;
    }

    const filename = generateFilename(projectName, 'puml');
    downloadPlantUml(source, filename);
  }, [plantumlSource, downloadArtifacts, projectName]);

  const hasImage = !!diagramImageUrl;

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider">
          Generated Diagram
        </CardTitle>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue={hasImage ? 'diagram' : 'code'}>
          <TabsList className="mb-4 w-full">
            <TabsTrigger value="diagram" className="flex-1">
              <ImageIcon className="h-4 w-4 mr-2" />
              Diagram
            </TabsTrigger>
            <TabsTrigger value="code" className="flex-1">
              <Code className="h-4 w-4 mr-2" />
              PlantUML Code
            </TabsTrigger>
          </TabsList>

          <TabsContent value="diagram">
            {hasImage ? (
              <DiagramPreview
                imageUrl={diagramImageUrl!}
                projectName={projectName}
                onViewFullscreen={() => setIsFullscreenOpen(true)}
                onDownload={handleDownloadImage}
              />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <ImageIcon className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p className="text-sm">Diagram image not available</p>
                <p className="text-xs mt-1">View the PlantUML code tab instead</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="code">
            <CodeViewer code={plantumlSource ?? ''} onDownload={handleDownloadCode} />
          </TabsContent>
        </Tabs>
      </CardContent>

      {hasImage && (
        <DiagramFullscreenModal
          isOpen={isFullscreenOpen}
          onClose={() => setIsFullscreenOpen(false)}
          imageUrl={diagramImageUrl!}
          projectName={projectName}
        />
      )}
    </Card>
  );
}
