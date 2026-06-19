// ConfidenceScore.tsx - Visual confidence indicator
import React from 'react';
import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

interface ConfidenceScoreProps {
  score: number;
  showLabel?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const ConfidenceScore: React.FC<ConfidenceScoreProps> = ({
  score,
  showLabel = true,
  className = '',
  size = 'md'
}) => {
  const getScoreColor = (s: number) => {
    if (s >= 80) return 'text-green-400';
    if (s >= 60) return 'text-yellow-400';
    if (s >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBg = (s: number) => {
    if (s >= 80) return 'bg-green-500';
    if (s >= 60) return 'bg-yellow-500';
    if (s >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreLabel = (s: number) => {
    if (s >= 80) return 'High Confidence';
    if (s >= 60) return 'Medium Confidence';
    if (s >= 40) return 'Low Confidence';
    return 'Very Low Confidence';
  };

  const getScoreIcon = (s: number) => {
    if (s >= 80) return <CheckCircle className="w-4 h-4 text-green-400" />;
    if (s >= 60) return <Shield className="w-4 h-4 text-yellow-400" />;
    if (s >= 40) return <AlertTriangle className="w-4 h-4 text-orange-400" />;
    return <AlertTriangle className="w-4 h-4 text-red-400" />;
  };

  const sizeClasses = {
    sm: { text: 'text-xs', bar: 'h-1', icon: 'w-3 h-3' },
    md: { text: 'text-sm', bar: 'h-1.5', icon: 'w-4 h-4' },
    lg: { text: 'text-base', bar: 'h-2', icon: 'w-5 h-5' }
  };

  const sizeClass = sizeClasses[size] || sizeClasses.md;

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="flex items-center gap-1.5">
        {getScoreIcon(score)}
        <span className={`font-medium ${getScoreColor(score)} ${sizeClass.text}`}>
          {score}%
        </span>
      </div>
      
      {showLabel && (
        <span className={`text-gray-400 ${sizeClass.text}`}>
          {getScoreLabel(score)}
        </span>
      )}
      
      <div className={`flex-1 ${sizeClass.bar} bg-gray-700 rounded-full overflow-hidden min-w-[60px]`}>
        <div 
          className={`h-full rounded-full ${getScoreBg(score)} transition-all duration-500`}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
};

export default ConfidenceScore;
