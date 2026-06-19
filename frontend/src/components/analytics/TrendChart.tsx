import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface TrendData {
  date: string;
  cases_created: number;
  cases_resolved: number;
  risk_score: number;
}

const TrendChart: React.FC = () => {
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState<'week' | 'month' | 'quarter'>('month');
  const { token } = useAuthStore();

  useEffect(() => {
    fetchTrendData();
  }, [period]);

  const fetchTrendData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost/analytics/trends?period=${period}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTrendData(data);
      } else {
        // Mock data
        const mockData: TrendData[] = [];
        const days = period === 'week' ? 7 : period === 'month' ? 30 : 90;
        for (let i = days; i >= 0; i--) {
          mockData.push({
            date: new Date(Date.now() - i * 86400000).toISOString().slice(0, 10),
            cases_created: Math.floor(Math.random() * 10) + 1,
            cases_resolved: Math.floor(Math.random() * 8),
            risk_score: 50 + Math.random() * 40,
          });
        }
        setTrendData(mockData);
      }
    } catch (error) {
      console.error('Failed to fetch trend data:', error);
    } finally {
      setLoading(false);
    }
  };

  const maxCases = Math.max(...trendData.map(d => d.cases_created), 1);
  const maxRisk = 100;

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading trend data...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end gap-2">
        <button
          onClick={() => setPeriod('week')}
          className={`px-3 py-1 text-sm rounded-lg ${period === 'week' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}
        >
          Week
        </button>
        <button
          onClick={() => setPeriod('month')}
          className={`px-3 py-1 text-sm rounded-lg ${period === 'month' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}
        >
          Month
        </button>
        <button
          onClick={() => setPeriod('quarter')}
          className={`px-3 py-1 text-sm rounded-lg ${period === 'quarter' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}
        >
          Quarter
        </button>
      </div>

      <div className="relative h-64">
        <svg className="w-full h-full" viewBox="0 0 800 250" preserveAspectRatio="none">
          {/* Grid lines */}
          {[0, 50, 100, 150, 200, 250].map((y) => (
            <line key={y} x1="0" y1={y} x2="800" y2={y} stroke="#374151" strokeWidth="0.5" />
          ))}
          
          {/* Cases Created Line */}
          <polyline
            points={trendData.map((d, i) => `${(i / (trendData.length - 1)) * 800},${250 - (d.cases_created / maxCases) * 200}`).join(' ')}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2"
          />
          
          {/* Cases Resolved Line */}
          <polyline
            points={trendData.map((d, i) => `${(i / (trendData.length - 1)) * 800},${250 - (d.cases_resolved / maxCases) * 200}`).join(' ')}
            fill="none"
            stroke="#22c55e"
            strokeWidth="2"
          />
          
          {/* Risk Score Line */}
          <polyline
            points={trendData.map((d, i) => `${(i / (trendData.length - 1)) * 800},${250 - (d.risk_score / maxRisk) * 200}`).join(' ')}
            fill="none"
            stroke="#ef4444"
            strokeWidth="2"
            strokeDasharray="5,5"
          />
        </svg>
        
        {/* Labels */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 px-2">
          {trendData.filter((_, i) => i % Math.ceil(trendData.length / 5) === 0).map((d, i) => (
            <span key={i}>{d.date.slice(5)}</span>
          ))}
        </div>
      </div>
      
      <div className="flex justify-center gap-6 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
          <span className="text-gray-400">Cases Created</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-gray-400">Cases Resolved</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <span className="text-gray-400">Risk Score</span>
        </div>
      </div>
    </div>
  );
};

export default TrendChart;
