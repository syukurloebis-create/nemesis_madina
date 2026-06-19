import React, { useState, useEffect, useCallback } from 'react';
import { Search, X, FileText, Building, AlertTriangle } from 'lucide-react';
import { api } from '../../services/api';
import { useAuthStore } from '../../stores/authStore';

export const SearchBar: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const { token } = useAuthStore();

  const performSearch = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setResults([]);
      return;
    }

    setLoading(true);
    try {
      const cases = await api.getCases();
      const casesData = cases.data || cases || [];
      const filtered = casesData.filter((c: any) => 
        c.title?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setResults(filtered.slice(0, 10));
      setIsOpen(true);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => performSearch(query), 300);
    return () => clearTimeout(timer);
  }, [query, performSearch]);

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder="Cari kasus, entitas, atau vendor..."
          className="w-80 bg-gray-800 border border-gray-700 rounded-lg py-2 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
        />
        {query && (
          <button onClick={() => setQuery('')} className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <X className="w-4 h-4 text-gray-500 hover:text-gray-300" />
          </button>
        )}
      </div>

      {isOpen && query.length >= 2 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-400">Mencari...</div>
          ) : results.length === 0 ? (
            <div className="p-4 text-center text-gray-500">Tidak ditemukan hasil untuk "{query}"</div>
          ) : (
            <div className="py-2">
              {results.map((result) => (
                <a
                  key={result.id}
                  href={`/investigation?id=${result.id}`}
                  className="flex items-center px-4 py-2 hover:bg-gray-700 transition"
                  onClick={() => setIsOpen(false)}
                >
                  <FileText className="w-4 h-4 text-cyan-400 mr-3" />
                  <div>
                    <div className="text-sm text-white">{result.title}</div>
                    <div className="text-xs text-gray-500">{result.status} • {result.priority}</div>
                  </div>
                </a>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
