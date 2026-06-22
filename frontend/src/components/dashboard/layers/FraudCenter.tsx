// src/components/dashboard/layers/FraudCenter.tsx
import React from 'react';

interface FraudCenterProps {
  graphData: {
    entities: any[];
    relationships: any[];
    keyActors: any[];
  };
}

export const FraudCenter: React.FC<FraudCenterProps> = ({ graphData }) => {
  const { entities, relationships, keyActors } = graphData;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Fraud Center</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Entities</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{entities?.length || 0}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Relationships</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{relationships?.length || 0}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Key Actors</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{keyActors?.length || 0}</p>
        </div>
      </div>

      {/* Key Actors List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Key Actors</h3>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {keyActors?.slice(0, 10).map((actor: any) => (
            <div key={actor.id} className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-800 dark:text-white">{actor.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {actor.entity_type || actor.type} • {actor.relationships || 0} connections
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  (actor.risk_score || 0) > 70
                    ? 'bg-red-100 text-red-800'
                    : (actor.risk_score || 0) > 40
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-green-100 text-green-800'
                }`}>
                  Risk: {actor.risk_score || 0}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FraudCenter;