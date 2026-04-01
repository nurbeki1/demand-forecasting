import { useState, useEffect, useRef } from "react";
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
} from "../api/chatApi";

import "../styles/chat.css";

// Simple Markdown-like renderer
function renderMarkdown(text) {
  if (!text) return null;

  const lines = text.split('\n');
  const elements = [];
  let inList = false;
  let listItems = [];

  lines.forEach((line, idx) => {
    if (line.startsWith('### ')) {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<h4 key={idx} className="mdH3">{processInline(line.slice(4))}</h4>);
    } else if (line.startsWith('## ')) {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<h3 key={idx} className="mdH2">{processInline(line.slice(3))}</h3>);
    } else if (line.startsWith('# ')) {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<h2 key={idx} className="mdH1">{processInline(line.slice(2))}</h2>);
    }
    else if (line.match(/^[-*]\s/)) {
      inList = true;
      listItems.push(<li key={idx}>{processInline(line.slice(2))}</li>);
    } else if (line.match(/^\d+\.\s/)) {
      inList = true;
      listItems.push(<li key={idx}>{processInline(line.replace(/^\d+\.\s/, ''))}</li>);
    }
    else if (line.trim() === '') {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<br key={idx} />);
    }
    else {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<p key={idx} className="mdP">{processInline(line)}</p>);
    }
  });

  if (inList && listItems.length > 0) {
    elements.push(<ul key="list-final" className="mdList">{listItems}</ul>);
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

// Trend Badge
function TrendBadge({ trend }) {
  if (!trend) return null;

  const { direction, percent, alert } = trend;

  const getTrendColor = () => {
    if (alert === 'hot') return 'hot';
    if (alert === 'critical') return 'critical';
    if (alert === 'warning') return 'warning';
    if (direction === 'rising') return 'rising';
    if (direction === 'declining' || direction === 'critical') return 'declining';
    return 'stable';
  };

  const getTrendIcon = () => {
    if (alert === 'hot') return '🔥';
    if (alert === 'critical') return '🚨';
    if (alert === 'warning') return '⚠️';
    if (direction === 'rising') return '📈';
    if (direction === 'declining') return '📉';
    return '➖';
  };

  return (
    <div className={`trendBadgeProduct ${getTrendColor()}`}>
      <span className="trendIcon">{getTrendIcon()}</span>
      <span className="trendPercent">
        {percent > 0 ? '+' : ''}{percent?.toFixed(1)}%
      </span>
    </div>
  );
}

// Product Card
function ProductCard({ product }) {
  return (
    <div className="productCard">
      {product.trend && <TrendBadge trend={product.trend} />}

      <div className="productImageContainer">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="productImage"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="productImagePlaceholder" style={{ display: product.image_url ? 'none' : 'flex' }}>
          <span>📦</span>
        </div>
      </div>
      <div className="productInfo">
        <div className="productName">{product.name}</div>
        <div className="productPrice">
          {product.price > 0 ? `₹${product.price.toLocaleString()}` : 'Price N/A'}
        </div>
        {product.rating > 0 && (
          <div className="productRating">
            <span className="stars">{'★'.repeat(Math.round(product.rating))}</span>
            <span className="ratingValue">{product.rating.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// Product Carousel
function ProductCarousel({ images }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!images || images.length === 0) return null;

  const goPrev = () => {
    setCurrentIndex((prev) => (prev === 0 ? images.length - 1 : prev - 1));
  };

  const goNext = () => {
    setCurrentIndex((prev) => (prev === images.length - 1 ? 0 : prev + 1));
  };

  return (
    <div className="productCarousel">
      <div className="carouselHeader">
        <span className="carouselTitle">📦 Found products ({images.length})</span>
        <div className="carouselNav">
          <button onClick={goPrev} className="carouselBtn">‹</button>
          <span className="carouselCounter">{currentIndex + 1} / {images.length}</span>
          <button onClick={goNext} className="carouselBtn">›</button>
        </div>
      </div>
      <div className="carouselContent">
        <ProductCard product={images[currentIndex]} />
      </div>
      <div className="carouselDots">
        {images.map((_, idx) => (
          <button
            key={idx}
            className={`carouselDot ${idx === currentIndex ? 'active' : ''}`}
            onClick={() => setCurrentIndex(idx)}
          />
        ))}
      </div>
    </div>
  );
}

// Mini Chart
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
    <div className="miniChart">
      <div className="miniChartHeader">
        <span>📈 Demand Forecast</span>
        <span className={`trendBadge ${trendUp ? 'up' : 'down'}`}>
          {trendUp ? '↑' : '↓'} {Math.abs(trendPercent)}%
        </span>
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <LineChart data={combined} margin={{ top: 10, right: 10, bottom: 5, left: 5 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="name" tick={{ fontSize: 10 }} />
          <YAxis tick={{ fontSize: 10 }} width={35} />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8 }}
            formatter={(value, name) => [value?.toFixed(0), name === 'history' ? 'History' : 'Forecast']}
          />
          <Legend
            wrapperStyle={{ fontSize: 11 }}
            formatter={(value) => value === 'history' ? 'History' : 'Forecast'}
          />
          <Line
            type="monotone"
            dataKey="history"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="history"
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#8b5cf6"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3 }}
            name="forecast"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Product Comparison
function ProductComparison({ products }) {
  if (!products || products.length < 2) return null;

  const prices = products.map(p => p.price || 0).filter(p => p > 0);
  const ratings = products.map(p => p.rating || 0).filter(r => r > 0);
  const minPrice = Math.min(...prices);
  const maxRating = Math.max(...ratings);

  return (
    <div className="comparisonContainer">
      <div className="comparisonHeader">
        <span>⚖️ Product Comparison ({products.length})</span>
      </div>
      <div className="comparisonGrid">
        {products.slice(0, 4).map((product, idx) => (
          <div key={idx} className="comparisonCard">
            <div className="comparisonImage">
              {product.image_url ? (
                <img
                  src={product.image_url}
                  alt={product.name}
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              ) : (
                <span>📦</span>
              )}
            </div>
            <div className="comparisonName">{product.name}</div>
            <div className="comparisonStats">
              <div className={`comparisonPrice ${product.price === minPrice ? 'best' : ''}`}>
                ₹{(product.price || 0).toLocaleString()}
                {product.price === minPrice && <span className="bestBadge">Best Price</span>}
              </div>
              {product.rating > 0 && (
                <div className={`comparisonRating ${product.rating === maxRating ? 'best' : ''}`}>
                  ★ {product.rating.toFixed(1)}
                  {product.rating === maxRating && <span className="bestBadge">Top Rated</span>}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const { user, logout } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Voice recognition setup
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setVoiceSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setInputValue(transcript);
      };

      recognition.onend = () => setIsRecording(false);
      recognition.onerror = () => setIsRecording(false);

      recognitionRef.current = recognition;
    }
  }, []);

  const toggleVoiceRecording = () => {
    if (!recognitionRef.current) return;

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      setInputValue('');
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  // Export functions
  const exportToText = () => {
    const text = messages.map(msg => {
      const role = msg.role === 'user' ? 'You' : 'AI';
      const time = msg.timestamp ? new Date(msg.timestamp).toLocaleString() : '';
      return `[${time}] ${role}:\n${msg.content}\n`;
    }).join('\n---\n\n');

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportToCSV = () => {
    const headers = ['Time', 'Role', 'Message', 'Intent'];
    const rows = messages.map(msg => [
      msg.timestamp ? new Date(msg.timestamp).toLocaleString() : '',
      msg.role === 'user' ? 'User' : 'AI Assistant',
      `"${(msg.content || '').replace(/"/g, '""')}"`,
      msg.intent || ''
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const bom = '\uFEFF';
    const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadHistory = async () => {
    try {
      const history = await getChatHistory(20);
      if (history.length === 0) {
        setMessages([
          {
            role: "assistant",
            content:
              "Hello! I'm your AI assistant for demand forecasting. Ask me about products, trends, or forecasts.\n\n**Example queries:**\n- iPhone 14 Pro\n- Nike sneakers\n- Forecast for P0001\n- Top 5 products",
          },
        ]);
        setSuggestions([
          "iPhone 14 Pro",
          "Samsung Galaxy",
          "Nike sneakers",
          "Top 5 products",
        ]);
      } else {
        setMessages(history);
      }
    } catch (e) {
      console.error("Failed to load history:", e);
      setMessages([
        {
          role: "assistant",
          content: "Hello! I'm your AI assistant for demand forecasting.",
        },
      ]);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || loading) return;

    const userMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);
    setError("");

    try {
      const response = await sendChatMessage(text);

      const assistantMessage = {
        role: "assistant",
        content: response.reply,
        intent: response.intent,
        images: response.images,
        data: response.data,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      if (response.suggestions?.length > 0) {
        setSuggestions(response.suggestions);
      }
    } catch (e) {
      setError(e.message || "Failed to send message");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, an error occurred. Please try again.",
        },
      ]);
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

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    setTimeout(() => handleSend(), 50);
  };

  const handleClearHistory = async () => {
    try {
      await clearChatHistory();
      setMessages([
        {
          role: "assistant",
          content: "History cleared. How can I help?",
        },
      ]);
      setSuggestions([
        "iPhone 14 Pro",
        "Samsung Galaxy",
        "Nike sneakers",
        "Top 5 products",
      ]);
    } catch (e) {
      setError("Failed to clear history");
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "";
    try {
      return new Date(timestamp).toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  };

  return (
    <div className="chatApp">
      {/* Header */}
      <header className="chatHeader">
        <div className="headerLeft">
          <div className="logoIcon">AI</div>
          <h1 className="headerTitle">AI Chat</h1>
        </div>
        <div className="headerRight">
          <span className="userEmail">{user?.email}</span>

          {/* Export Dropdown */}
          <div className="exportDropdown">
            <button
              className="btnIcon"
              onClick={() => setShowExportMenu(!showExportMenu)}
              title="Export"
            >
              📥
            </button>
            {showExportMenu && (
              <div className="exportMenu">
                <button onClick={() => { exportToText(); setShowExportMenu(false); }}>
                  📄 Export TXT
                </button>
                <button onClick={() => { exportToCSV(); setShowExportMenu(false); }}>
                  📊 Export CSV
                </button>
              </div>
            )}
          </div>

          <button className="btnIcon" onClick={handleClearHistory} title="Clear history">
            🗑️
          </button>
          <button className="btnIcon" onClick={logout} title="Sign out">
            🚪
          </button>
        </div>
      </header>

      {error && <div className="errorBox">{error}</div>}

      {/* Chat Container */}
      <div className="chatContainer">
        {/* Messages */}
        <div className="chatMessages">
          {loadingHistory ? (
            <div className="chatLoading">
              <div className="loadingSpinner"></div>
              <span>Loading history...</span>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`chatMessage ${
                    msg.role === "user" ? "userMessage" : "assistantMessage"
                  }`}
                >
                  <div className="messageAvatar">
                    {msg.role === "user" ? "👤" : "🤖"}
                  </div>
                  <div className="messageContent">
                    <div className="messageText">
                      {renderMarkdown(msg.content)}
                    </div>

                    {/* Product Carousel */}
                    {msg.images && msg.images.length > 0 && msg.intent !== 'comparison' && (
                      <ProductCarousel images={msg.images} />
                    )}

                    {/* Product Comparison */}
                    {msg.images && msg.images.length >= 2 && msg.intent === 'comparison' && (
                      <ProductComparison products={msg.images} />
                    )}

                    {/* Chart */}
                    {msg.data && (
                      <MiniChart data={msg.data} />
                    )}

                    {/* Meta */}
                    <div className="messageMeta">
                      {msg.timestamp && (
                        <span className="messageTime">{formatTime(msg.timestamp)}</span>
                      )}
                      {msg.intent && (
                        <span className="messageIntent">{msg.intent}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {loading && (
                <div className="chatMessage assistantMessage">
                  <div className="messageAvatar">🤖</div>
                  <div className="messageContent">
                    <div className="typingIndicator">
                      <span>AI is thinking</span>
                      <div className="typingDots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && !loading && (
          <div className="chatSuggestions">
            {suggestions.map((s, idx) => (
              <button
                key={idx}
                className="suggestionChip"
                onClick={() => handleSuggestionClick(s)}
                disabled={loading}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="chatInputContainer">
          <input
            ref={inputRef}
            type="text"
            className="chatInput"
            placeholder={isRecording ? "🎤 Listening..." : "Ask about products, forecasts, trends..."}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading || isRecording}
          />
          {voiceSupported && (
            <button
              className={`voiceButton ${isRecording ? 'recording' : ''}`}
              onClick={toggleVoiceRecording}
              disabled={loading}
              title={isRecording ? "Stop recording" : "Voice input"}
            >
              {isRecording ? "⏹️" : "🎤"}
            </button>
          )}
          <button
            className="sendButton"
            onClick={handleSend}
            disabled={loading || !inputValue.trim()}
          >
            {loading ? <span className="sendSpinner"></span> : "➤"}
          </button>
        </div>
      </div>
    </div>
  );
}