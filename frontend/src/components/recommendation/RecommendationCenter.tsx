// RecommendationCenter.tsx
import React, { useEffect, useState } from 'react';
import api from '../../services/api';
import { RecommendationCard } from './RecommendationCard';

export const RecommendationCenter: React.FC = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/api/v1/recommendations/');
        setRecommendations(response.data);
        setError(null);
      } catch (err) {
        setError('Gagal memuat rekomendasi');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="bg-white dark:bg-dark-card rounded-lg shadow p-4 animate-pulse">
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-16 bg-gray-100 dark:bg-gray-800 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-600 dark:text-red-400">
        ⚠️ {error}
      </div>
    );
  }

  if (!recommendations.length) {
    return (
      <div className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-gray-500 dark:text-gray-400 text-center">
        Tidak ada rekomendasi
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow p-4">
      <h3 className="text-lg font-bold mb-3 text-gray-900 dark:text-white">⚡ Recommendations</h3>
      <div className="space-y-2">
        {recommendations.map((rec, idx) => (
          <RecommendationCard key={idx} recommendation={rec} />
        ))}
      </div>
    </div>
  );
};

export default RecommendationCenter;
