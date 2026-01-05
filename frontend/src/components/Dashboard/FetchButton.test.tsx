/** Tests for FetchButton component. */

import { describe, expect, test, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { FetchButton } from './FetchButton';

describe('FetchButton', () => {
  const mockOnFetch = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders button with fetch text', () => {
    render(<FetchButton onFetch={mockOnFetch} isLoading={false} />);

    expect(screen.getByRole('button', { name: /Fetch Today's Papers/i })).toBeInTheDocument();
  });

  test('shows loading state', () => {
    render(<FetchButton onFetch={mockOnFetch} isLoading={true} />);

    expect(screen.getByRole('button')).toHaveTextContent(/Fetching.../i);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('calls onFetch when clicked', () => {
    render(<FetchButton onFetch={mockOnFetch} isLoading={false} />);

    fireEvent.click(screen.getByRole('button'));
    expect(mockOnFetch).toHaveBeenCalledTimes(1);
  });

  test('is disabled when disabled prop is true', () => {
    render(<FetchButton onFetch={mockOnFetch} isLoading={false} disabled={true} />);

    expect(screen.getByRole('button')).toBeDisabled();
  });

  test('is disabled when isLoading is true', () => {
    render(<FetchButton onFetch={mockOnFetch} isLoading={true} />);

    expect(screen.getByRole('button')).toBeDisabled();
  });
});
