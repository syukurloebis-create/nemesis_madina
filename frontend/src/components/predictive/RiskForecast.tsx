import React from 'react';
import { TrendingUp, TrendingDown, Activity, AlertTriangle } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface RiskForecastProps {
  entityId: string;
  historicalData: { date: string; risk: number }[];
  predictedData: { date: string; risk: number; confidence_lower: number; confidence_upper: number }[];
  trend: 'increasing' | 'decreasing' | 'stable';
  confidence: number;
}

export const RiskForecast: React.FC<RiskForecastProps> = ({
  entityId,
  historicalData,
  predictedData,
  trend,
  confidence,
}) => {
  const combinedData = [...historicalData, ...predictedData];

  const getTrendColor = () => {
    if (trend === 'increasing') return 'text-red-400';
    if (trend === 'decreasing') return 'text-green-400';
    return 'text-yellow-400';
  };

  const getTrendIcon = () => {
    if (trend === 'increasing') return <TrendingUp className="w-5 h-5" />;
    if (trend === 'decreasing') return <TrendingDown className="w-5 h-5" />;
    return <Activity className="w-5 h-5" />;
  };

  return (
    <div className="bg-gray-900/95 rounded-xl border border-purple-500/30 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-purple-400 flex items-center gap-2">
          <Activity className="w-5 h-5" />
          Risk Forecast - {entityId.slice(0, 12)}...
        </h3>
        <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${getTrendColor()} bg-opacity-10`}>
          {getTrendIcon()}
          <span className="text-sm font-medium">{trend.toUpperCase()} TREND</span>
          <span className="text-xs opacity-75">Confidence: {(confidence * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={combinedData}>
            <defs>
              <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ff4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a1a2e" />
            <XAxis 
              dataKey="date" 
              tick={{ fill: '#666', fontSize: 10 }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis 
              domain={[0, 1]} 
              tick={{ fill: '#666', fontSize: 10 }}
              tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
            />
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-gray-900 border border-purple-500/30 rounded-lg p-3">
                      <p className="text-xs text-gray-400">{payload[0].payload.date}</p>
                      <p className="text-lg font-bold text-purple-400">
                        {(payload[0].value * 100).toFixed(1)}%
                      </p>
                      {payload[0].payload.confidence_lower && (
                        <p className="text-xs text-gray-500">
                          Range: {(payload[0].payload.confidence_lower * 100).toFixed(0)}% - {(payload[0].payload.confidence_upper * 100).toFixed(0)}%
                        </p>
                      )}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Area
              type="monotone"
              dataKey="risk"
              stroke="#ff4444"
              strokeWidth={2}
              fill="url(#riskGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-purple-500 rounded-full" />
              <span>Historical</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span>Predicted</span>
            </div>
          </div>
          <button className="text-cyan-400 hover:text-cyan-300">
            View Full Analysis →
          </button>
        </div>
      </div>
    </div>
  );
};
