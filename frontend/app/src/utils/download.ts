/**
 * Download Utilities
 * Helper functions for downloading files from the browser
 */

/**
 * Download a text file
 */
export function downloadTextFile(content: string, filename: string, mimeType: string = 'text/plain'): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  URL.revokeObjectURL(url);
}

/**
 * Download PlantUML code as .puml file
 */
export function downloadPlantUml(code: string, filename: string = 'diagram.puml'): void {
  downloadTextFile(code, filename, 'text/plain');
}

/**
 * Download an image from a data URL or blob URL
 */
export async function downloadImage(imageUrl: string, filename: string = 'diagram.png'): Promise<void> {
  try {
    // If it's a data URL, convert to blob
    if (imageUrl.startsWith('data:')) {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
    } else {
      // Regular URL - fetch and download
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('Failed to download image:', error);
    throw new Error('Failed to download image');
  }
}

/**
 * Generate a filename from project name
 */
export function generateFilename(projectName: string, extension: string): string {
  const sanitized = projectName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  
  const timestamp = new Date().toISOString().slice(0, 10);
  return `${sanitized}-${timestamp}.${extension}`;
}
