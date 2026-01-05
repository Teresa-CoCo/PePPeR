import React from 'react';
import type { Category } from '../types';

interface CategorySelectorProps {
  categories: Category[];
  selectedCategory: string;
  onSelect: (category: string) => void;
}

export function CategorySelector({
  categories,
  selectedCategory,
  onSelect,
}: CategorySelectorProps) {
  return (
    <div className="mb-4">
      <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
        ArXiv Category
      </label>
      <select
        id="category"
        value={selectedCategory}
        onChange={(e) => onSelect(e.target.value)}
        className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
      >
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.id} - {cat.name}
          </option>
        ))}
      </select>
    </div>
  );
}
