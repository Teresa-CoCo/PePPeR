import { useState, useCallback, useRef, useEffect } from 'react';
import { chatApi, papersApi } from '../services/api';
import type { ChatMessage } from '../types';

interface UseChatStreamReturn {
  messages: ChatMessage[];
  isStreaming: boolean;
  sendMessage: (content: string) => Promise<void>;
  clearHistory: () => Promise<void>;
  setMessages: (messages: ChatMessage[]) => void;
}

export function useChatStream(paperId: string): UseChatStreamReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Load chat history on mount
  useEffect(() => {
    if (!paperId) return;

    chatApi.getHistory(paperId).then((history) => {
      setMessages(
        history.map((msg) => ({
          role: msg.role as 'user' | 'assistant',
          content: msg.content,
          timestamp: msg.timestamp,
        }))
      );
    });
  }, [paperId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isStreaming) return;

      // Add user message immediately
      const userMessage: ChatMessage = {
        role: 'user',
        content: content.trim(),
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      setIsStreaming(true);

      try {
        // Close any existing connection
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
        }

        const url = new URL(`/api/chat/${paperId}`, window.location.origin);
        url.searchParams.append('message', content.trim());
        const eventSource = new EventSource(url.toString());
        eventSourceRef.current = eventSource;

        let assistantContent = '';

        eventSource.onmessage = (event) => {
          if (event.data === '') {
            // Done
            eventSource.close();
            eventSourceRef.current = null;
            setIsStreaming(false);

            // Add assistant message
            const assistantMessage: ChatMessage = {
              role: 'assistant',
              content: assistantContent,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
          } else {
            assistantContent += event.data;
            // Update last message
            setMessages((prev) => {
              const updated = [...prev];
              if (updated.length > 0 && updated[updated.length - 1].role === 'user') {
                updated.push({
                  role: 'assistant',
                  content: assistantContent,
                  timestamp: new Date().toISOString(),
                });
              } else {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  content: assistantContent,
                };
              }
              return updated;
            });
          }
        };

        eventSource.onerror = () => {
          eventSource.close();
          eventSourceRef.current = null;
          setIsStreaming(false);
        };
      } catch (err) {
        setIsStreaming(false);
        console.error('Chat error:', err);
      }
    },
    [paperId, isStreaming]
  );

  const clearHistory = useCallback(async () => {
    if (!paperId) return;
    await chatApi.clearHistory(paperId);
    setMessages([]);
  }, [paperId]);

  return {
    messages,
    isStreaming,
    sendMessage,
    clearHistory,
    setMessages,
  };
}
