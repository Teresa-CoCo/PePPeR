import axios from 'axios';
import type {
  PaperResponse,
  PaperDetailResponse,
  FetchRequest,
  FetchResponse,
  ProcessResponse,
  ChatRequest,
  Category,
} from './types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Papers API
export const papersApi = {
  list: async (params?: {
    category?: string;
    date_from?: string;
    date_to?: string;
    processed?: boolean;
    search?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaperResponse[]> => {
    const response = await api.get('/papers', { params });
    return response.data;
  },

  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/papers/categories');
    return response.data;
  },

  get: async (arxivId: string): Promise<PaperDetailResponse> => {
    const response = await api.get(`/papers/${arxivId}`);
    return response.data;
  },

  fetch: async (request: FetchRequest): Promise<FetchResponse> => {
    const response = await api.post('/papers/fetch', request);
    return response.data;
  },

  process: async (arxivId: string, skipOcr?: boolean): Promise<ProcessResponse> => {
    const response = await api.post(`/papers/${arxivId}/process`, { skip_ocr: skipOcr });
    return response.data;
  },

  getPdf: (arxivId: string): string => {
    return `${API_BASE}/papers/${arxivId}/pdf`;
  },
};

// Chat API
export const chatApi = {
  send: async (arxivId: string, request: ChatRequest): Promise<void> => {
    await api.post(`/chat/${arxivId}`, request);
  },

  getHistory: async (arxivId: string): Promise<{ role: string; content: string; timestamp: string }[]> => {
    const response = await api.get(`/chat/${arxivId}/history`);
    return response.data;
  },

  clearHistory: async (arxivId: string): Promise<void> => {
    await api.delete(`/chat/${arxivId}`);
  },

  generateSummary: async (arxivId: string): Promise<{
    summary: string;
    key_findings: string[];
    methodology?: string;
    strengths: string[];
    limitations: string[];
  }> => {
    const response = await api.post(`/chat/${arxivId}/generate-summary`);
    return response.data;
  },

  // SSE stream for chat
  stream: (arxivId: string, message: string): EventSource => {
    const url = new URL(`${API_BASE}/chat/${arxivId}`, window.location.origin);
    url.searchParams.append('message', message);
    return new EventSource(url.toString());
  },
};

// Health check
export const healthCheck = async (): Promise<{ status: string }> => {
  const response = await api.get('/health');
  return response.data;
};
