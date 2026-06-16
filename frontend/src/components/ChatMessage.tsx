import React from 'react';
import type { Message } from '../types';
import { parseMarkdown } from '../utils/markdown';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}>
      <div className="message-container">
        <div className="message-avatar">
          {isUser ? (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
          )}
        </div>
        <div className="message-bubble">
          <div className="message-sender">
            {isUser ? 'You' : 'JumpOff Assistant'}
          </div>
          <div className="message-content">
            {parseMarkdown(message.content)}
          </div>
        </div>
      </div>
    </div>
  );
};
