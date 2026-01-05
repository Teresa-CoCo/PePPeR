import { useState, useCallback } from 'react';
import { papersApi } from '../services/api';
import type { PaperResponse, Category, FetchRequest } from '../types';

interface UseArxivSearchReturn {
  papers: PaperResponse[];
  categories: Category[];
  selectedCategory: string;
  isLoading: boolean;
  error: string | null;
  fetchPapers: (category: string, date?: string) => Promise<void>;
  setSelectedCategory: (category: string) => void;
  clearError: () => void;
}

export function useArxivSearch(): UseArxivSearchReturn {
  const [papers, setPapers] = useState<PaperResponse[]>([]);
  const [categories] = useState<Category[]>([
    { id: 'cs.AI', name: 'Artificial Intelligence' },
    { id: 'cs.CL', name: 'Computation and Language' },
    { id: 'cs.CV', name: 'Computer Vision' },
    { id: 'cs.LG', name: 'Machine Learning' },
    { id: 'cs.NE', name: 'Neural and Evolutionary Computing' },
    { id: 'cs.RO', name: 'Robotics' },
    { id: 'cs.SE', name: 'Software Engineering' },
    { id: 'cs.CR', name: 'Cryptography and Security' },
    { id: 'cs.DB', name: 'Databases' },
    { id: 'cs.DC', name: 'Distributed Computing' },
    { id: 'cs.HC', name: 'Human-Computer Interaction' },
    { id: 'cs.IR', name: 'Information Retrieval' },
    { id: 'stat.ML', name: 'Statistics - Machine Learning' },
  ]);
  const [selectedCategory, setSelectedCategory] = useState<string>('cs.AI');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPapers = useCallback(async (category: string, date?: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const request: FetchRequest = { category, date };
      const response = await papersApi.fetch(request);
      setPapers(response.papers);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch papers';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    papers,
    categories,
    selectedCategory,
    isLoading,
    error,
    fetchPapers,
    setSelectedCategory,
    clearError,
  };
}
