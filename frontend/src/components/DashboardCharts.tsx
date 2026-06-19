// src/components/DashboardCharts.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

const DashboardCharts: React.FC = () => {
  const [eventVolume, setEventVolume] = useState<any[]>([]);
  const [caseStatus, setCaseStatus] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChartData();
  }, []);

  const loadChartData = async () => {
    try {
      // Get case stats for status chart
      const stats = await api.getCaseStats();
      setCaseStatus([
        { name: 'Open', value: stats.open || 0, color: '#f59e0b' },
        { name: 'In Progress', value: stats.in_progress || 0, color: '#3b82f6' },
        { name: 'Closed', value: stats.closed || 0, color: '#10b981' },
        { name: 'Archived', value: stats.archived || 0, color: '#6b7280' }
      ]);
      
      // Get event volume from system info
      const systemInfo = await api.getSystemInfo();
      const totalEvents = systemInfo.statistics?.total_events || 0;
      
      // Generate sample daily data (in production, get from API)
      setEventVolume([
        { date: 'Day 1', events: Math.floor(totalEvents * 0.1) },
        { date: 'Day 2', events: Math.floor(totalEvents * 0.15) },
        { date: 'Day 3', events: Math.floor(totalEvents * 0.2) },
        { date: 'Day 4', events: Math.floor(totalEvents * 0.25) },
        { date: 'Day 5', events: Math.floor(totalEvents * 0.3) },
      ]);
    } catch (error) {
      console.error('Error loading chart data:', error);
      // Set default data
      setCaseStatus([
        { name: 'Open', value: 0, color: '#f59e0b' },
        { name: 'In Progress', value: 0, color: '#3b82f6' },
        { name: 'Closed', value: 0, color: '#10b981' },
        { name: 'Archived', value: 0, color: '#6b7280' }
      ]);
      setEventVolume([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-4 animate-pulse">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
        <div className="bg-white rounded-lg shadow p-4 animate-pulse">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      {/* Event Volume Chart */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Event Volume Trend</h3>
        {eventVolume.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={eventVolume}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="events" stroke="#3b82f6" name="Events" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-400">
            No event data available
          </div>
        )}
      </div>

      {/* Case Status Distribution */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Case Status Distribution</h3>
        {caseStatus.some(s => s.value > 0) ? (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={caseStatus}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => percent > 0 ? `${name}: ${(percent * 100).toFixed(0)}%` : ''}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {caseStatus.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-64 flex items-center justify-center text-gray-400">
            No case status data available
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardCharts;