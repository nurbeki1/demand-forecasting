import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

import { useAuth } from "../context/AuthContext";
import {
  sendChatMessage,
  getChatHistory,
  clearChatHistory,
  recalculateKZAnalysis,
} from "../api/chatApi";

import KZAnalysisCard from "../components/kz/KZAnalysisCard";

import "../styles/chat.css";

// ============================================
// TYPEWRITER ANIMATION COMPONENT
// ============================================
const TYPEWRITER_PHRASES = [
  "How can I help you today?",
  "Ask anything, I'm ready.",
  "Let's build something great.",
  "Search, write, analyze, create.",
  "Your AI workspace starts here.",
];

function TypewriterText() {
  const [displayText, setDisplayText] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const currentPhrase = TYPEWRITER_PHRASES[phraseIndex];

    if (isPaused) {
      const pauseTimer = setTimeout(() => {
        setIsPaused(false);
        setIsDeleting(true);
      }, 2000);
      return () => clearTimeout(pauseTimer);
    }

    const typeSpeed = isDeleting ? 30 : 50;

    const timer = setTimeout(() => {
      if (!isDeleting) {
        // Typing
        if (displayText.length < currentPhrase.length) {
          setDisplayText(currentPhrase.slice(0, displayText.length + 1));
        } else {
          setIsPaused(true);
        }
      } else {
        // Deleting
        if (displayText.length > 0) {
          setDisplayText(displayText.slice(0, -1));
        } else {
          setIsDeleting(false);
          setPhraseIndex((prev) => (prev + 1) % TYPEWRITER_PHRASES.length);
        }
      }
    }, typeSpeed);

    return () => clearTimeout(timer);
  }, [displayText, phraseIndex, isDeleting, isPaused]);

  return (
    <div className="typewriter">
      <span className="typewriter-text">{displayText}</span>
      <span className="typewriter-cursor">|</span>
    </div>
  );
}

