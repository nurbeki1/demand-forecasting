import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { useAuth } from "../context/AuthContext";
import { API_URL } from "../config";

const SUGGESTIONS = [
  "What can you help me with?",
  "Tell me about demand forecasting",
  "How does AI prediction work?",
  "Analyze market trends",
];

export default function ChatPage() {
  const { user, logout, getToken } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    adjustTextareaHeight();
  }, [input]);

  function scrollToBottom() {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  function adjustTextareaHeight() {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "24px";
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + "px";
    }
  }

  async function loadHistory() {
    try {
      const res = await fetch(`${API_URL}/chat/history?limit=50`, {
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
          setMessages(data.messages.reverse());
        }
      }
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setHistoryLoaded(true);
    }
  }

  async function sendMessage(text) {
    if (!text.trim() || loading) return;

    const userMessage = {
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error("Failed to send message");
      }

      const data = await res.json();

      const assistantMessage = {
        role: "assistant",
        content: data.response || data.message || "I received your message.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("Chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.",
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  }

  function handleSuggestionClick(suggestion) {
    sendMessage(suggestion);
  }

  async function clearHistory() {
    try {
      await fetch(`${API_URL}/chat/history`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${getToken()}` },
      });
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear history:", err);
    }
  }

  return (
    <div className="chat-container">
      {/* Header */}
      <header className="chat-header">
        <div className="chat-header-left">
          <div className="chat-logo">
            <span style={{ color: "white", fontSize: "14px", fontWeight: 600 }}>AI</span>
          </div>
          <h1 className="chat-title">AI Chat</h1>
        </div>
        <div className="chat-header-right">
          <div className="user-menu">
            <span className="user-email">{user?.email}</span>
          </div>
          {messages.length > 0 && (
            <button className="btn-icon" onClick={clearHistory} title="Clear chat">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14z" />
              </svg>
            </button>
          )}
          <button className="btn-icon" onClick={logout} title="Sign out">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" />
            </svg>
          </button>
        </div>
      </header>

      {/* Messages */}
      {messages.length === 0 && historyLoaded ? (
        <div className="chat-empty">
          <div className="chat-empty-icon">
            <span>AI</span>
          </div>
          <h2 className="chat-empty-title">How can I help you today?</h2>
          <p className="chat-empty-text">
            Ask me anything about demand forecasting, market analysis, or data insights.
          </p>
          <div className="suggestions">
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(s)}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="chat-messages">
          <div className="messages-inner">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                <div className="message-avatar">
                  {msg.role === "user" ? (
                    <span>{user?.email?.[0]?.toUpperCase() || "U"}</span>
                  ) : (
                    <span>AI</span>
                  )}
                </div>
                <div className="message-content">
                  <div className="message-author">
                    {msg.role === "user" ? "You" : "AI Assistant"}
                  </div>
                  <div className="message-text">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message message-assistant">
                <div className="message-avatar">
                  <span>AI</span>
                </div>
                <div className="message-content">
                  <div className="message-author">AI Assistant</div>
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Input */}
      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <div className="chat-input-box">
            <textarea
              ref={textareaRef}
              className="chat-textarea"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message AI..."
              rows={1}
              disabled={loading}
            />
            <button
              className="send-button"
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            </button>
          </div>
          <p className="chat-footer-text">
            AI can make mistakes. Verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}