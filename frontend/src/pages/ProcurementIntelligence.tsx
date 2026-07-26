import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface CollusionPattern {
  vendor: string;
  score: number;
  reason: string;
  id?: string;
}

export default function ProcurementIntelligence() {
  const [summary, setSummary] = useState({ 
    total_projects: 0, 
    total_value: 0, 
    risk_score: 0 
  });
  const [patterns, setPatterns] = useState<CollusionPattern[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [summaryRes, patternsRes] = await Promise.all([
          api.get('/api/v1/procurement/summary'),
          api.get('/api/v1/procurement/collusions'),
        ]);
        setSummary(summaryRes?.data || { total_projects: 0, total_value: 0, risk_score: 0 });
        
        const rawPatterns = patternsRes?.data || [];
        // Filter duplicate vendor
        const uniquePatterns = rawPatterns.filter(
          (p: any, index: number, self: any[]) =>
            index === self.findIndex((x: any) => x.vendor === p.vendor)
        );
        setPatterns(uniquePatterns);
      } catch (error) {
        console.error('Failed to load procurement intelligence:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return <div className="p-6 text-white">Loading procurement intelligence...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white">Procurement Intelligence</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <StatCard label="Total Projects" value={summary.total_projects} />
        <StatCard label="Total Value" value={`Rp ${(summary.total_value / 1000000000).toFixed(1)}B`} />
        <StatCard label="Risk Score" value={`${summary.risk_score}%`} />
      </div>

      <div className="mt-6 bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-700">
          <h2 className="text-white font-semibold">Collusion Patterns</h2>
        </div>
        
        {patterns.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            No collusion patterns detected
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700/50">
                <tr>
                  <th className="px-4 py-2 text-left text-gray-300 text-sm">#</th>
                  <th className="px-4 py-2 text-left text-gray-300 text-sm">Vendor</th>
                  <th className="px-4 py-2 text-left text-gray-300 text-sm">Score</th>
                  <th className="px-4 py-2 text-left text-gray-300 text-sm">Reason</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {patterns.map((p, index) => {
                  // UNIQUE KEY: guaranteed unique
                  const uniqueKey = `pattern-${index}-${p.vendor.replace(/\s/g, '')}-${Date.now()}`;
                  return (
                    <tr key={uniqueKey} className="hover:bg-gray-700/30 transition-colors">
                      <td className="px-4 py-2 text-gray-500 text-sm">{index + 1}</td>
                      <td className="px-4 py-2 text-white font-medium">{p.vendor}</td>
                      <td className="px-4 py-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          p.score > 70 ? 'bg-red-500/20 text-red-400' :
                          p.score > 50 ? 'bg-orange-500/20 text-orange-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {p.score}%
                        </span>
                      </td>
                      <td className="px-4 py-2 text-gray-300 text-sm">{p.reason}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 text-center">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="text-white text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
