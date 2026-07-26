import React from 'react';
import { HealthResponse } from '../../services/intelligence';
import { Activity, Database, Server, Cpu } from 'lucide-react';

interface Props {
  health?: HealthResponse;
}

export default function IntelligenceStatusBar({ health }: Props) {
  const isHealthy = health?.status === 'healthy';

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-4 flex items-center justify-between flex-wrap gap-3">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Activity className={`w-4 h-4 ${isHealthy ? 'text-green-500' : 'text-red-500'}`} />
          <span className={`text-sm font-medium ${isHealthy ? 'text-green-400' : 'text-red-400'}`}>
            {isHealthy ? 'Operational' : 'Degraded'}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Server className="w-3 h-3" />
            {health?.service ?? 'N/A'}
          </span>
          <span className="flex items-center gap-1">
            <Cpu className="w-3 h-3" />
            v{health?.version ?? '8.1.0'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-400">Risk Engine</span>
          <span className="text-white font-medium">98%</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-400">Graph Engine</span>
          <span className="text-white font-medium">99%</span>
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          <span className="text-gray-400">Fraud Engine</span>
          <span className="text-white font-medium">96%</span>
        </span>
      </div>
    </div>
  );
}