/** Tests for types module. */

import { describe, expect, test } from 'vitest';
import type { Category, Paper, PaperMetadata, AIAnalysis, ChatMessage } from '../types';

describe('Types', () => {
  describe('Category', () => {
    test('Category type should accept id and name', () => {
      const category: Category = {
        id: 'cs.AI',
        name: 'Artificial Intelligence',
      };
      expect(category.id).toBe('cs.AI');
      expect(category.name).toBe('Artificial Intelligence');
    });
  });

  describe('PaperMetadata', () => {
    test('PaperMetadata should have required fields', () => {
      const metadata: PaperMetadata = {
        arxiv_id: 'test-1234.5678',
        title: 'Test Paper',
        authors: [{ name: 'Test Author' }],
        abstract: 'Test abstract',
        published_date: '2024-01-15T00:00:00Z',
        pdf_url: 'http://arxiv.org/pdf/test-1234.5678.pdf',
        primary_category: 'cs.AI',
        categories: ['cs.AI', 'cs.LG'],
      };
      expect(metadata.arxiv_id).toBe('test-1234.5678');
      expect(metadata.categories).toHaveLength(2);
    });
  });

  describe('AIAnalysis', () => {
    test('AIAnalysis should have summary and findings', () => {
      const analysis: AIAnalysis = {
        summary: 'Test summary',
        key_findings: ['Finding 1', 'Finding 2'],
        strengths: ['Strength 1'],
        limitations: ['Limitation 1'],
        generated_at: '2024-01-15T00:00:00Z',
      };
      expect(analysis.summary).toBe('Test summary');
      expect(analysis.key_findings).toHaveLength(2);
    });
  });

  describe('ChatMessage', () => {
    test('ChatMessage should have role and content', () => {
      const message: ChatMessage = {
        role: 'user',
        content: 'What is this paper about?',
        timestamp: '2024-01-15T00:00:00Z',
      };
      expect(message.role).toBe('user');
      expect(message.content).toBe('What is this paper about?');
    });

    test('ChatMessage role can be assistant', () => {
      const message: ChatMessage = {
        role: 'assistant',
        content: 'This paper is about...',
        timestamp: '2024-01-15T00:00:00Z',
      };
      expect(message.role).toBe('assistant');
    });
  });

  describe('Paper', () => {
    test('Paper should have metadata and processed flag', () => {
      const paper: Paper = {
        metadata: {
          arxiv_id: 'test-1234.5678',
          title: 'Test Paper',
          authors: [{ name: 'Test Author' }],
          abstract: 'Test abstract',
          published_date: '2024-01-15T00:00:00Z',
          pdf_url: 'http://arxiv.org/pdf/test-1234.5678.pdf',
          primary_category: 'cs.AI',
          categories: ['cs.AI'],
        },
        chat_history: [],
        processed: false,
      };
      expect(paper.processed).toBe(false);
      expect(paper.chat_history).toEqual([]);
    });
  });
});
