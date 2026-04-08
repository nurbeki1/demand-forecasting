/**
 * Settings Context - User Settings Management
 *
 * Manages all user preferences for:
 * - ML/Forecast display
 * - Chat Assistant behavior
 * - Trust indicators
 * - UI/UX preferences
 * - Notifications
 */

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { getSettings, updateSettings as apiUpdateSettings } from "../api/settingsApi";

const SettingsContext = createContext(null);

// Default settings structure
const DEFAULT_SETTINGS = {
  // Profile
  profile: {
    fullName: "",
    email: "",
    language: "kk", // kk, ru, en
  },

  // ML / Forecast Settings
  forecast: {
    defaultHorizon: 7, // 7, 14, 30 days
    showConfidence: true,
    showExplanation: true,
    dataFreshness: null, // Date string from backend
    modelType: "auto", // linear, randomforest, auto
  },

  // Chat Assistant Settings
  chat: {
    responseStyle: "analytical", // short, detailed, analytical
    showSuggestions: true,
    proactiveInsights: true,
  },

  // Trust Settings
  trust: {
    showConfidenceLevel: true,
    showExplanations: true,
    showDataSources: true,
  },

  // UI/UX Settings
  ui: {
    theme: "dark", // dark, light
    compactMode: false,
    animations: true,
  },

  // Notification Settings
  notifications: {
    demandIncrease: true,
    demandDecrease: true,
    forecastChange: true,
    emailNotifications: false,
  },
};

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getSettings();
      setSettings(prev => ({
        ...prev,
        ...data,
      }));
    } catch (err) {
      console.error("Failed to load settings:", err);
      // Use defaults on error
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = useCallback(async (section, key, value) => {
    // Optimistic update
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));

    // Persist to API
    try {
      setSaving(true);
      await apiUpdateSettings(section, key, value);
    } catch (err) {
      console.error("Failed to save setting:", err);
      setError("Failed to save setting");
      // Could revert here, but for UX we keep the optimistic update
    } finally {
      setSaving(false);
    }
  }, []);

  const updateSectionSettings = useCallback(async (section, values) => {
    // Optimistic update
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        ...values,
      },
    }));

    // Persist each value
    try {
      setSaving(true);
      for (const [key, value] of Object.entries(values)) {
        await apiUpdateSettings(section, key, value);
      }
    } catch (err) {
      console.error("Failed to save settings:", err);
      setError("Failed to save settings");
    } finally {
      setSaving(false);
    }
  }, []);

  const resetSettings = useCallback(async () => {
    setSettings(DEFAULT_SETTINGS);
    // Could call API to reset
  }, []);

  // Convenience getters for integrations
  const getForecastSettings = useCallback(() => settings.forecast, [settings.forecast]);
  const getChatSettings = useCallback(() => settings.chat, [settings.chat]);
  const getTrustSettings = useCallback(() => settings.trust, [settings.trust]);
  const getUISettings = useCallback(() => settings.ui, [settings.ui]);

  const value = {
    settings,
    loading,
    saving,
    error,
    updateSettings,
    updateSectionSettings,
    resetSettings,
    loadSettings,
    // Convenience getters
    getForecastSettings,
    getChatSettings,
    getTrustSettings,
    getUISettings,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return context;
}

// Hook for specific settings sections
export function useForecastSettings() {
  const { settings, updateSettings } = useSettings();
  return {
    ...settings.forecast,
    update: (key, value) => updateSettings("forecast", key, value),
  };
}

export function useChatSettings() {
  const { settings, updateSettings } = useSettings();
  return {
    ...settings.chat,
    update: (key, value) => updateSettings("chat", key, value),
  };
}

export function useTrustSettings() {
  const { settings, updateSettings } = useSettings();
  return {
    ...settings.trust,
    update: (key, value) => updateSettings("trust", key, value),
  };
}

export function useUISettings() {
  const { settings, updateSettings } = useSettings();
  return {
    ...settings.ui,
    update: (key, value) => updateSettings("ui", key, value),
  };
}
