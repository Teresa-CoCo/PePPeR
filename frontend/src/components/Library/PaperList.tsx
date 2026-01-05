import React, { useState } from 'react';
import { PaperCard } from './PaperCard';
import type { PaperResponse } from '../../types';

interface PaperListProps {
  papers: PaperResponse[];
  onSelectPaper: (arxivId: string) => void;
}

export function PaperList({ papers, onSelectPaper }: PaperListProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPapers = papers.filter(
    (paper) =>
      paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      paper.abstract.toLowerCase().includes(searchTerm.toLowerCase()) ||
      paper.authors.some((a) => a.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Group by date
  const groupedPapers = filteredPapers.reduce((groups, paper) => {
    const date = new Date(paper.published_date).toLocaleDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(paper);
    return groups;
  }, {} as Record<string, PaperResponse[]>);

  return (
    <div>
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search papers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
        />
      </div>

      {Object.keys(groupedPapers).length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          {searchTerm ? 'No papers match your search' : 'No papers found'}
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(groupedPapers).map(([date, datePapers]) => (
            <div key={date}>
              <h3 className="text-sm font-medium text-gray-500 mb-2">{date}</h3>
              <div className="grid gap-3">
                {datePapers.map((paper) => (
                  <PaperCard
                    key={paper.arxiv_id}
                    paper={paper}
                    onClick={() => onSelectPaper(paper.arxiv_id)}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
