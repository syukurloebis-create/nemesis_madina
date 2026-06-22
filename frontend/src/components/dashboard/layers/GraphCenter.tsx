// src/components/dashboard/layers/GraphCenter.tsx
import React from 'react';

interface GraphCenterProps {
  graphData: {
    entities: any[];
    relationships: any[];
    metrics: any;
    communities: any[];
    keyActors: any[];
  };
}

export const GraphCenter: React.FC<GraphCenterProps> = ({ graphData }) => {
  const { entities, relationships, metrics, communities, keyActors } = graphData;

  const totalEntities = metrics?.total_entities || entities?.length || 0;
  const totalRelationships = metrics?.total_relationships || relationships?.length || 0;

  if (!entities || entities.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500 dark:text-gray-400">No graph data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Network Intelligence</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Entities</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{totalEntities}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Relationships</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{totalRelationships}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Communities</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{communities?.length || 0}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Key Actors</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{keyActors?.length || 0}</p>
        </div>
      </div>

      {/* Key Actors */}
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
                  {actor.type} • {actor.connections || 0} connections
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  Influence: {(actor.influence_score || actor.centrality_score || 0).toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GraphCenter;