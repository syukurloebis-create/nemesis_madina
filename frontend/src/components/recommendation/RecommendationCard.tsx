// RecommendationCard.tsx
import React from 'react';

interface Recommendation {
  id: string;
  recommendation_text: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: string;
  timeline_days?: number;
}

const priorityConfig = {
  CRITICAL: { 
    border: 'border-red-500 dark:border-red-400', 
    bg: 'bg-red-50 dark:bg-red-900/20', 
    label: '🔴 CRITICAL',
    text: 'text-red-700 dark:text-red-400'
  },
  HIGH: { 
    border: 'border-orange-500 dark:border-orange-400', 
    bg: 'bg-orange-50 dark:bg-orange-900/20', 
    label: '🟠 HIGH',
    text: 'text-orange-700 dark:text-orange-400'
  },
  MEDIUM: { 
    border: 'border-yellow-500 dark:border-yellow-400', 
    bg: 'bg-yellow-50 dark:bg-yellow-900/20', 
    label: '🟡 MEDIUM',
    text: 'text-yellow-700 dark:text-yellow-400'
  },
  LOW: { 
    border: 'border-green-500 dark:border-green-400', 
    bg: 'bg-green-50 dark:bg-green-900/20', 
    label: '🟢 LOW',
    text: 'text-green-700 dark:text-green-400'
  },
};

export const RecommendationCard: React.FC<{ recommendation: Recommendation }> = ({ 
  recommendation 
}) => {
  const config = priorityConfig[recommendation.priority] || priorityConfig.MEDIUM;
  
  return (
    <div className={`border-l-4 ${config.border} ${config.bg} p-3 rounded-r`}>
      <div className="font-medium text-sm text-gray-900 dark:text-white">
        {recommendation.recommendation_text}
      </div>
      <div className="flex gap-3 mt-1 text-xs">
        <span className={`font-semibold ${config.text}`}>{config.label}</span>
        <span className="text-gray-600 dark:text-gray-400">Status: {recommendation.status}</span>
        {recommendation.timeline_days && (
          <span className="text-gray-600 dark:text-gray-400">⏱️ {recommendation.timeline_days} hari</span>
        )}
      </div>
    </div>
  );
};

export default RecommendationCard;
