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

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import { useTheme } from "../context/ThemeContext";

import {
  sendChatMessage,
  getChatHistory,
  clearChatHistory,
} from "../api/chatApi";

import "../styles/dashboard.css";

// Simple Markdown-like renderer
function renderMarkdown(text) {
  if (!text) return null;

  // Split by lines and process
  const lines = text.split('\n');
  const elements = [];
  let inList = false;
  let listItems = [];

  lines.forEach((line, idx) => {
    // Headers
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
    // List items
    else if (line.match(/^[-*•]\s/)) {
      inList = true;
      listItems.push(<li key={idx}>{processInline(line.slice(2))}</li>);
    } else if (line.match(/^\d+\.\s/)) {
      inList = true;
      listItems.push(<li key={idx}>{processInline(line.replace(/^\d+\.\s/, ''))}</li>);
    }
    // Empty line
    else if (line.trim() === '') {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<br key={idx} />);
    }
    // Regular paragraph
    else {
      if (inList) {
        elements.push(<ul key={`list-${idx}`} className="mdList">{listItems}</ul>);
        listItems = [];
        inList = false;
      }
      elements.push(<p key={idx} className="mdP">{processInline(line)}</p>);
    }
  });

  // Flush remaining list
  if (inList && listItems.length > 0) {
    elements.push(<ul key="list-final" className="mdList">{listItems}</ul>);
  }

  return elements;
}

// Process inline markdown (bold, italic, code)
function processInline(text) {
  if (!text) return text;

  // Split by bold markers and process
  const parts = [];
  let remaining = text;
  let key = 0;

  // Process **bold**
  const boldRegex = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;
  let match;

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

// Trend Badge Component
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

// Product Card Component
function ProductCard({ product }) {
  return (
    <div className="productCard">
      {/* Trend Badge if available */}
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

// Product Carousel Component
function ProductCarousel({ images }) {
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!images || images.length === 0) return null;

  const goTo = (index) => {
    setCurrentIndex(index);
  };

  const goPrev = () => {
    setCurrentIndex((prev) => (prev === 0 ? images.length - 1 : prev - 1));
  };

  const goNext = () => {
    setCurrentIndex((prev) => (prev === images.length - 1 ? 0 : prev + 1));
  };

  return (
    <div className="productCarousel">
      <div className="carouselHeader">
        <span className="carouselTitle">📦 Найденные товары ({images.length})</span>
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
            onClick={() => goTo(idx)}
          />
        ))}
      </div>
    </div>
  );
}

