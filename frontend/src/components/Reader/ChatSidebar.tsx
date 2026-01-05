import React from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import type { ChatMessage } from '../../types';

interface ChatSidebarProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  onSendMessage: (message: string) => void;
  onClearHistory: () => void;
  disabled?: boolean;
}

export function ChatSidebar({
  messages,
  isStreaming,
  onSendMessage,
  onClearHistory,
  disabled,
}: ChatSidebarProps) {
  return (
    <div className="flex flex-col h-full bg-white border-l border-gray-200">
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Paper Companion</h2>
        <button
          onClick={onClearHistory}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Clear chat
        </button>
      </div>

      <MessageList messages={messages} isStreaming={isStreaming} />

      <ChatInput
        onSend={onSendMessage}
        isStreaming={isStreaming}
        disabled={disabled}
      />
    </div>
  );
}
