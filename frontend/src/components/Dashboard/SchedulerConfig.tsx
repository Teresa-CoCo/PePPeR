import React from 'react';

interface SchedulerConfigProps {
  isEnabled: boolean;
  fetchTime: string;
  onToggle: (enabled: boolean) => void;
  onTimeChange: (time: string) => void;
}

export function SchedulerConfig({
  isEnabled,
  fetchTime,
  onToggle,
  onTimeChange,
}: SchedulerConfigProps) {
  return (
    <div className="mt-6 p-4 bg-gray-50 rounded-lg">
      <h3 className="text-sm font-medium text-gray-900 mb-3">Scheduler Configuration</h3>
      <div className="flex items-center space-x-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={isEnabled}
            onChange={(e) => onToggle(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-700">Enable daily auto-fetch</span>
        </label>
        {isEnabled && (
          <div className="flex items-center">
            <label htmlFor="fetch-time" className="sr-only">
              Fetch time
            </label>
            <input
              type="time"
              id="fetch-time"
              value={fetchTime}
              onChange={(e) => onTimeChange(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2 border"
            />
          </div>
        )}
      </div>
    </div>
  );
}
