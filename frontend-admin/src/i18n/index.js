/**
 * i18n Configuration
 * Supports Kazakh, Russian, and English languages
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import kk from './kk.json';
import ru from './ru.json';
import en from './en.json';

// Language resources
const resources = {
  kk: { translation: kk },
  ru: { translation: ru },
  en: { translation: en },
};

// Supported languages
export const languages = [
  { code: 'kk', name: 'Қазақша', flag: '🇰🇿' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'en', name: 'English', flag: '🇬🇧' },
];

// Initialize i18n
i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('i18nextLng') || 'kk', // Default to Kazakh, check localStorage first
    fallbackLng: 'kk', // Fallback to Kazakh
    supportedLngs: ['kk', 'ru', 'en'],

    interpolation: {
      escapeValue: false, // React already handles XSS
    },

    // Namespace
    defaultNS: 'translation',
    ns: ['translation'],

    // React options
    react: {
      useSuspense: true,
    },
  });

// Helper function to change language
export const changeLanguage = (langCode) => {
  i18n.changeLanguage(langCode);
  localStorage.setItem('i18nextLng', langCode);
  document.documentElement.lang = langCode;
};

// Get current language
export const getCurrentLanguage = () => {
  return i18n.language || 'kk';
};

// Get language by code
export const getLanguageByCode = (code) => {
  return languages.find(lang => lang.code === code);
};

export default i18n;