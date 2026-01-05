import { useState, useEffect } from 'react';
import { Header } from './components/Layout/Header';
import { SplitPane } from './components/Layout/SplitPane';
import { CategorySelector, FetchButton, SchedulerConfig } from './components/Dashboard';
import { PaperList } from './components/Library';
import { PDFViewer, ChatSidebar } from './components/Reader';
import { useArxivSearch } from './hooks/useArxivSearch';
import { useChatStream } from './hooks/useChatStream';
import { usePaperContext } from './hooks/usePaperContext';
import { papersApi } from './services/api';
import type { PaperDetailResponse, PaperResponse } from './types';

type View = 'dashboard' | 'reader';

function App() {
  const [view, setView] = useState<View>('dashboard');
  const [selectedPaperId, setSelectedPaperId] = useState<string | null>(null);
  const [paperDetail, setPaperDetail] = useState<PaperDetailResponse | null>(null);

  const {
    categories,
    selectedCategory,
    isLoading: isFetching,
    error: fetchError,
    fetchPapers,
    setSelectedCategory,
  } = useArxivSearch();

  const { processPaper } = usePaperContext();
  const {
    messages,
    isStreaming,
    sendMessage,
    clearHistory,
  } = useChatStream(selectedPaperId || '');

  // Load papers on mount
  useEffect(() => {
    papersApi.list({ limit: 50 }).then((papers) => {
      // Cast papers to PaperDetailResponse[] for display
      setPaperDetail(papers as unknown as PaperDetailResponse);
    });
  }, []);

  const handleFetch = async () => {
    await fetchPapers(selectedCategory);
  };

  const handleSelectPaper = async (arxivId: string) => {
    setSelectedPaperId(arxivId);
    setView('reader');

    // Load paper details
    try {
      const detail = await papersApi.get(arxivId);
      setPaperDetail(detail);

      // Auto-process if not processed
      if (!detail.processed) {
        await processPaper(true);
      }
    } catch (err) {
      console.error('Failed to load paper:', err);
    }
  };

  const handleHome = () => {
    setView('dashboard');
    setSelectedPaperId(null);
    setPaperDetail(null);

    // Refresh paper list
    papersApi.list({ limit: 50 }).then((papers: PaperResponse[]) => {
      setPaperDetail(papers as unknown as PaperDetailResponse);
    });
  };

  const renderDashboard = () => (
    <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Fetch Papers</h1>

        <CategorySelector
          categories={categories}
          selectedCategory={selectedCategory}
          onSelect={setSelectedCategory}
        />

        <FetchButton onFetch={handleFetch} isLoading={isFetching} />

        {fetchError && (
          <div className="mt-4 p-4 bg-red-50 rounded-md">
            <p className="text-sm text-red-700">{fetchError}</p>
          </div>
        )}

        <SchedulerConfig
          isEnabled={false}
          fetchTime="08:00"
          onToggle={() => {}}
          onTimeChange={() => {}}
        />
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Paper Library</h2>
        {paperDetail && (
          <PaperList
            papers={paperDetail as any}
            onSelectPaper={handleSelectPaper}
          />
        )}
      </div>
    </div>
  );

  const renderReader = () => {
    if (!selectedPaperId || !paperDetail) {
      return (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">No paper selected</p>
        </div>
      );
    }

    const paper = paperDetail as any;
    const pdfUrl = papersApi.getPdf(selectedPaperId);

    return (
      <SplitPane
        left={
          <div className="h-full flex flex-col">
            <div className="p-4 bg-gray-50 border-b">
              <h1 className="font-semibold text-gray-900 line-clamp-2">
                {paper.metadata?.title || 'Loading...'}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                {paper.metadata?.authors?.map((a: any) => a.name).join(', ')}
              </p>
            </div>
            <div className="flex-1">
              <PDFViewer url={pdfUrl} />
            </div>
          </div>
        }
        right={
          <ChatSidebar
            messages={messages}
            isStreaming={isStreaming}
            onSendMessage={sendMessage}
            onClearHistory={clearHistory}
            disabled={!paperDetail?.extracted_text}
          />
        }
      />
    );
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header onHome={handleHome} />

      {view === 'dashboard' && renderDashboard()}
      {view === 'reader' && renderReader()}
    </div>
  );
}

export default App;
