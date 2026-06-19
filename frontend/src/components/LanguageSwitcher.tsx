import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher: React.FC = () => {
  const { i18n, t } = useTranslation();
  const currentLanguage = i18n.language;

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="text-xs text-gray-500">🌐</span>
      <button
        onClick={() => changeLanguage('id')}
        className={`px-2 py-1 text-xs rounded transition-colors ${
          currentLanguage === 'id' 
            ? 'bg-green-500/20 text-green-400' 
            : 'text-gray-400 hover:text-white'
        }`}
      >
        🇮🇩 ID
      </button>
      <button
        onClick={() => changeLanguage('en')}
        className={`px-2 py-1 text-xs rounded transition-colors ${
          currentLanguage === 'en' 
            ? 'bg-green-500/20 text-green-400' 
            : 'text-gray-400 hover:text-white'
        }`}
      >
        🇬🇧 EN
      </button>
    </div>
  );
};

export default LanguageSwitcher;
