import React, { useState } from 'react';
import GraphVisualization from '../components/graph/GraphVisualization';
import { useAuthStore } from '../stores/authStore';

const GraphIntelligence: React.FC = () => {
  const [selectedCaseId, setSelectedCaseId] = useState<string>('');
  const [showGraph, setShowGraph] = useState(false);
  const { token } = useAuthStore();

  const patterns = [
    { id: 1, name: 'Vendor Address Collusion', severity: 'high', confidence: 92, entities: ['PT. Maju Jaya', 'CV. Karya Mandiri'] },
    { id: 2, name: 'Bid Rigging Pattern', severity: 'critical', confidence: 88, entities: ['PT. Maju Jaya', 'PT. Bangun Nusantara'] },
    { id: 3, name: 'Subcontractor Loop', severity: 'medium', confidence: 75, entities: ['CV. Karya Mandiri', 'PT. Bangun Nusantara'] },
    { id: 4, name: 'Conflict of Interest', severity: 'high', confidence: 85, entities: ['Dr. Ahmad Fauzi', 'Kementerian PUPR'] },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Graph Intelligence</h1>
        <p className="text-gray-400 text-sm mt-1">Collusion detection, influence mapping, and relationship analysis</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Patterns</p>
          <p className="text-3xl font-bold text-white">{patterns.length}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Critical</p>
          <p className="text-3xl font-bold text-red-500">
            {patterns.filter(p => p.severity === 'critical').length}
          </p>
        </div>
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">High Risk</p>
          <p className="text-3xl font-bold text-orange-500">
            {patterns.filter(p => p.severity === 'high').length}
          </p>
        </div>
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Avg Confidence</p>
          <p className="text-3xl font-bold text-yellow-500">85%</p>
        </div>
      </div>

      {/* Collusion Patterns List */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Collusion Patterns</h2>
        </div>
        <div className="divide-y divide-gray-700">
          {patterns.map((pattern) => (
            <div key={pattern.id} className={`p-4 border-l-4 ${getSeverityColor(pattern.severity)}`}>
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-white">{pattern.name}</h3>
                  <div className="flex gap-2 mt-2">
                    {pattern.entities.map((entity, idx) => (
                      <span key={idx} className="text-xs px-2 py-1 bg-gray-700 rounded-lg text-gray-300">
                        {entity}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-sm text-gray-400">Confidence: <span className="text-white font-bold">{pattern.confidence}%</span></span>
                  <p className="text-xs text-gray-500 mt-1">2 related cases</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Graph Visualization */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Network Analysis</h2>
          <p className="text-xs text-gray-500 mt-1">Click on any node to see details</p>
        </div>
        <div className="p-4">
          <GraphVisualization />
        </div>
      </div>
    </div>
  );
};

export default GraphIntelligence;
