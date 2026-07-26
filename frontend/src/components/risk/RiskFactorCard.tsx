import React from 'react';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface RiskFactorCardProps {
  name: string;
  value: number;
  change?: number;
  description?: string;
  color?: 'red' | 'orange' | 'yellow' | 'green';
}

export const RiskFactorCard: React.FC<RiskFactorCardProps> = ({
  name,
  value,
  change,
  description,
  color = 'orange',
}) => {
  const colors = {
    red: 'border-red-500/20 bg-red-500/10',
    orange: 'border-orange-500/20 bg-orange-500/10',
    yellow: 'border-yellow-500/20 bg-yellow-500/10',
    green: 'border-green-500/20 bg-green-500/10',
  };

  const textColors = {
    red: 'text-red-400',
    orange: 'text-orange-400',
    yellow: 'text-yellow-400',
    green: 'text-green-400',
  };

  const ChangeIcon = change && change > 0 ? ArrowUp : change && change < 0 ? ArrowDown : Minus;

  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-gray-400">{name}</p>
          <p className={`text-2xl font-bold mt-1 ${textColors[color]}`}>{value}%</p>
          {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
        </div>
        {change !== undefined && (
          <div className={`flex items-center gap-1 text-sm ${change > 0 ? 'text-green-400' : change < 0 ? 'text-red-400' : 'text-gray-400'}`}>
            <ChangeIcon className="w-4 h-4" />
            {Math.abs(change)}%
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskFactorCard;
