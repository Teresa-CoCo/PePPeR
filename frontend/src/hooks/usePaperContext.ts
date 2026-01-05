import { useState, useCallback } from 'react';
import { papersApi } from '../services/api';
import type { PaperDetailResponse } from '../types';

interface UsePaperContextReturn {
  paper: PaperDetailResponse | null;
  isLoading: boolean;
  error: string | null;
  loadPaper: (arxivId: string) => Promise<void>;
  processPaper: (skipOcr?: boolean) => Promise<void>;
  clearPaper: () => void;
}

export function usePaperContext(): UsePaperContextReturn {
  const [paper, setPaper] = useState<PaperDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPaper = useCallback(async (arxivId: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await papersApi.get(arxivId);
      setPaper(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load paper');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const processPaper = useCallback(async (skipOcr?: boolean) => {
    if (!paper) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await papersApi.process(paper.metadata.arxiv_id, skipOcr);

      // Reload paper to get updated data
      const updated = await papersApi.get(paper.metadata.arxiv_id);
      setPaper(updated);

      if (!result.ai_analysis_generated) {
        setError('Processing completed but AI analysis failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Processing failed');
    } finally {
      setIsLoading(false);
    }
  }, [paper]);

  const clearPaper = useCallback(() => {
    setPaper(null);
    setError(null);
  }, []);

  return {
    paper,
    isLoading,
    error,
    loadPaper,
    processPaper,
    clearPaper,
  };
}
