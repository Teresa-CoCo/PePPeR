/** Tests for CategorySelector component. */

import { describe, expect, test, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { CategorySelector } from './CategorySelector';
import type { Category } from '../types';

describe('CategorySelector', () => {
  const mockCategories: Category[] = [
    { id: 'cs.AI', name: 'Artificial Intelligence' },
    { id: 'cs.LG', name: 'Machine Learning' },
    { id: 'cs.CV', name: 'Computer Vision' },
  ];

  const mockOnSelect = vi.fn();

  test('renders all categories', () => {
    render(
      <CategorySelector
        categories={mockCategories}
        selectedCategory="cs.AI"
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByRole('combobox')).toBeInTheDocument();

    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(3);
  });

  test('shows correct selected value', () => {
    render(
      <CategorySelector
        categories={mockCategories}
        selectedCategory="cs.LG"
        onSelect={mockOnSelect}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('cs.LG');
  });

  test('calls onSelect when selection changes', () => {
    render(
      <CategorySelector
        categories={mockCategories}
        selectedCategory="cs.AI"
        onSelect={mockOnSelect}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: 'cs.CV' } });

    expect(mockOnSelect).toHaveBeenCalledWith('cs.CV');
  });

  test('displays category name with id', () => {
    render(
      <CategorySelector
        categories={mockCategories}
        selectedCategory="cs.AI"
        onSelect={mockOnSelect}
      />
    );

    expect(screen.getByText('cs.AI - Artificial Intelligence')).toBeInTheDocument();
  });
});