// ============================================
// MARKDOWN RENDERER
// ============================================
function renderMarkdown(text) {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];
  let inList = false;
  let listItems = [];
  let inTable = false;
  let tableRows = [];
  let tableHeader = null;

  const flushList = (idx) => {
    if (inList && listItems.length > 0) {
      elements.push(<ul key={`list-${idx}`} className="md-list">{listItems}</ul>);
      listItems = [];
      inList = false;
    }
  };

  const flushTable = (idx) => {
    if (inTable && tableRows.length > 0) {
      elements.push(
        <div key={`table-wrap-${idx}`} className="md-table-wrapper">
          <table className="md-table">
            {tableHeader && (
              <thead>
                <tr>
                  {tableHeader.map((cell, i) => (
                    <th key={i}>{processInline(cell.trim())}</th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody>
              {tableRows.map((row, rowIdx) => (
                <tr key={rowIdx} className={row.some(c => c.includes('🟢')) ? 'row-success' : row.some(c => c.includes('🔴')) ? 'row-danger' : row.some(c => c.includes('🟡')) ? 'row-warning' : ''}>
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx}>{processInline(cell.trim())}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
      tableRows = [];
      tableHeader = null;
      inTable = false;
    }
  };

  lines.forEach((line, idx) => {
    // Check for table row (starts and ends with |)
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      flushList(idx);

      // Parse cells
      const cells = line.trim().slice(1, -1).split('|');

      // Check if it's a separator row (|---|---|)
      if (cells.every(c => /^[\s:-]+$/.test(c))) {
        // This is the separator, skip it but mark we're in table
        inTable = true;
        return;
      }

      if (!inTable && !tableHeader) {
        // First row is header
        tableHeader = cells;
        inTable = true;
      } else {
        // Data row
        tableRows.push(cells);
      }
      return;
    }

    // If we were in a table but this line isn't a table row, flush the table
    if (inTable) {
      flushTable(idx);
    }

    if (line.startsWith('### ')) {
      flushList(idx);
      elements.push(<h4 key={idx} className="md-h3">{processInline(line.slice(4))}</h4>);
    } else if (line.startsWith('## ')) {
      flushList(idx);
      elements.push(<h3 key={idx} className="md-h2">{processInline(line.slice(3))}</h3>);
    } else if (line.startsWith('# ')) {
      flushList(idx);
      elements.push(<h2 key={idx} className="md-h1">{processInline(line.slice(2))}</h2>);
    } else if (line.match(/^[-*]\s/)) {
      inList = true;
      listItems.push(<li key={idx}>{processInline(line.slice(2))}</li>);
    } else if (line.match(/^\d+\.\s/)) {
      inList = true;
      listItems.push(<li key={idx}>{processInline(line.replace(/^\d+\.\s/, ''))}</li>);
    } else if (line === '---') {
      flushList(idx);
      elements.push(<hr key={idx} className="md-divider" />);
    } else if (line.trim() === '') {
      flushList(idx);
    } else {
      flushList(idx);
      elements.push(<p key={idx} className="md-p">{processInline(line)}</p>);
    }
  });

  // Flush remaining content
  if (inList && listItems.length > 0) {
    elements.push(<ul key="list-final" className="md-list">{listItems}</ul>);
  }
  if (inTable && tableRows.length > 0) {
    flushTable('final');
  }

  return elements;
}

function processInline(text) {
  if (!text) return text;

  const parts = [];
  const boldRegex = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let match;
  let key = 0;

  while ((match = boldRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    parts.push(<strong key={`bold-${key++}`}>{match[1]}</strong>);
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

// ============================================
// PRODUCT COMPONENTS
// ============================================
function ProductCard({ product }) {
  return (
    <div className="product-card">
      <div className="product-image-container">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="product-image"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="product-image-placeholder" style={{ display: product.image_url ? 'none' : 'flex' }}>
          <span>📦</span>
        </div>
      </div>
      <div className="product-info">
        <div className="product-name">{product.name}</div>
        <div className="product-price">
          {product.price > 0 ? `₹${product.price.toLocaleString()}` : 'Price N/A'}
        </div>
        {product.rating > 0 && (
          <div className="product-rating">
            <span className="stars">{'★'.repeat(Math.round(product.rating))}</span>
            <span className="rating-value">{product.rating.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

function ProductCarousel({ images }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!images || images.length === 0) return null;

  return (
    <div className="product-carousel">
      <div className="carousel-header">
        <span className="carousel-title">Products ({images.length})</span>
        <div className="carousel-nav">
          <button
            className="carousel-btn"
            onClick={() => setCurrentIndex(prev => prev === 0 ? images.length - 1 : prev - 1)}
          >
            ‹
          </button>
          <span className="carousel-counter">{currentIndex + 1} / {images.length}</span>
          <button
            className="carousel-btn"
            onClick={() => setCurrentIndex(prev => prev === images.length - 1 ? 0 : prev + 1)}
          >
            ›
          </button>
        </div>
      </div>
      <ProductCard product={images[currentIndex]} />
    </div>
  );
}

function MiniChart({ data }) {
  if (!data?.history && !data?.forecast) return null;

  const historyData = (data.history || []).slice(-7).map((h) => ({
    name: h.date?.split('-').slice(1).join('/') || '',
    history: h.demand,
  }));

  const forecastData = (data.forecast || []).slice(0, 7).map((f) => ({
    name: f.date?.split('-').slice(1).join('/') || '',
    forecast: f.predicted_demand,
  }));

  const combined = [...historyData];
  if (historyData.length > 0 && forecastData.length > 0) {
    combined[combined.length - 1].forecast = combined[combined.length - 1].history;
  }
  forecastData.forEach(f => combined.push(f));

  if (combined.length === 0) return null;

  const avgHistory = historyData.length > 0
    ? historyData.reduce((a, b) => a + (b.history || 0), 0) / historyData.length
    : 0;
  const avgForecast = forecastData.length > 0
    ? forecastData.reduce((a, b) => a + (b.forecast || 0), 0) / forecastData.length
    : 0;
  const trendPercent = avgHistory > 0 ? ((avgForecast - avgHistory) / avgHistory * 100).toFixed(1) : 0;
  const trendUp = avgForecast >= avgHistory;

  return (
    <div className="mini-chart">
      <div className="mini-chart-header">
        <span>Demand Forecast</span>
        <span className={`trend-badge ${trendUp ? 'up' : 'down'}`}>
          {trendUp ? '↑' : '↓'} {Math.abs(trendPercent)}%
        </span>
      </div>
      <ResponsiveContainer width="100%" height={160}>
        <LineChart data={combined} margin={{ top: 10, right: 10, bottom: 5, left: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#6b7280' }} />
          <YAxis tick={{ fontSize: 11, fill: '#6b7280' }} width={40} />
          <Tooltip
            contentStyle={{
              background: '#1e1e2e',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              fontSize: 12
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Line type="monotone" dataKey="history" stroke="#60a5fa" strokeWidth={2} dot={{ r: 3 }} name="History" />
          <Line type="monotone" dataKey="forecast" stroke="#34d399" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 3 }} name="Forecast" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ============================================
// CONVERSATION HELPERS
// ============================================
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function getConversations() {
  try {
    return JSON.parse(localStorage.getItem('chat_conversations') || '[]');
  } catch {
    return [];
  }
}

function saveConversations(conversations) {
  localStorage.setItem('chat_conversations', JSON.stringify(conversations));
}

function getCurrentConversationId() {
  return localStorage.getItem('current_conversation_id');
}

function setCurrentConversationId(id) {
  if (id) {
    localStorage.setItem('current_conversation_id', id);
  } else {
    localStorage.removeItem('current_conversation_id');
  }
}

// ============================================
// CHAT SIDEBAR COMPONENT (Conversation History)
// ============================================
function ChatSidebar({
  isOpen,
  onClose,
  conversations,
  currentConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  user,
  onLogout
}) {
  return (
    <>
      {/* Mobile Overlay */}
      <div
        className={`chat-sidebar-overlay ${isOpen ? 'visible' : ''}`}
        onClick={onClose}
      />

      {/* Chat Sidebar */}
      <aside className={`chat-sidebar ${isOpen ? 'open' : ''}`}>
        {/* Logo Section */}
        <div className="chat-sidebar-header">
          <div className="chat-sidebar-logo">
            <div className="logo-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
              </svg>
            </div>
            <span className="logo-text">Chat History</span>
          </div>
          <button className="chat-sidebar-close-btn" onClick={onClose}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 18l-6-6 6-6"/>
            </svg>
          </button>
        </div>

        {/* New Chat Button */}
        <button className="new-chat-btn" onClick={onNewChat}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>New Chat</span>
        </button>

        {/* Projects Section */}
        <div className="chat-sidebar-section">
          <div className="section-title">Projects</div>
          <div className="chat-list">
            <div className="chat-item">
              <button className="chat-item-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span className="chat-item-title">Demand Forecasting</span>
              </button>
            </div>
            <div className="chat-item">
              <button className="chat-item-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span className="chat-item-title">Analytics</span>
              </button>
            </div>
          </div>
        </div>

        {/* Recent Chats */}
        <div className="chat-sidebar-section">
          <div className="section-title">Recent Chats</div>
          <div className="chat-list">
            {conversations.length === 0 ? (
              <div className="empty-chats">
                <span>No conversations yet</span>
              </div>
            ) : (
              conversations.slice(0, 10).map(conv => (
                <div
                  key={conv.id}
                  className={`chat-item ${conv.id === currentConversationId ? 'active' : ''}`}
                >
                  <button
                    className="chat-item-btn"
                    onClick={() => onSelectConversation(conv.id)}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    <span className="chat-item-title">{conv.title || 'New Chat'}</span>
                  </button>
                  <button
                    className="chat-item-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteConversation(conv.id);
                    }}
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Spacer */}
        <div className="chat-sidebar-spacer" />

        {/* Settings */}
        <div className="chat-sidebar-section">
          <button className="chat-sidebar-menu-item">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
            <span>Settings</span>
          </button>
        </div>

        {/* Coming Soon Section */}
        <div className="chat-sidebar-section chat-sidebar-soon">
          <div className="section-title">Coming Soon</div>
          <div className="soon-items">
            <div className="soon-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                <line x1="12" y1="22.08" x2="12" y2="12"/>
              </svg>
              <span>Plugins</span>
            </div>
            <div className="soon-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                <line x1="9" y1="9" x2="9.01" y2="9"/>
                <line x1="15" y1="9" x2="15.01" y2="9"/>
              </svg>
              <span>Custom GPTs</span>
            </div>
            <div className="soon-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="9" y1="21" x2="9" y2="9"/>
              </svg>
              <span>Workspaces</span>
            </div>
          </div>
        </div>

        {/* User info with logout */}
        <div className="chat-sidebar-user">
          <div className="user-avatar">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <span className="user-email">{user?.email || 'User'}</span>
          </div>
          <button className="logout-btn" onClick={onLogout} title="Выйти">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </aside>
    </>
  );
}

// ============================================
// MAIN CHAT PAGE COMPONENT
// ============================================
export default function ChatPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  // UI state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationIdState] = useState(null);

  // Voice recording state
  const [isRecording, setIsRecording] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);
  const recognitionRef = useRef(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Determine if we're in "empty state" (no messages yet)
  const isEmptyState = messages.length === 0;

  // Initialize
  useEffect(() => {
    const savedConversations = getConversations();
    setConversations(savedConversations);

    const currentId = getCurrentConversationId();
    if (currentId && savedConversations.find(c => c.id === currentId)) {
      loadConversation(currentId, savedConversations);
    }

    // Check for prefilled prompt from other pages (e.g., ChartsPage)
    const prefillPrompt = sessionStorage.getItem("chat_prefill");
    if (prefillPrompt) {
      setInputValue(prefillPrompt);
      sessionStorage.removeItem("chat_prefill");
      // Focus input
      setTimeout(() => inputRef.current?.focus(), 100);
    }

    // Open sidebar by default on desktop
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(true);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);

    // Check for speech recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
    }

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadConversation = useCallback((conversationId, convList = conversations) => {
    const conv = convList.find(c => c.id === conversationId);
    if (conv) {
      setMessages(conv.messages || []);
      setCurrentConversationIdState(conversationId);
      setCurrentConversationId(conversationId);
    }
  }, [conversations]);

  const saveCurrentConversation = useCallback((newMessages, title = null) => {
    const convId = currentConversationId || generateId();

    const updatedConversations = [...conversations];
    const existingIndex = updatedConversations.findIndex(c => c.id === convId);

    const conversationData = {
      id: convId,
      title: title || (newMessages.find(m => m.role === 'user')?.content?.slice(0, 40) || 'New Chat'),
      messages: newMessages,
      updatedAt: new Date().toISOString(),
    };

    if (existingIndex >= 0) {
      updatedConversations[existingIndex] = conversationData;
    } else {
      updatedConversations.unshift(conversationData);
    }

    setConversations(updatedConversations);
    saveConversations(updatedConversations);
    setCurrentConversationIdState(convId);
    setCurrentConversationId(convId);
  }, [currentConversationId, conversations]);

  const handleNewChat = async () => {
    try {
      await clearChatHistory();
    } catch (e) {
      console.error("Failed to clear backend history");
    }

    setMessages([]);
    setCurrentConversationIdState(null);
    setCurrentConversationId(null);
    inputRef.current?.focus();

    // Close sidebar on mobile
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  const handleSelectConversation = (conversationId) => {
    loadConversation(conversationId);
    if (window.innerWidth < 1024) {
      setSidebarOpen(false);
    }
  };

  const handleDeleteConversation = (conversationId) => {
    const updated = conversations.filter(c => c.id !== conversationId);
    setConversations(updated);
    saveConversations(updated);

    if (conversationId === currentConversationId) {
      handleNewChat();
    }
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || loading) return;

    const userMessage = { role: "user", content: text };
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue("");
    setLoading(true);

    try {
      const response = await sendChatMessage(text);
      const assistantMessage = {
        role: "assistant",
        content: response.reply,
        intent: response.intent,
        response_type: response.response_type,
        images: response.images,
        data: response.data,
        suggested_questions: response.suggested_questions,
        available_details: response.available_details,
      };
      const finalMessages = [...newMessages, assistantMessage];
      setMessages(finalMessages);
      saveCurrentConversation(finalMessages);
    } catch (e) {
      const errorMessages = [...newMessages, {
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
      }];
      setMessages(errorMessages);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Handle KZ analysis recalculation with new markup
  const handleKZRecalculate = async (markup, originalMessage) => {
    if (!originalMessage?.data?.product_name) return;

    try {
      const response = await recalculateKZAnalysis(
        originalMessage.data.product_name,
        markup
      );

      // Update the message with new data
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg === originalMessage
            ? { ...msg, data: { ...response, markup_percent: markup } }
            : msg
        )
      );

      // Save updated conversation
      const updatedMessages = messages.map((msg) =>
        msg === originalMessage
          ? { ...msg, data: { ...response, markup_percent: markup } }
          : msg
      );
      saveCurrentConversation(updatedMessages);
    } catch (error) {
      console.error("Failed to recalculate KZ analysis:", error);
    }
  };

  // Voice recording functions
  const startRecording = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in your browser. Please use Chrome or Edge.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'ru-RU'; // Default to Russian, can be changed

    let finalTranscript = inputValue;

    recognition.onresult = (event) => {
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }
      setInputValue(finalTranscript + interimTranscript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsRecording(false);
      if (event.error === 'not-allowed') {
        alert("Microphone access denied. Please allow microphone access in your browser settings.");
      }
    };

    recognition.onend = () => {
      setIsRecording(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsRecording(false);
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const toggleSidebar = () => {
    setSidebarOpen(prev => !prev);
  };

  return (
    <div className="chat-app-container">
      {/* Chat Area - No global sidebar for regular users */}
      <div className="chat-app">
        <ChatSidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          conversations={conversations}
          currentConversationId={currentConversationId}
          onNewChat={handleNewChat}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          user={user}
          onLogout={handleLogout}
        />

        <main className="chat-main">
        {/* Header - Only show in chat mode */}
        {!isEmptyState && (
          <header className="chat-header">
            <div className="header-left">
              <button className="menu-toggle" onClick={toggleSidebar}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="3" y1="12" x2="21" y2="12"/>
                  <line x1="3" y1="6" x2="21" y2="6"/>
                  <line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
              </button>
              <span className="header-title">AI Assistant</span>
            </div>
          </header>
        )}

        {/* Content Area */}
        <div className={`chat-content ${isEmptyState ? 'empty-state' : ''}`}>
          {isEmptyState ? (
            /* ============================================
               EMPTY STATE - Centered Layout
               ============================================ */
            <div className="empty-container">
              {/* Menu toggle for empty state */}
              <button className="empty-menu-toggle" onClick={toggleSidebar}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="3" y1="12" x2="21" y2="12"/>
                  <line x1="3" y1="6" x2="21" y2="6"/>
                  <line x1="3" y1="18" x2="21" y2="18"/>
                </svg>
              </button>

              <div className="empty-content">
                {/* Logo */}
                <div className="empty-logo">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                  </svg>
                </div>

                {/* Typewriter Animation */}
                <TypewriterText />

                {/* Centered Input */}
                <div className="empty-input-wrapper">
                  <div className="empty-input-box">
                    <input
                      ref={inputRef}
                      type="text"
                      className="empty-input"
                      placeholder="Ask anything..."
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={loading || isRecording}
                      autoFocus
                    />
                    {/* Microphone Button */}
                    {speechSupported && (
                      <button
                        className={`mic-btn ${isRecording ? 'recording' : ''}`}
                        onClick={toggleRecording}
                        disabled={loading}
                        title={isRecording ? "Stop recording" : "Start voice input"}
                      >
                        {isRecording ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="6" y="6" width="12" height="12" rx="2" />
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                            <line x1="12" y1="19" x2="12" y2="23"/>
                            <line x1="8" y1="23" x2="16" y2="23"/>
                          </svg>
                        )}
                      </button>
                    )}
                    <button
                      className="empty-send-btn"
                      onClick={handleSend}
                      disabled={loading || !inputValue.trim()}
                    >
                      {loading ? (
                        <div className="send-spinner" />
                      ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="22" y1="2" x2="11" y2="13"/>
                          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                        </svg>
                      )}
                    </button>
                  </div>
                  <p className="empty-disclaimer">AI can make mistakes. Verify important information.</p>
                </div>

                {/* Quick suggestions */}
                <div className="empty-suggestions">
                  {["Top products", "Sales forecast", "Trending items", "Compare products"].map((s, idx) => (
                    <button
                      key={idx}
                      className="suggestion-chip"
                      onClick={() => {
                        setInputValue(s);
                        inputRef.current?.focus();
                      }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            /* ============================================
               CHAT STATE - Messages Layout
               ============================================ */
            <>
              <div className="messages-container">
                <div className="messages-inner">
                  {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.role}`}>
                      <div className="message-avatar">
                        {msg.role === "user" ? (
                          <span>{user?.email?.[0]?.toUpperCase() || 'U'}</span>
                        ) : (
                          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                          </svg>
                        )}
                      </div>
                      <div className="message-content">
                        <div className="message-role">
                          {msg.role === "user" ? "You" : "AI Assistant"}
                        </div>
                        <div className="message-text">
                          {renderMarkdown(msg.content)}
                        </div>
                        {msg.images && msg.images.length > 0 && (
                          <ProductCarousel images={msg.images} />
                        )}
                        {msg.data && !msg.response_type?.startsWith('kz_') && <MiniChart data={msg.data} />}
                        {msg.response_type?.startsWith('kz_') && msg.data && msg.response_type !== 'error' && (
                          <KZAnalysisCard
                            data={msg.data}
                            onMarkupChange={(markup) => handleKZRecalculate(markup, msg)}
                            responseType={msg.response_type}
                          />
                        )}
                        {/* Suggested Questions for Progressive Disclosure */}
                        {msg.role === 'assistant' && msg.suggested_questions && msg.suggested_questions.length > 0 && (
                          <div className="suggested-questions">
                            {msg.suggested_questions.slice(0, 4).map((sq, sqIdx) => (
                              <button
                                key={sqIdx}
                                className="suggested-question-btn"
                                onClick={() => {
                                  setInputValue(sq.prompt || sq.text);
                                  setTimeout(() => handleSend(), 100);
                                }}
                              >
                                {sq.text}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Loading indicator */}
                  {loading && (
                    <div className="message assistant">
                      <div className="message-avatar">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                        </svg>
                      </div>
                      <div className="message-content">
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

              {/* Bottom Input */}
              <div className="chat-input-area">
                <div className="chat-input-wrapper">
                  <div className="chat-input-box">
                    <input
                      ref={inputRef}
                      type="text"
                      className="chat-input"
                      placeholder="Type a message..."
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      disabled={loading || isRecording}
                    />
                    {/* Microphone Button */}
                    {speechSupported && (
                      <button
                        className={`mic-btn ${isRecording ? 'recording' : ''}`}
                        onClick={toggleRecording}
                        disabled={loading}
                        title={isRecording ? "Stop recording" : "Start voice input"}
                      >
                        {isRecording ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                            <rect x="6" y="6" width="12" height="12" rx="2" />
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                            <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                            <line x1="12" y1="19" x2="12" y2="23"/>
                            <line x1="8" y1="23" x2="16" y2="23"/>
                          </svg>
                        )}
                      </button>
                    )}
                    <button
                      className="send-btn"
                      onClick={handleSend}
                      disabled={loading || !inputValue.trim()}
                    >
                      {loading ? (
                        <div className="send-spinner" />
                      ) : (
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <line x1="22" y1="2" x2="11" y2="13"/>
                          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
      </div>
    </div>
  );
}