import React, { useState } from 'react';

interface SplitPaneProps {
  left: React.ReactNode;
  right: React.ReactNode;
  initialSplit?: number;
}

export function SplitPane({ left, right, initialSplit = 50 }: SplitPaneProps) {
  const [split, setSplit] = useState(initialSplit);
  const [isDragging, setIsDragging] = useState(false);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    e.preventDefault();
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;

    const container = e.currentTarget as HTMLElement;
    const containerWidth = container.clientWidth;
    const newSplit = (e.clientX / containerWidth) * 100;

    if (newSplit > 20 && newSplit < 80) {
      setSplit(newSplit);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging]);

  return (
    <div
      className="flex h-full"
      style={{ cursor: isDragging ? 'col-resize' : 'default' }}
    >
      <div style={{ width: `${split}%` }} className="overflow-auto">
        {left}
      </div>
      <div
        className="w-1 bg-gray-200 hover:bg-gray-400 cursor-col-resize"
        onMouseDown={handleMouseDown}
      />
      <div style={{ width: `${100 - split}%` }} className="overflow-auto">
        {right}
      </div>
    </div>
  );
}
