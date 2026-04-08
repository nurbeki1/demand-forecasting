import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
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
import SettingsPanel from "../components/settings/SettingsPanel";

import "../styles/chat.css";

// ============================================
// TYPEWRITER ANIMATION COMPONENT
// ============================================
const getTypewriterPhrases = (t) => [
  t('chat.welcome'),
  t('chat.askAnything'),
  t('chat.aiDisclaimer'),
];

function TypewriterText() {
  const { t } = useTranslation();
  const [displayText, setDisplayText] = useState("");
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const phrases = getTypewriterPhrases(t);

  useEffect(() => {
    const currentPhrase = phrases[phraseIndex];

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
          setPhraseIndex((prev) => (prev + 1) % phrases.length);
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
function ProductCard({ product, t }) {
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
          {product.price > 0 ? `₹${product.price.toLocaleString()}` : t('common.noData')}
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

function ProductCarousel({ images, t }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!images || images.length === 0) return null;

  return (
    <div className="product-carousel">
      <div className="carousel-header">
        <span className="carousel-title">{t('dashboard.products')} ({images.length})</span>
        <div className="carousel-nav">
          <button
            className="carousel-btn"
            aria-label={t('common.previous')}
            onClick={() => setCurrentIndex(prev => prev === 0 ? images.length - 1 : prev - 1)}
          >
            ‹
          </button>
          <span className="carousel-counter">{currentIndex + 1} / {images.length}</span>
          <button
            className="carousel-btn"
            aria-label={t('common.next')}
            onClick={() => setCurrentIndex(prev => prev === images.length - 1 ? 0 : prev + 1)}
          >
            ›
          </button>
        </div>
      </div>
      <ProductCard product={images[currentIndex]} t={t} />
    </div>
  );
}

function MiniChart({ data, t }) {
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
        <span>{t('chart.demandForecast')}</span>
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
          <Line type="monotone" dataKey="history" stroke="#60a5fa" strokeWidth={2} dot={{ r: 3 }} name={t('forecast.history')} />
          <Line type="monotone" dataKey="forecast" stroke="#34d399" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 3 }} name={t('forecast.result')} />
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
  isExpanded,
  onToggle,
  conversations,
  currentConversationId,
  onNewChat,
  onSelectConversation,
  onDeleteConversation,
  user,
  onLogout,
  onShowSettings,
  t
}) {
  return (
    <aside className={`chat-sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}>
      {/* Logo / Toggle Button */}
      <div className="sidebar-top">
        <button className="sidebar-logo-btn" onClick={onToggle} title={isExpanded ? t('common.close') : t('common.open')} aria-label={isExpanded ? t('common.close') : t('common.open')}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </button>

        {/* New Chat */}
        <button className="sidebar-icon-btn" onClick={onNewChat} title={t('chat.newChat')} aria-label={t('chat.newChat')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 20h9"/>
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
          </svg>
          <span>{t('chat.newChat')}</span>
        </button>

        {/* Search */}
        <button className="sidebar-icon-btn" title={t('common.search')} aria-label={t('common.search')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          <span>{t('common.search')}</span>
        </button>

        {/* Projects */}
        <button className="sidebar-icon-btn" title={t('chat.projects')} aria-label={t('chat.projects')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          <span>{t('chat.projects')}</span>
        </button>

        {/* Chat History */}
        <button className="sidebar-icon-btn" title={t('chat.chatHistory')} aria-label={t('chat.chatHistory')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span>{t('chat.chatHistory')}</span>
        </button>
      </div>

      {/* Expanded Content - Recent Chats (always rendered, hidden via CSS) */}
      <div className="sidebar-expanded-content">
        <div className="section-title">{t('chat.recentChats')}</div>
        <div className="chat-list">
          {conversations.length === 0 ? (
            <div className="empty-chats">
              <span>{t('chat.noConversations')}</span>
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
                  <span className="chat-item-title">{conv.title || t('chat.newChat')}</span>
                </button>
                <button
                  className="chat-item-delete"
                  aria-label={t('common.delete')}
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

      {/* Bottom Icons */}
      <div className="sidebar-bottom">
        {/* Settings */}
        <button className="sidebar-icon-btn" onClick={onShowSettings} title={t('chat.settings')} aria-label={t('chat.settings')}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
          <span>{t('chat.settings')}</span>
        </button>

        {/* User Avatar with Logout */}
        <div className="sidebar-user-row">
          <div className="user-avatar-small">
            {user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <span className="user-email-small">{user?.email || 'User'}</span>
          <button className="sidebar-logout-btn" onClick={onLogout} title={t('nav.logout')} aria-label={t('nav.logout')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  );
}

// ============================================
// MAIN CHAT PAGE COMPONENT
// ============================================
export default function ChatPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);

  // UI state
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationIdState] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

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

    // Keep sidebar collapsed by default
    const handleResize = () => {
      // Sidebar starts collapsed, user can expand it
    };
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
      setSidebarExpanded(false);
    }
  };

  const handleSelectConversation = (conversationId) => {
    loadConversation(conversationId);
    if (window.innerWidth < 1024) {
      setSidebarExpanded(false);
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
      const response = await sendChatMessage(text, i18n.language);
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
        content: t('auth.serverError'),
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
      alert(t('chat.speechNotSupported'));
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    // Set language based on current i18n language
    const langMap = { kk: 'kk-KZ', ru: 'ru-RU', en: 'en-US' };
    recognition.lang = langMap[i18n.language] || 'kk-KZ';

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
        alert(t('chat.microphoneDenied'));
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
    setSidebarExpanded(prev => !prev);
  };

  return (
    <div className="chat-app-container">
      {/* Chat Area - No global sidebar for regular users */}
      <div className="chat-app">
        {/* Mobile overlay when sidebar is expanded */}
        <div
          className={`sidebar-overlay ${sidebarExpanded ? 'visible' : ''}`}
          onClick={() => setSidebarExpanded(false)}
        />

        <ChatSidebar
          isExpanded={sidebarExpanded}
          onToggle={toggleSidebar}
          conversations={conversations}
          currentConversationId={currentConversationId}
          onNewChat={handleNewChat}
          onSelectConversation={handleSelectConversation}
          onDeleteConversation={handleDeleteConversation}
          user={user}
          onLogout={handleLogout}
          onShowSettings={() => {
            setShowSettings(true);
          }}
          t={t}
        />

        <main className="chat-main">
        {/* Settings View */}
        {showSettings ? (
          <SettingsPanel onClose={() => setShowSettings(false)} />
        ) : (
          <>
        {/* Header - Only show in chat mode */}
        {!isEmptyState && (
          <header className="chat-header">
            <div className="header-left">
              <span className="header-title">{t('chat.aiAssistant')}</span>
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
                      placeholder={t('chat.askAnything')}
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
                        title={isRecording ? t('chat.stopRecording') : t('chat.voiceInput')}
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
                  <p className="empty-disclaimer">{t('chat.aiDisclaimer')}</p>
                </div>

                {/* Quick suggestions */}
                <div className="empty-suggestions">
                  {[t('chat.topProducts'), t('chat.salesForecast'), t('chat.trendingItems'), t('chat.compareProducts')].map((s, idx) => (
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
                          {msg.role === "user" ? t('chat.you') : t('chat.aiAssistant')}
                        </div>
                        <div className="message-text">
                          {renderMarkdown(msg.content)}
                        </div>
                        {msg.images && msg.images.length > 0 && (
                          <ProductCarousel images={msg.images} t={t} />
                        )}
                        {msg.data && !msg.response_type?.startsWith('kz_') && <MiniChart data={msg.data} t={t} />}
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
                      placeholder={t('chat.typeMessage')}
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
                        title={isRecording ? t('chat.stopRecording') : t('chat.voiceInput')}
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
        </>
        )}
      </main>
      </div>
    </div>
  );
}