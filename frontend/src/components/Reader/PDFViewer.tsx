import { Worker, Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';

interface PDFViewerProps {
  url: string;
  onLoadSuccess?: (numPages: number) => void;
}

export function PDFViewer({ url, onLoadSuccess }: PDFViewerProps) {
  const defaultLayoutPluginInstance = defaultLayoutPlugin();

  return (
    <div className="h-[calc(100vh-200px)]">
      <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
        <Viewer
          fileUrl={url}
          plugins={[defaultLayoutPluginInstance]}
          onDocumentLoad={(e) => {
            if (onLoadSuccess) {
              onLoadSuccess(e.doc.numPages);
            }
          }}
        />
      </Worker>
    </div>
  );
}
