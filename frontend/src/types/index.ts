// Paper and API types

export interface Author {
  name: string;
  arxiv_id?: string;
}

export interface PaperMetadata {
  arxiv_id: string;
  title: string;
  authors: Author[];
  abstract: string;
  published_date: string;
  pdf_url: string;
  primary_category: string;
  categories: string[];
  comment?: string;
  journal_ref?: string;
  doi?: string;
}

export interface AIAnalysis {
  summary: string;
  key_findings: string[];
  methodology?: string;
  strengths: string[];
  limitations: string[];
  relevance_score?: number;
  generated_at: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Paper {
  metadata: PaperMetadata;
  pdf_path?: string;
  extracted_text?: string;
  ai_analysis?: AIAnalysis;
  chat_history: ChatMessage[];
  processed: boolean;
}

export interface PaperResponse {
  arxiv_id: string;
  title: string;
  authors: string[];
  abstract: string;
  published_date: string;
  category: string;
  ai_summary?: string;
  processed: boolean;
}

export interface PaperDetailResponse {
  metadata: PaperMetadata;
  pdf_path?: string;
  extracted_text?: string;
  ai_analysis?: AIAnalysis;
  chat_history: ChatMessage[];
  processed: boolean;
}

export interface FetchRequest {
  category: string;
  date?: string;
}

export interface FetchResponse {
  category: string;
  date: string;
  papers_found: number;
  papers_downloaded: number;
  papers: PaperResponse[];
}

export interface ProcessResponse {
  arxiv_id: string;
  ocr_success: boolean;
  text_extracted: boolean;
  ai_analysis_generated: boolean;
  message: string;
}

export interface ChatRequest {
  message: string;
  model?: string;
}

export interface Category {
  id: string;
  name: string;
}

export const CATEGORIES: Category[] = [
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
];
