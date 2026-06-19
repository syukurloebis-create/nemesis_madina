// src/components/executive/TrustHeatmap.tsx
import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, TrendingDown } from 'lucide-react';

interface RegionData {
  name: string;
  trustScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  trend: 'up' | 'down' | 'stable';
}

export const TrustHeatmap: React.FC = () => {
  const [regions, setRegions] = useState<RegionData[]>([
    { name: 'Jakarta Pusat', trustScore: 87.5, riskLevel: 'low', trend: 'up' },
    { name: 'Jakarta Selatan', trustScore: 72.3, riskLevel: 'medium', trend: 'down' },
    { name: 'Jakarta Barat', trustScore: 45.8, riskLevel: 'high', trend: 'down' },
    { name: 'Jakarta Timur', trustScore: 91.2, riskLevel: 'low', trend: 'up' },
    { name: 'Jakarta Utara', trustScore: 63.4, riskLevel: 'medium', trend: 'stable' },
    { name: 'Bogor', trustScore: 78.9, riskLevel: 'medium', trend: 'up' },
    { name: 'Depok', trustScore: 82.1, riskLevel: 'low', trend: 'up' },
    { name: 'Tangerang', trustScore: 55.6, riskLevel: 'high', trend: 'down' },
    { name: 'Bekasi', trustScore: 68.7, riskLevel: 'medium', trend: 'stable' },
  ]);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'bg-gradient-to-br from-green-500/20 to-green-600/10 border-green-500/30';
      case 'medium': return 'bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border-yellow-500/30';
      case 'high': return 'bg-gradient-to-br from-orange-500/20 to-orange-600/10 border-orange-500/30';
      case 'critical': return 'bg-gradient-to-br from-red-500/20 to-red-600/10 border-red-500/30';
      default: return 'bg-gray-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-900/95 rounded-xl border border-cyan-500/30 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-cyan-400 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Trust Heatmap by Region
        </h3>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-green-500 rounded" />
            <span>Low Risk</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-yellow-500 rounded" />
            <span>Medium</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-orange-500 rounded" />
            <span>High</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded" />
            <span>Critical</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {regions.map((region) => (
          <div
            key={region.name}
            className={`p-3 rounded-lg border ${getRiskColor(region.riskLevel)} transition-all hover:scale-105`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-white text-sm">{region.name}</span>
              {region.trend === 'up' && <TrendingUp className="w-3 h-3 text-green-400" />}
              {region.trend === 'down' && <TrendingDown className="w-3 h-3 text-red-400" />}
              {region.trend === 'stable' && <div className="w-3 h-0.5 bg-gray-400 rounded" />}
            </div>
            <div className="text-2xl font-bold mb-1">
              <span className={getScoreColor(region.trustScore)}>{region.trustScore.toFixed(1)}%</span>
            </div>
            <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  region.riskLevel === 'low' ? 'bg-green-500' :
                  region.riskLevel === 'medium' ? 'bg-yellow-500' :
                  region.riskLevel === 'high' ? 'bg-orange-500' : 'bg-red-500'
                }`}
                style={{ width: `${region.trustScore}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Last updated: {new Date().toLocaleString()}</span>
          <button className="text-cyan-400 hover:text-cyan-300">View Detailed Report →</button>
        </div>
      </div>
    </div>
  );
};