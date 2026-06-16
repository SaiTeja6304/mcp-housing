import { useState, useRef, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { TypingIndicator } from './components/TypingIndicator';
import type { Message } from './types';
import { sendChatMessage } from './api';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isMcpConnected, setIsMcpConnected] = useState<'connected' | 'offline' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/health');
        if (res.ok) {
          const data = await res.json();
          if (data.status === 'connected') {
            setIsMcpConnected('connected');
            return;
          }
        }
        setIsMcpConnected('offline');
      } catch (err) {
        setIsMcpConnected('offline');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (text: string) => {
    setError(null);
    const userMsgId = Date.now().toString();
    const newUserMessage: Message = {
      id: userMsgId,
      role: 'user',
      content: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setIsLoading(true);

    try {
      // Map current messages to api history payload
      const historyPayload = messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      const responseText = await sendChatMessage(text, historyPayload);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: responseText,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Could not reach the chatbot backend. Please ensure the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setError(null);
    setIsLoading(false);
  };

  return (
    <div className="app-container">
      <Sidebar
        onNewChat={handleNewChat}
        onSelectSuggestion={handleSendMessage}
        isMcpConnected={isMcpConnected}
      />

      <main className="chat-area">
        {messages.length === 0 ? (
          <div className="welcome-container">
            <div className="welcome-header">
              <h1>Find Off-Campus Housing</h1>
              <p className="welcome-subtitle">
                Powered by the JumpOff Campus MCP server. Ask questions to find available universities, filter by rooms, price, and amenities.
              </p>
            </div>

            <div className="welcome-cards">
              <div className="welcome-card" onClick={() => handleSendMessage('List all housing locations')}>
                <div className="card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="2" y1="12" x2="22" y2="12" />
                    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                  </svg>
                </div>
                <h3>Explore Locations</h3>
                <p>Discover universities, cities, and slugs supported by JumpOff Campus.</p>
              </div>

              <div className="welcome-card" onClick={() => handleSendMessage('Find housing in Worcester under $1000')}>
                <div className="card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="12" y1="1" x2="12" y2="23" />
                    <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                  </svg>
                </div>
                <h3>Budget Search</h3>
                <p>Find affordable rooms, private apartments, and filter listings by prices.</p>
              </div>

              <div className="welcome-card" onClick={() => handleSendMessage('What community posts are available for Worcester?')}>
                <div className="card-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                  </svg>
                </div>
                <h3>Blogs &amp; Tips</h3>
                <p>Read helpful posts, renter guides, and community announcements.</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
            {error && (
              <div className="error-message-bubble">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="error-icon">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <span>{error}</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        <div className="input-area-container">
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          <div className="input-footer-text">
            JumpOff Campus Assistant may search listings and external links dynamically using MCP tools.
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
