import { useState, useRef, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { searchProducts } from "../../api/forecastApi";

const RECENT_KEY = "recent_searches";
const MAX_RECENT = 5;

function getRecentSearches() {
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY) || "[]");
  } catch {
    return [];
  }
}

function saveRecentSearch(query) {
  const recent = getRecentSearches().filter((q) => q !== query);
  recent.unshift(query);
  localStorage.setItem(RECENT_KEY, JSON.stringify(recent.slice(0, MAX_RECENT)));
}

export default function Topbar() {
  const { t } = useTranslation();
  const { user, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [searching, setSearching] = useState(false);

  const searchRef = useRef(null);
  const timerRef = useRef(null);

  const handleLogout = () => {
    navigate("/");
    setTimeout(() => logout(), 100);
  };

  // Debounced search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const data = await searchProducts(query.trim());
        setResults(data.results || []);
        setSelectedIndex(-1);
        setIsOpen(true);
      } catch {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [query]);

  // Click outside to close
  useEffect(() => {
    function handleClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = useCallback(
    (item) => {
      const productId = item.product_id;
      saveRecentSearch(productId);
      setQuery("");
      setIsOpen(false);
      setResults([]);
      navigate(`/admin/forecast?product=${productId}`);
    },
    [navigate]
  );

  function handleKeyDown(e) {
    if (!isOpen) return;

    const items = results.length > 0 ? results : [];
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((i) => Math.min(i + 1, items.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((i) => Math.max(i - 1, -1));
    } else if (e.key === "Enter" && selectedIndex >= 0 && items[selectedIndex]) {
      e.preventDefault();
      handleSelect(items[selectedIndex]);
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  }

  const recentSearches = getRecentSearches();
  const showRecent = isOpen && !query.trim() && recentSearches.length > 0;
  const showResults = isOpen && query.trim() && (results.length > 0 || searching);

  return (
    <div className="topbar">
      <div className="search search-wrap" ref={searchRef}>
        <span className="search-icon">🔍</span>
        <input
          placeholder={t('common.search')}
          aria-label={t('common.search')}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!isOpen) setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          disabled={!isAdmin}
        />

        {/* Search Dropdown */}
        {(showResults || showRecent) && (
          <div className="search-dropdown">
            {showRecent && (
              <>
                <div className="search-dropdown-label">{t('search.recent', 'Recent')}</div>
                {recentSearches.map((q) => (
                  <div
                    key={q}
                    className="search-result-item"
                    onClick={() => {
                      setQuery(q);
                      setIsOpen(true);
                    }}
                  >
                    <span className="search-result-icon">🕐</span>
                    <span>{q}</span>
                  </div>
                ))}
              </>
            )}

            {searching && (
              <div className="search-dropdown-label">{t('common.loading')}</div>
            )}

            {showResults && !searching && results.length === 0 && (
              <div className="search-dropdown-label">{t('search.noResults', 'No results found')}</div>
            )}

            {results.map((item, idx) => (
              <div
                key={item.product_id}
                className={`search-result-item ${idx === selectedIndex ? "selected" : ""}`}
                onClick={() => handleSelect(item)}
                onMouseEnter={() => setSelectedIndex(idx)}
              >
                <span className="search-result-icon">📦</span>
                <div className="search-result-info">
                  <div className="search-result-name">{item.product_id}</div>
                  {item.name && (
                    <div className="search-result-meta">{item.name}</div>
                  )}
                  {item.category && (
                    <div className="search-result-meta">{item.category}</div>
                  )}
                </div>
                {item.score != null && (
                  <span className="search-result-score">
                    {Math.round(item.score * 100)}%
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="topActions">
        {user && (
          <span className="userEmail">{user.email}</span>
        )}
        <button className="logoutBtn" onClick={handleLogout} aria-label={t('nav.logout')}>
          {t('nav.logout')}
        </button>
      </div>
    </div>
  );
}
