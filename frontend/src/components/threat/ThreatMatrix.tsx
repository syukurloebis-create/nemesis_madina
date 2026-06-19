# src/components/threat/ThreatMatrix.tsx
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, AlertTriangle, Skull, Zap, Eye, TrendingUp } from 'lucide-react';

interface Threat {
  id: string;
  name: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  count: number;
  trend: 'up' | 'down' | 'stable';
  description: string;
}

export const ThreatMatrix: React.FC = () => {
  const [threats, setThreats] = useState<Threat[]>([
    {
      id: '1',
      name: 'Hash Mismatch',
      severity: 'critical',
      category: 'Integrity',
      count: 0,
      trend: 'stable',
      description: 'Event hash does not match recomputed value',
    },
    {
      id: '2',
      name: 'Invalid Transition',
      severity: 'high',
      category: 'Business',
      count: 1,
      trend: 'up',
      description: 'Business state transition violation',
    },
    {
      id: '3',
      name: 'Duplicate Replay',
      severity: 'medium',
      category: 'Security',
      count: 0,
      trend: 'stable',
      description: 'Duplicate event detected',
    },
    {
      id: '4',
      name: 'Orphan Event',
      severity: 'high',
      category: 'Lineage',
      count: 0,
      trend: 'stable',
      description: 'Event with broken previous hash link',
    },
    {
      id: '5',
      name: 'Tamper Detection',
      severity: 'critical',
      category: 'Forensic',
      count: 0,
      trend: 'stable',
      description: 'Potential data tampering detected',
    },
  ]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-500 bg-red-500/10 border-red-500/30';
      case 'high': return 'text-orange-500 bg-orange-500/10 border-orange-500/30';
      case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30';
      default: return 'text-blue-500 bg-blue-500/10 border-blue-500/30';
    }
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return <TrendingUp className="w-3 h-3 text-red-500" />;
    if (trend === 'down') return <TrendingUp className="w-3 h-3 text-green-500 transform rotate-180" />;
    return <div className="w-3 h-3 rounded-full bg-gray-500" />;
  };

  const totalRiskScore = threats.reduce((acc, t) => {
    const multiplier = t.severity === 'critical' ? 10 : t.severity === 'high' ? 5 : t.severity === 'medium' ? 2 : 1;
    return acc + (t.count * multiplier);
  }, 0);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-red-400 flex items-center gap-2">
          <Skull className="w-5 h-5" />
          Threat Intelligence Matrix
        </h3>
        <div className="text-right">
          <div className="text-2xl font-bold text-red-400">{totalRiskScore}</div>
          <div className="text-xs text-gray-500">Risk Score</div>
        </div>
      </div>

      <div className="space-y-2 flex-1 overflow-y-auto">
        {threats.map((threat) => (
          <motion.div
            key={threat.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`p-3 rounded-lg border ${getSeverityColor(threat.severity)}`}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                <span className="font-medium">{threat.name}</span>
              </div>
              <div className="flex items-center gap-2">
                {getTrendIcon(threat.trend)}
                <span className="text-xs font-mono">{threat.count}</span>
              </div>
            </div>
            <p className="text-xs text-gray-400">{threat.description}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs px-2 py-0.5 rounded bg-gray-800/50">{threat.category}</span>
              <span className="text-xs text-gray-500">Severity: {threat.severity.toUpperCase()}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Last Scan: {new Date().toLocaleTimeString()}</span>
          <button className="text-cyan-400 hover:text-cyan-300">Run Forensic Scan →</button>
        </div>
      </div>
    </div>
  );
};