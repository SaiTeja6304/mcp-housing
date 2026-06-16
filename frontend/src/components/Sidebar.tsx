import React from 'react';

interface SidebarProps {
  onNewChat: () => void;
  onSelectSuggestion: (text: string) => void;
  isMcpConnected: 'connected' | 'offline' | 'checking';
}

export const Sidebar: React.FC<SidebarProps> = ({ onNewChat, onSelectSuggestion, isMcpConnected }) => {
  const suggestions = [
    "List all housing locations",
    "Find housing in Worcester under $1000",
    "Show listings in Worcester with laundry",
    "What community posts are available for Worcester?",
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="logo-icon">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
          </svg>
          <h2>JumpOff Campus</h2>
        </div>
        <button onClick={onNewChat} className="new-chat-btn">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="plus-icon">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Chat
        </button>
      </div>

      <div className="sidebar-content">
        <div className="suggestions-section">
          <h3>Quick Prompts</h3>
          <div className="suggestions-list">
            {suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onSelectSuggestion(suggestion)}
                className="suggestion-item"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className={`status-dot dot-${isMcpConnected}`}></span>
          {isMcpConnected === 'connected' ? 'MCP Server Connected' :
           isMcpConnected === 'offline' ? 'MCP Server Offline' : 'Checking server...'}
        </div>
      </div>
    </aside>
  );
};
