// src/components/entity/EntitySearch.tsx
import React from 'react';
import { Entity } from '../../stores/entityStore';

interface EntitySearchProps {
  entities: Entity[];
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSelectEntity: (entity: Entity) => void;
  selectedEntityId?: string;
}

const typeIcons = {
  vendor: '🏢',
  institution: '🏛️',
  individual: '👤',
  package: '📦',
};

const getRiskColor = (score: number) => {
  if (score >= 80) return 'bg-red-100 text-red-800';
  if (score >= 60) return 'bg-orange-100 text-orange-800';
  if (score >= 40) return 'bg-yellow-100 text-yellow-800';
  return 'bg-green-100 text-green-800';
};

export const EntitySearch: React.FC<EntitySearchProps> = ({
  entities,
  searchQuery,
  onSearchChange,
  onSelectEntity,
  selectedEntityId,
}) => {
  const filteredEntities = entities.filter(e =>
    e.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    e.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <div className="relative">
          <input
            type="text"
            placeholder="Search by name or ID..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
        </div>
      </div>
      
      <div className="divide-y max-h-96 overflow-y-auto">
        {filteredEntities.map((entity) => (
          <button
            key={entity.id}
            onClick={() => onSelectEntity(entity)}
            className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
              selectedEntityId === entity.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{typeIcons[entity.type]}</span>
                <div>
                  <p className="font-medium text-gray-900">{entity.name}</p>
                  <p className="text-xs text-gray-500">{entity.id}</p>
                </div>
              </div>
              <div className="text-right">
                <span className={`px-2 py-0.5 text-xs rounded-full ${getRiskColor(entity.risk_score)}`}>
                  Risk: {entity.risk_score}%
                </span>
                <p className="text-xs text-gray-500 mt-1">{entity.total_cases} cases</p>
              </div>
            </div>
          </button>
        ))}
        
        {filteredEntities.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No entities found matching "{searchQuery}"
          </div>
        )}
      </div>
    </div>
  );
};
