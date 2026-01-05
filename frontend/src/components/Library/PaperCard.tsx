import React from 'react';
import type { PaperResponse } from '../../types';

interface PaperCardProps {
  paper: PaperResponse;
  onClick: () => void;
}

export function PaperCard({ paper, onClick }: PaperCardProps) {
  const publishedDate = new Date(paper.published_date).toLocaleDateString();

  return (
    <div
      onClick={onClick}
      className="bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200"
    >
      <div className="flex justify-between items-start">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
          {paper.category}
        </span>
        <span className="text-xs text-gray-500">{publishedDate}</span>
      </div>

      <h3 className="mt-2 text-sm font-semibold text-gray-900 line-clamp-2">
        {paper.title}
      </h3>

      <p className="mt-1 text-xs text-gray-500 line-clamp-1">
        {paper.authors.slice(0, 3).join(', ')}
        {paper.authors.length > 3 && ` +${paper.authors.length - 3} more`}
      </p>

      {paper.ai_summary && (
        <div className="mt-3 p-2 bg-green-50 rounded text-xs text-green-800 line-clamp-2">
          <span className="font-medium">AI Summary:</span> {paper.ai_summary}
        </div>
      )}

      <div className="mt-2 flex items-center justify-between">
        <span className="text-xs text-gray-400">arXiv:{paper.arxiv_id}</span>
        {paper.processed ? (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
            Processed
          </span>
        ) : (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
            Unprocessed
          </span>
        )}
      </div>
    </div>
  );
}
