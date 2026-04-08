/**
 * Settings Panel - Claude-style settings layout
 * All sections visible on one scrollable page
 */

import { useState, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { SettingsProvider, useSettings } from "../../context/SettingsContext";

import "../../styles/settings.css";

// Navigation items
const NAV_ITEMS = [
  { id: "general", label: "General" },
  { id: "notifications", label: "Notifications" },
  { id: "appearance", label: "Appearance" },
];

function SettingsPanelContent({ onClose }) {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const { settings, updateSettings } = useSettings();
  const [activeNav, setActiveNav] = useState("general");
  const contentRef = useRef(null);

  const handleLanguageChange = (e) => {
    const newLang = e.target.value;
    updateSettings("profile", "language", newLang);
    i18n.changeLanguage(newLang);
  };

  // Scroll spy - auto-select nav item based on scroll position
  useEffect(() => {
    const container = contentRef.current;
    if (!container) return;

    const handleScroll = () => {
      const sections = NAV_ITEMS.map(item => ({
        id: item.id,
        element: document.getElementById(`settings-${item.id}`)
      })).filter(s => s.element);

      const containerTop = container.scrollTop;
      const containerHeight = container.clientHeight;

      for (let i = sections.length - 1; i >= 0; i--) {
        const section = sections[i];
        const sectionTop = section.element.offsetTop - container.offsetTop;

        if (containerTop >= sectionTop - containerHeight / 3) {
          setActiveNav(section.id);
          break;
        }
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToSection = (sectionId) => {
    setActiveNav(sectionId);
    const element = document.getElementById(`settings-${sectionId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <div className="settings-panel-wrapper" onClick={(e) => e.target === e.currentTarget && onClose()}>
    <div className="settings-panel-claude">
      {/* Left Navigation */}
      <div className="settings-nav-claude">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`settings-nav-item-claude ${activeNav === item.id ? 'active' : ''}`}
            onClick={() => scrollToSection(item.id)}
          >
            {t(`settings.nav.${item.id}`)}
          </button>
        ))}
      </div>

      {/* Right Content */}
      <div className="settings-content-claude" ref={contentRef}>
        <div className="settings-content-header">
          <h1>{t('settings.title')}</h1>
          <button className="settings-close-btn" onClick={onClose}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <div className="settings-sections">
          {/* ============================================
              GENERAL SECTION
              ============================================ */}
          <section id="settings-general" className="settings-section">
            {/* Profile */}
            <div className="settings-group">
              <h3 className="settings-group-title">{t('settings.sections.profile.title')}</h3>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.profile.fullName')}</span>
                </div>
                <input
                  type="text"
                  className="settings-input-claude"
                  value={settings.profile.fullName}
                  onChange={(e) => updateSettings("profile", "fullName", e.target.value)}
                  placeholder={t('settings.sections.profile.enterName')}
                />
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.profile.email')}</span>
                </div>
                <input
                  type="email"
                  className="settings-input-claude"
                  value={user?.email || ''}
                  disabled
                />
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.profile.language')}</span>
                </div>
                <select
                  className="settings-select-claude"
                  value={settings.profile.language}
                  onChange={handleLanguageChange}
                >
                  <option value="kk">{t('languages.kk')}</option>
                  <option value="ru">{t('languages.ru')}</option>
                  <option value="en">{t('languages.en')}</option>
                </select>
              </div>
            </div>

            {/* Forecast Settings */}
            <div className="settings-group">
              <h3 className="settings-group-title">{t('settings.sections.forecast.title')}</h3>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.forecast.defaultHorizon')}</span>
                  <span className="settings-row-desc">{t('settings.sections.forecast.defaultHorizonDesc')}</span>
                </div>
                <select
                  className="settings-select-claude"
                  value={settings.forecast.defaultHorizon}
                  onChange={(e) => updateSettings("forecast", "defaultHorizon", Number(e.target.value))}
                >
                  <option value={7}>7 {t('forecast.days')}</option>
                  <option value={14}>14 {t('forecast.days')}</option>
                  <option value={30}>30 {t('forecast.days')}</option>
                </select>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.forecast.showConfidence')}</span>
                  <span className="settings-row-desc">{t('settings.sections.forecast.showConfidenceDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.forecast.showConfidence}
                    onChange={(e) => updateSettings("forecast", "showConfidence", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.forecast.showExplanation')}</span>
                  <span className="settings-row-desc">{t('settings.sections.forecast.showExplanationDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.forecast.showExplanation}
                    onChange={(e) => updateSettings("forecast", "showExplanation", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>
            </div>

            {/* Chat Settings */}
            <div className="settings-group">
              <h3 className="settings-group-title">{t('settings.sections.chat.title')}</h3>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.chat.responseStyle')}</span>
                  <span className="settings-row-desc">{t('settings.sections.chat.responseStyleDesc')}</span>
                </div>
                <select
                  className="settings-select-claude"
                  value={settings.chat.responseStyle}
                  onChange={(e) => updateSettings("chat", "responseStyle", e.target.value)}
                >
                  <option value="short">{t('settings.sections.chat.styleShort')}</option>
                  <option value="detailed">{t('settings.sections.chat.styleDetailed')}</option>
                  <option value="analytical">{t('settings.sections.chat.styleAnalytical')}</option>
                </select>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.chat.showSuggestions')}</span>
                  <span className="settings-row-desc">{t('settings.sections.chat.showSuggestionsDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.chat.showSuggestions}
                    onChange={(e) => updateSettings("chat", "showSuggestions", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>
            </div>
          </section>

          {/* ============================================
              NOTIFICATIONS SECTION
              ============================================ */}
          <section id="settings-notifications" className="settings-section">
            <div className="settings-group">
              <h3 className="settings-group-title">{t('settings.sections.notifications.title')}</h3>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.notifications.demandIncrease')}</span>
                  <span className="settings-row-desc">{t('settings.sections.notifications.demandIncreaseDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.notifications.demandIncrease}
                    onChange={(e) => updateSettings("notifications", "demandIncrease", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.notifications.demandDecrease')}</span>
                  <span className="settings-row-desc">{t('settings.sections.notifications.demandDecreaseDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.notifications.demandDecrease}
                    onChange={(e) => updateSettings("notifications", "demandDecrease", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.notifications.forecastChange')}</span>
                  <span className="settings-row-desc">{t('settings.sections.notifications.forecastChangeDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.notifications.forecastChange}
                    onChange={(e) => updateSettings("notifications", "forecastChange", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.notifications.emailNotifications')}</span>
                  <span className="settings-row-desc">{t('settings.sections.notifications.emailNotificationsDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.notifications.emailNotifications}
                    onChange={(e) => updateSettings("notifications", "emailNotifications", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>
            </div>
          </section>

          {/* ============================================
              APPEARANCE SECTION
              ============================================ */}
          <section id="settings-appearance" className="settings-section">
            <div className="settings-group">
              <h3 className="settings-group-title">{t('settings.sections.ui.title')}</h3>

              {/* Color Mode Cards */}
              <div className="settings-row-full">
                <span className="settings-row-title">{t('settings.sections.ui.theme')}</span>
                <div className="color-mode-cards">
                  <button
                    className={`color-mode-card ${settings.ui.theme === 'light' ? 'active' : ''}`}
                    onClick={() => updateSettings("ui", "theme", "light")}
                  >
                    <div className="color-mode-preview light">
                      <div className="preview-sidebar"></div>
                      <div className="preview-content">
                        <div className="preview-line"></div>
                        <div className="preview-line short"></div>
                      </div>
                    </div>
                    <span>{t('settings.sections.ui.themeLight')}</span>
                  </button>

                  <button
                    className={`color-mode-card ${settings.ui.theme === 'auto' ? 'active' : ''}`}
                    onClick={() => updateSettings("ui", "theme", "auto")}
                  >
                    <div className="color-mode-preview auto">
                      <div className="preview-sidebar"></div>
                      <div className="preview-content">
                        <div className="preview-line"></div>
                        <div className="preview-line short"></div>
                      </div>
                    </div>
                    <span>Auto</span>
                  </button>

                  <button
                    className={`color-mode-card ${settings.ui.theme === 'dark' ? 'active' : ''}`}
                    onClick={() => updateSettings("ui", "theme", "dark")}
                  >
                    <div className="color-mode-preview dark">
                      <div className="preview-sidebar"></div>
                      <div className="preview-content">
                        <div className="preview-line"></div>
                        <div className="preview-line short"></div>
                      </div>
                    </div>
                    <span>{t('settings.sections.ui.themeDark')}</span>
                  </button>
                </div>
              </div>

              <div className="settings-row">
                <div className="settings-row-label">
                  <span className="settings-row-title">{t('settings.sections.ui.animations')}</span>
                  <span className="settings-row-desc">{t('settings.sections.ui.animationsDesc')}</span>
                </div>
                <label className="toggle-claude">
                  <input
                    type="checkbox"
                    checked={settings.ui.animations}
                    onChange={(e) => updateSettings("ui", "animations", e.target.checked)}
                  />
                  <span className="toggle-slider-claude"></span>
                </label>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
    </div>
  );
}

export default function SettingsPanel({ onClose }) {
  return (
    <SettingsProvider>
      <SettingsPanelContent onClose={onClose} />
    </SettingsProvider>
  );
}
