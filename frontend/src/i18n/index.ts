import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Resources
const resources = {
  en: {
    translation: {
      welcome: "Welcome to NEMESIS V8+",
      dashboard: "Dashboard",
      cases: "Cases",
      admin: "Admin",
      login: "Login",
      logout: "Logout"
    }
  },
  id: {
    translation: {
      welcome: "Selamat Datang di NEMESIS V8+",
      dashboard: "Dasbor",
      cases: "Kasus",
      admin: "Admin",
      login: "Masuk",
      logout: "Keluar"
    }
  }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
