import React, { useState, useEffect } from 'react';

const STATUS_TEXTS = [
  "Processing query...",
  "Searching JumpOff Campus locations...",
  "Parsing school listings...",
  "Filtering by amenities...",
  "Generating verified website links...",
  "Formatting recommendations..."
];

export const TypingIndicator: React.FC = () => {
  const [textIndex, setTextIndex] = useState(0);
  const [fadeClass, setFadeClass] = useState('fade-in');

  useEffect(() => {
    const textInterval = setInterval(() => {
      // Transition out
      setFadeClass('fade-out');
      
      // Delay state switch slightly to allow fade out to conclude
      setTimeout(() => {
        setTextIndex((prev) => (prev + 1) % STATUS_TEXTS.length);
        setFadeClass('fade-in');
      }, 400); // 400ms delay matches fade animation time
    }, 2800);

    return () => clearInterval(textInterval);
  }, []);

  return (
    <div className="message-row assistant-row typing-indicator-row">
      <div className="message-container">
        <div className="message-avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
        </div>
        <div className="message-bubble typing-bubble">
          <div className="typing-dots">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
          </div>
          <span className={`typing-status-text ${fadeClass}`}>
            {STATUS_TEXTS[textIndex]}
          </span>
        </div>
      </div>
    </div>
  );
};