// Mini Chart Component for inline display
function MiniChart({ data }) {
  if (!data?.history && !data?.forecast) return null;

  // Prepare data with separate columns for history and forecast
  const historyData = (data.history || []).slice(-7).map((h) => ({
    name: h.date?.split('-').slice(1).join('/') || '',
    history: h.demand,
  }));

  const forecastData = (data.forecast || []).slice(0, 7).map((f) => ({
    name: f.date?.split('-').slice(1).join('/') || '',
    forecast: f.predicted_demand,
  }));

  // Combine with last history point connecting to forecast
  const combined = [...historyData];
  if (historyData.length > 0 && forecastData.length > 0) {
    // Add forecast start point to last history entry
    combined[combined.length - 1].forecast = combined[combined.length - 1].history;
  }
  forecastData.forEach(f => combined.push(f));

  if (combined.length === 0) return null;

  // Calculate trend
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
        <span>📈 Прогноз спроса</span>
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
            formatter={(value, name) => [value?.toFixed(0), name === 'history' ? 'История' : 'Прогноз']}
          />
          <Legend
            wrapperStyle={{ fontSize: 11 }}
            formatter={(value) => value === 'history' ? 'История' : 'Прогноз'}
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

// Product Comparison Component (side-by-side)
function ProductComparison({ products }) {
  if (!products || products.length < 2) return null;

  // Find best values for highlighting
  const prices = products.map(p => p.price || 0).filter(p => p > 0);
  const ratings = products.map(p => p.rating || 0).filter(r => r > 0);
  const minPrice = Math.min(...prices);
  const maxRating = Math.max(...ratings);

  return (
    <div className="comparisonContainer">
      <div className="comparisonHeader">
        <span>⚖️ Сравнение товаров ({products.length})</span>
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
                {product.price === minPrice && <span className="bestBadge">Лучшая цена</span>}
              </div>
              {product.rating > 0 && (
                <div className={`comparisonRating ${product.rating === maxRating ? 'best' : ''}`}>
                  ★ {product.rating.toFixed(1)}
                  {product.rating === maxRating && <span className="bestBadge">Лучший рейтинг</span>}
                </div>
              )}
              {product.num_ratings > 0 && (
                <div className="comparisonReviews">
                  {product.num_ratings.toLocaleString()} отзывов
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
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [suggestions, setSuggestions] = useState([]);
  const [error, setError] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);

  // Use global theme context
  const { darkMode } = useTheme();

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Check if speech recognition is supported
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setVoiceSupported(true);
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'ru-RU'; // Russian, will also understand English

      recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');
        setInputValue(transcript);
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        if (event.error === 'not-allowed') {
          setError('Доступ к микрофону запрещён. Разрешите доступ в настройках браузера.');
        }
      };

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

  // Export chat to text file
  const exportToText = () => {
    const text = messages.map(msg => {
      const role = msg.role === 'user' ? 'Вы' : 'AI';
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

  // Export chat to CSV (Excel compatible)
  const exportToCSV = () => {
    const headers = ['Время', 'Роль', 'Сообщение', 'Intent'];
    const rows = messages.map(msg => [
      msg.timestamp ? new Date(msg.timestamp).toLocaleString() : '',
      msg.role === 'user' ? 'Пользователь' : 'AI Ассистент',
      `"${(msg.content || '').replace(/"/g, '""')}"`,
      msg.intent || ''
    ]);

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const bom = '\uFEFF'; // UTF-8 BOM for Excel
    const blob = new Blob([bom + csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${new Date().toISOString().slice(0,10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Export state for dropdown
  const [showExportMenu, setShowExportMenu] = useState(false);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Scroll to bottom when messages change
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
              "Привет! Я ваш AI-ассистент по прогнозированию спроса. Спрашивайте о товарах, трендах или прогнозах.\n\n**Примеры запросов:**\n- iPhone 14 Pro\n- Nike кроссовки\n- Прогноз для P0001\n- Топ-5 продуктов",
          },
        ]);
        setSuggestions([
          "iPhone 14 Pro",
          "Samsung Galaxy",
          "Nike кроссовки",
          "Топ-5 продуктов",
        ]);
      } else {
        setMessages(history);
      }
    } catch (e) {
      console.error("Failed to load history:", e);
      setMessages([
        {
          role: "assistant",
          content: "Привет! Я ваш AI-ассистент по прогнозированию спроса.",
        },
      ]);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSend = async () => {
    const text = inputValue.trim();
    if (!text || loading) return;

    // Add user message
    const userMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setLoading(true);
    setError("");

    try {
      const response = await sendChatMessage(text);

      // Add assistant message with images and data
      const assistantMessage = {
        role: "assistant",
        content: response.reply,
        intent: response.intent,
        images: response.images,
        data: response.data,
      };
      setMessages((prev) => [...prev, assistantMessage]);

      // Update suggestions
      if (response.suggestions?.length > 0) {
        setSuggestions(response.suggestions);
      }
    } catch (e) {
      setError(e.message || "Failed to send message");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Извините, произошла ошибка. Попробуйте ещё раз.",
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
    setTimeout(() => {
      handleSend();
    }, 50);
  };

  const handleClearHistory = async () => {
    try {
      await clearChatHistory();
      setMessages([
        {
          role: "assistant",
          content: "История очищена. Чем могу помочь?",
        },
      ]);
      setSuggestions([
        "iPhone 14 Pro",
        "Samsung Galaxy",
        "Nike кроссовки",
        "Топ-5 продуктов",
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
    <div className="appShell">
      <Sidebar />

      <div className="main">
        <Topbar />

        <div className="content">
          {/* Header */}
          <div className="headerRow">
            <div>
              <div className="title">🤖 AI Chat</div>
              <div className="subtitle">Demand Forecasting Assistant • 551K товаров</div>
            </div>

            <div className="headerActions">
              {/* Export Dropdown */}
              <div className="exportDropdown">
                <button
                  className="btnIcon"
                  type="button"
                  onClick={() => setShowExportMenu(!showExportMenu)}
                  title="Экспорт"
                >
                  📥
                </button>
                {showExportMenu && (
                  <div className="exportMenu">
                    <button onClick={() => { exportToText(); setShowExportMenu(false); }}>
                      📄 Экспорт TXT
                    </button>
                    <button onClick={() => { exportToCSV(); setShowExportMenu(false); }}>
                      📊 Экспорт CSV (Excel)
                    </button>
                  </div>
                )}
              </div>

              <button
                className="btnSecondary"
                type="button"
                onClick={handleClearHistory}
              >
                🗑️ Очистить
              </button>
            </div>
          </div>

          {error && <div className="errorBox">{error}</div>}

          {/* Chat Container */}
          <div className="chatContainerNew">
            {/* Messages */}
            <div className="chatMessagesNew">
              {loadingHistory ? (
                <div className="chatLoading">
                  <div className="loadingSpinner"></div>
                  <span>Загрузка истории...</span>
                </div>
              ) : (
                <>
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`chatMessageNew ${
                        msg.role === "user" ? "userMessageNew" : "assistantMessageNew"
                      }`}
                    >
                      <div className="messageAvatarNew">
                        {msg.role === "user" ? "👤" : "🤖"}
                      </div>
                      <div className="messageContentNew">
                        {/* Markdown rendered text */}
                        <div className="messageTextNew">
                          {renderMarkdown(msg.content)}
                        </div>

                        {/* Product Images Carousel */}
                        {msg.images && msg.images.length > 0 && msg.intent !== 'comparison' && (
                          <ProductCarousel images={msg.images} />
                        )}

                        {/* Product Comparison (side-by-side) */}
                        {msg.images && msg.images.length >= 2 && msg.intent === 'comparison' && (
                          <ProductComparison products={msg.images} />
                        )}

                        {/* Inline Chart */}
                        {msg.data && (
                          <MiniChart data={msg.data} />
                        )}

                        {/* Meta info */}
                        <div className="messageMeta">
                          {msg.timestamp && (
                            <span className="messageTime">
                              {formatTime(msg.timestamp)}
                            </span>
                          )}
                          {msg.intent && (
                            <span className="messageIntent">
                              {msg.intent}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Typing Indicator */}
                  {loading && (
                    <div className="chatMessageNew assistantMessageNew">
                      <div className="messageAvatarNew">🤖</div>
                      <div className="messageContentNew">
                        <div className="typingIndicatorNew">
                          <span>AI думает</span>
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
              <div className="chatSuggestionsNew">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    className="suggestionChipNew"
                    onClick={() => handleSuggestionClick(s)}
                    disabled={loading}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="chatInputContainerNew">
              <input
                ref={inputRef}
                type="text"
                className="chatInputNew"
                placeholder={isRecording ? "🎤 Говорите..." : "Спросите о товарах, прогнозах, трендах..."}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={loading || isRecording}
              />
              {/* Voice Button */}
              {voiceSupported && (
                <button
                  className={`voiceButtonNew ${isRecording ? 'recording' : ''}`}
                  onClick={toggleVoiceRecording}
                  disabled={loading}
                  title={isRecording ? "Остановить запись" : "Голосовой ввод"}
                >
                  {isRecording ? "⏹️" : "🎤"}
                </button>
              )}
              <button
                className="sendButtonNew"
                onClick={handleSend}
                disabled={loading || !inputValue.trim()}
              >
                {loading ? (
                  <span className="sendSpinner"></span>
                ) : (
                  "➤"
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        /* New Chat Styles */
        .chatContainerNew {
          display: flex;
          flex-direction: column;
          height: calc(100vh - 180px);
          min-height: 500px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        }

        .chatMessagesNew {
          flex: 1;
          overflow-y: auto;
          padding: 24px;
          display: flex;
          flex-direction: column;
          gap: 16px;
          background: linear-gradient(to bottom, rgba(255,255,255,0.95), rgba(255,255,255,0.98));
        }

        .chatLoading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          gap: 12px;
          color: #6b7280;
        }

        .loadingSpinner {
          width: 32px;
          height: 32px;
          border: 3px solid #e5e7eb;
          border-top-color: #6366f1;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .chatMessageNew {
          display: flex;
          gap: 12px;
          max-width: 85%;
          animation: messageIn 0.3s ease-out;
        }

        @keyframes messageIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .userMessageNew {
          align-self: flex-end;
          flex-direction: row-reverse;
        }

        .assistantMessageNew {
          align-self: flex-start;
        }

        .messageAvatarNew {
          width: 40px;
          height: 40px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 20px;
          flex-shrink: 0;
          background: white;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }

        .userMessageNew .messageAvatarNew {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .messageContentNew {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .messageTextNew {
          padding: 16px 20px;
          border-radius: 16px;
          line-height: 1.6;
          font-size: 14px;
        }

        .userMessageNew .messageTextNew {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-bottom-right-radius: 4px;
        }

        .assistantMessageNew .messageTextNew {
          background: white;
          color: #374151;
          border-bottom-left-radius: 4px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        /* Markdown Styles */
        .mdH1, .mdH2, .mdH3 {
          margin: 8px 0;
          color: #1f2937;
        }
        .mdH1 { font-size: 18px; }
        .mdH2 { font-size: 16px; }
        .mdH3 { font-size: 14px; font-weight: 600; color: #6366f1; }

        .mdP {
          margin: 4px 0;
        }

        .mdList {
          margin: 8px 0;
          padding-left: 20px;
        }

        .mdList li {
          margin: 4px 0;
        }

        /* Product Card */
        .productCarousel {
          background: white;
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        .carouselHeader {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          padding-bottom: 8px;
          border-bottom: 1px solid #f3f4f6;
        }

        .carouselTitle {
          font-weight: 600;
          font-size: 13px;
          color: #374151;
        }

        .carouselNav {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .carouselBtn {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          border: 1px solid #e5e7eb;
          background: white;
          cursor: pointer;
          font-size: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .carouselBtn:hover {
          background: #6366f1;
          color: white;
          border-color: #6366f1;
        }

        .carouselCounter {
          font-size: 12px;
          color: #6b7280;
        }

        .productCard {
          display: flex;
          gap: 16px;
          padding: 12px;
          background: #fafafa;
          border-radius: 8px;
        }

        .productImageContainer {
          width: 100px;
          height: 100px;
          border-radius: 8px;
          overflow: hidden;
          flex-shrink: 0;
          background: white;
        }

        .productImage {
          width: 100%;
          height: 100%;
          object-fit: contain;
        }

        .productImagePlaceholder {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
          background: #f3f4f6;
        }

        .productInfo {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .productName {
          font-size: 14px;
          font-weight: 500;
          color: #1f2937;
          line-height: 1.3;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }

        .productPrice {
          font-size: 18px;
          font-weight: 700;
          color: #059669;
        }

        .productRating {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 13px;
        }

        .stars {
          color: #f59e0b;
        }

        .ratingValue {
          color: #6b7280;
        }

        .carouselDots {
          display: flex;
          justify-content: center;
          gap: 6px;
          margin-top: 12px;
        }

        .carouselDot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          border: none;
          background: #e5e7eb;
          cursor: pointer;
          transition: all 0.2s;
        }

        .carouselDot.active {
          background: #6366f1;
          transform: scale(1.2);
        }

        /* Mini Chart */
        .miniChart {
          background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
          border-radius: 12px;
          padding: 16px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
          border: 1px solid #e2e8f0;
          margin-top: 12px;
        }

        .miniChartHeader {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 13px;
          font-weight: 600;
          color: #374151;
          margin-bottom: 12px;
        }

        .trendBadge {
          font-size: 12px;
          padding: 4px 10px;
          border-radius: 20px;
          font-weight: 600;
        }

        .trendBadge.up {
          background: #dcfce7;
          color: #16a34a;
        }

        .trendBadge.down {
          background: #fee2e2;
          color: #dc2626;
        }

        /* Message Meta */
        .messageMeta {
          display: flex;
          gap: 8px;
          padding-top: 4px;
        }

        .messageTime {
          font-size: 11px;
          color: #9ca3af;
        }

        .messageIntent {
          font-size: 10px;
          padding: 2px 8px;
          background: #f3f4f6;
          border-radius: 10px;
          color: #6b7280;
        }

        /* Typing Indicator */
        .typingIndicatorNew {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 0;
          color: #6b7280;
          font-size: 13px;
        }

        .typingDots {
          display: flex;
          gap: 4px;
        }

        .typingDots span {
          width: 6px;
          height: 6px;
          background: #6366f1;
          border-radius: 50%;
          animation: bounce 1.4s infinite ease-in-out both;
        }

        .typingDots span:nth-child(1) { animation-delay: -0.32s; }
        .typingDots span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); }
          40% { transform: scale(1); }
        }

        /* Suggestions */
        .chatSuggestionsNew {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          padding: 12px 24px;
          background: rgba(255, 255, 255, 0.9);
          border-top: 1px solid rgba(0, 0, 0, 0.05);
        }

        .suggestionChipNew {
          padding: 8px 16px;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 20px;
          font-size: 13px;
          color: #374151;
          cursor: pointer;
          transition: all 0.2s;
        }

        .suggestionChipNew:hover:not(:disabled) {
          background: #6366f1;
          border-color: #6366f1;
          color: white;
          transform: translateY(-1px);
        }

        .suggestionChipNew:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        /* Input */
        .chatInputContainerNew {
          display: flex;
          gap: 12px;
          padding: 16px 24px;
          background: white;
          border-top: 1px solid #e5e7eb;
        }

        .chatInputNew {
          flex: 1;
          padding: 14px 20px;
          border: 2px solid #e5e7eb;
          border-radius: 25px;
          font-size: 14px;
          outline: none;
          transition: all 0.2s;
        }

        .chatInputNew:focus {
          border-color: #6366f1;
          box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .chatInputNew:disabled {
          background: #f9fafb;
        }

        .sendButtonNew {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          border: none;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          font-size: 20px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .sendButtonNew:hover:not(:disabled) {
          transform: scale(1.05);
          box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .sendButtonNew:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .voiceButtonNew {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          border: 2px solid #e5e7eb;
          background: white;
          font-size: 20px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .voiceButtonNew:hover:not(:disabled) {
          border-color: #667eea;
          background: #f0f1ff;
        }

        .voiceButtonNew.recording {
          border-color: #ef4444;
          background: #fef2f2;
          animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
          50% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        }

        .voiceButtonNew:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .sendSpinner {
          width: 20px;
          height: 20px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .chatContainerNew {
            height: calc(100vh - 150px);
            border-radius: 0;
          }

          .chatMessageNew {
            max-width: 95%;
          }

          .productCard {
            flex-direction: column;
          }

          .productImageContainer {
            width: 100%;
            height: 150px;
          }
        }

        /* Header Actions */
        .headerActions {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .btnIcon {
          width: 40px;
          height: 40px;
          border-radius: 10px;
          border: 1px solid #e5e7eb;
          background: white;
          font-size: 18px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .btnIcon:hover {
          background: #f3f4f6;
          border-color: #d1d5db;
        }

        /* Export Dropdown */
        .exportDropdown {
          position: relative;
        }

        .exportMenu {
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 8px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
          border: 1px solid #e5e7eb;
          overflow: hidden;
          z-index: 100;
          min-width: 180px;
        }

        .exportMenu button {
          display: block;
          width: 100%;
          padding: 12px 16px;
          text-align: left;
          border: none;
          background: white;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.2s;
        }

        .exportMenu button:hover {
          background: #f3f4f6;
        }

        .exportMenu button:not(:last-child) {
          border-bottom: 1px solid #e5e7eb;
        }

        /* Product Comparison */
        .comparisonContainer {
          background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
          border-radius: 16px;
          padding: 16px;
          margin-top: 12px;
          border: 1px solid #fbbf24;
        }

        .comparisonHeader {
          font-size: 14px;
          font-weight: 600;
          color: #92400e;
          margin-bottom: 12px;
        }

        .comparisonGrid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
          gap: 12px;
        }

        .comparisonCard {
          background: white;
          border-radius: 12px;
          padding: 12px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
          text-align: center;
        }

        .comparisonImage {
          width: 80px;
          height: 80px;
          margin: 0 auto 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #f9fafb;
          border-radius: 8px;
          overflow: hidden;
        }

        .comparisonImage img {
          max-width: 100%;
          max-height: 100%;
          object-fit: contain;
        }

        .comparisonImage span {
          font-size: 32px;
        }

        .comparisonName {
          font-size: 12px;
          font-weight: 500;
          color: #374151;
          margin-bottom: 8px;
          height: 32px;
          overflow: hidden;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }

        .comparisonStats {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .comparisonPrice {
          font-size: 14px;
          font-weight: 700;
          color: #059669;
        }

        .comparisonPrice.best {
          color: #16a34a;
          background: #dcfce7;
          padding: 4px 8px;
          border-radius: 6px;
        }

        .comparisonRating {
          font-size: 13px;
          color: #f59e0b;
        }

        .comparisonRating.best {
          color: #d97706;
          background: #fef3c7;
          padding: 4px 8px;
          border-radius: 6px;
        }

        .comparisonReviews {
          font-size: 11px;
          color: #6b7280;
        }

        .bestBadge {
          display: block;
          font-size: 9px;
          margin-top: 2px;
          font-weight: 600;
        }

        /* Dark Mode Styles */
        body.dark-mode .chatContainerNew {
          background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        }

        body.dark-mode .chatMessagesNew {
          background: linear-gradient(to bottom, #1f2937, #111827);
        }

        body.dark-mode .chatLoading {
          color: #9ca3af;
        }

        body.dark-mode .messageContentNew {
          background: #374151;
          color: #f3f4f6;
        }

        body.dark-mode .userMessageNew .messageContentNew {
          background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
          color: white;
        }

        body.dark-mode .messageTextNew,
        body.dark-mode .mdP,
        body.dark-mode .mdList {
          color: #e5e7eb;
        }

        body.dark-mode .mdH1,
        body.dark-mode .mdH2,
        body.dark-mode .mdH3 {
          color: #f9fafb;
        }

        body.dark-mode .chatSuggestionsNew {
          background: #1f2937;
          border-top-color: #374151;
        }

        body.dark-mode .suggestionChipNew {
          background: #374151;
          color: #e5e7eb;
          border-color: #4b5563;
        }

        body.dark-mode .suggestionChipNew:hover {
          background: #4b5563;
          border-color: #6366f1;
        }

        body.dark-mode .chatInputContainerNew {
          background: #1f2937;
          border-top-color: #374151;
        }

        body.dark-mode .chatInputNew {
          background: #374151;
          border-color: #4b5563;
          color: #f3f4f6;
        }

        body.dark-mode .chatInputNew::placeholder {
          color: #9ca3af;
        }

        body.dark-mode .voiceButtonNew {
          background: #374151;
          border-color: #4b5563;
        }

        body.dark-mode .miniChart {
          background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
          border-color: #4b5563;
        }

        body.dark-mode .miniChartHeader {
          color: #e5e7eb;
        }

        body.dark-mode .productCard {
          background: #374151;
          border-color: #4b5563;
        }

        body.dark-mode .productName {
          color: #f3f4f6;
        }

        body.dark-mode .carouselHeader {
          color: #e5e7eb;
        }
      `}</style>
    </div>
  );
}
