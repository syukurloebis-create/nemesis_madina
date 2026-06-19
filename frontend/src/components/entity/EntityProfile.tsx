// src/components/entity/EntityProfile.tsx
import React from 'react';
import { Entity } from '../../stores/entityStore';

interface EntityProfileProps {
  entity: Entity | null;
  onClose?: () => void;
}

const typeColors = {
  vendor: 'bg-purple-100 text-purple-800',
  institution: 'bg-blue-100 text-blue-800',
  individual: 'bg-green-100 text-green-800',
  package: 'bg-orange-100 text-orange-800',
};

export const EntityProfile: React.FC<EntityProfileProps> = ({ entity, onClose }) => {
  if (!entity) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        Select an entity to view details
      </div>
    );
  }

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-600';
    if (score >= 60) return 'text-orange-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getTrustColor = (score: number) => {
    if (score >= 70) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h2 className="text-xl font-bold text-gray-900">{entity.name}</h2>
              <span className={`px-2 py-0.5 text-xs rounded-full ${typeColors[entity.type]}`}>
                {entity.type.toUpperCase()}
              </span>
            </div>
            <p className="text-sm text-gray-500">ID: {entity.id}</p>
          </div>
          {onClose && (
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          )}
        </div>
      </div>
      
      <div className="p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Risk Score</p>
            <p className={`text-xl font-bold ${getRiskColor(entity.risk_score)}`}>
              {entity.risk_score}%
            </p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Trust Score</p>
            <p className={`text-xl font-bold ${getTrustColor(entity.trust_score)}`}>
              {entity.trust_score}%
            </p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Total Cases</p>
            <p className="text-xl font-bold text-gray-900">{entity.total_cases}</p>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500">Total Amount</p>
            <p className="text-xl font-bold text-gray-900">
              Rp {(entity.total_amount / 1000000000).toFixed(1)}B
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">First Seen</span>
            <span className="text-gray-900">{new Date(entity.first_seen).toLocaleDateString()}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Last Seen</span>
            <span className="text-gray-900">{new Date(entity.last_seen).toLocaleDateString()}</span>
          </div>
          {Object.entries(entity.metadata).map(([key, value]) => (
            <div key={key} className="flex justify-between text-sm">
              <span className="text-gray-500 capitalize">{key}</span>
              <span className="text-gray-900">{String(value)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
