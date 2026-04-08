/**
 * Language Switcher Component
 * Allows users to switch between Kazakh, Russian, and English
 */

import { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { languages, changeLanguage, getCurrentLanguage } from '../i18n';

export default function LanguageSwitcher({ variant = 'dropdown' }) {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [currentLang, setCurrentLang] = useState(getCurrentLanguage());
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLanguageChange = (langCode) => {
    changeLanguage(langCode);
    setCurrentLang(langCode);
    setIsOpen(false);
  };

  const currentLanguage = languages.find(l => l.code === currentLang) || languages[1];

  // Inline styles (can be moved to CSS)
  const styles = {
    container: {
      position: 'relative',
      display: 'inline-block',
    },
    button: {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 12px',
      background: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '8px',
      color: 'inherit',
      cursor: 'pointer',
      fontSize: '14px',
      transition: 'all 0.2s ease',
    },
    buttonHover: {
      background: 'rgba(255, 255, 255, 0.15)',
    },
    dropdown: {
      position: 'absolute',
      top: '100%',
      right: 0,
      marginTop: '4px',
      background: '#1a1a2e',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '8px',
      boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
      overflow: 'hidden',
      zIndex: 1000,
      minWidth: '150px',
    },
    option: {
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      padding: '10px 16px',
      cursor: 'pointer',
      transition: 'background 0.2s ease',
      color: '#fff',
      fontSize: '14px',
    },
    optionActive: {
      background: 'rgba(99, 102, 241, 0.2)',
    },
    optionHover: {
      background: 'rgba(255, 255, 255, 0.1)',
    },
    flag: {
      fontSize: '18px',
    },
    arrow: {
      marginLeft: '4px',
      transition: 'transform 0.2s ease',
      transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
    },
    // Buttons variant
    buttonsContainer: {
      display: 'flex',
      gap: '4px',
      background: 'rgba(255, 255, 255, 0.1)',
      padding: '4px',
      borderRadius: '8px',
    },
    langButton: {
      padding: '6px 12px',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '12px',
      fontWeight: '500',
      transition: 'all 0.2s ease',
    },
    langButtonActive: {
      background: '#6366f1',
      color: '#fff',
    },
    langButtonInactive: {
      background: 'transparent',
      color: 'rgba(255, 255, 255, 0.7)',
    },
  };

  // Buttons variant - compact language buttons
  if (variant === 'buttons') {
    return (
      <div style={styles.buttonsContainer}>
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            style={{
              ...styles.langButton,
              ...(currentLang === lang.code ? styles.langButtonActive : styles.langButtonInactive),
            }}
            title={lang.name}
          >
            {lang.code.toUpperCase()}
          </button>
        ))}
      </div>
    );
  }

  // Flags variant - just flags
  if (variant === 'flags') {
    return (
      <div style={{ display: 'flex', gap: '8px' }}>
        {languages.map((lang) => (
          <button
            key={lang.code}
            onClick={() => handleLanguageChange(lang.code)}
            style={{
              ...styles.langButton,
              padding: '4px 8px',
              fontSize: '20px',
              opacity: currentLang === lang.code ? 1 : 0.5,
              background: currentLang === lang.code ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
            }}
            title={lang.name}
          >
            {lang.flag}
          </button>
        ))}
      </div>
    );
  }

  // Default dropdown variant
  return (
    <div style={styles.container} ref={dropdownRef}>
      <button
        style={styles.button}
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={(e) => Object.assign(e.target.style, styles.buttonHover)}
        onMouseLeave={(e) => Object.assign(e.target.style, styles.button)}
      >
        <span style={styles.flag}>{currentLanguage.flag}</span>
        <span>{currentLanguage.name}</span>
        <span style={styles.arrow}>▼</span>
      </button>

      {isOpen && (
        <div style={styles.dropdown}>
          {languages.map((lang) => (
            <div
              key={lang.code}
              style={{
                ...styles.option,
                ...(currentLang === lang.code ? styles.optionActive : {}),
              }}
              onClick={() => handleLanguageChange(lang.code)}
              onMouseEnter={(e) => {
                if (currentLang !== lang.code) {
                  e.target.style.background = 'rgba(255, 255, 255, 0.1)';
                }
              }}
              onMouseLeave={(e) => {
                if (currentLang !== lang.code) {
                  e.target.style.background = 'transparent';
                }
              }}
            >
              <span style={styles.flag}>{lang.flag}</span>
              <span>{lang.name}</span>
              {currentLang === lang.code && <span style={{ marginLeft: 'auto' }}>✓</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}