import React from 'react';

interface ConfidenceBadgeProps {
  confidence: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence,
  size = 'md',
  showLabel = true,
}) => {
  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  const getColor = () => {
    if (confidence >= 0.8) return 'bg-green-500/20 text-green-400 border-green-500/30';
    if (confidence >= 0.6) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    if (confidence >= 0.4) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    return 'bg-red-500/20 text-red-400 border-red-500/30';
  };

  return (
    <div className={`inline-flex items-center gap-1.5 rounded-full border ${sizes[size]} ${getColor()}`}>
      <span className="font-medium">{(confidence * 100).toFixed(0)}%</span>
      {showLabel && <span className="text-xs opacity-70">confidence</span>}
    </div>
  );
};

export default ConfidenceBadge;
