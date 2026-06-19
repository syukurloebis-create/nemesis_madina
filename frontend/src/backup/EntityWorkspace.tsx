import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Entity {
  id: string;
  name: string;
  type: string;
  risk_score: number;
  risk_level: string;
  metadata: Record<string, any>;
}

const EntityWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const [entities] = useState<Entity[]>([
    { id: '1', name: 'PT. Maju Jaya', type: 'vendor', risk_score: 92, risk_level: 'critical', metadata: { registration: '1234567890', established: '2010', employees: 250, revenue: 'Rp 500M' } },
    { id: '2', name: 'CV. Karya Mandiri', type: 'vendor', risk_score: 88, risk_level: 'high', metadata: { registration: '9876543210', established: '2015', employees: 120, revenue: 'Rp 280M' } },
    { id: '3', name: 'Kementerian PUPR', type: 'institution', risk_score: 65, risk_level: 'medium', metadata: { type: 'government', sector: 'infrastructure' } },
    { id: '4', name: 'PT. Bangun Nusantara', type: 'vendor', risk_score: 78, risk_level: 'high', metadata: { registration: '5555555555', established: '2008', employees: 300, revenue: 'Rp 620M' } },
    { id: '5', name: 'Dr. Ahmad Fauzi', type: 'individual', risk_score: 68, risk_level: 'medium', metadata: { position: 'Pejabat', institution: 'Kementerian' } },
  ]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  const handleInvestigate = (entity: Entity) => {
    // Navigate ke investigation case dengan query params
    navigate(`/investigation?entity=${encodeURIComponent(entity.name)}&type=${entity.type}`);
  };

  const handleExportReport = (entity: Entity) => {
    const reportData = {
      entity_name: entity.name,
      entity_type: entity.type,
      risk_score: entity.risk_score,
      risk_level: entity.risk_level,
      metadata: entity.metadata,
      generated_at: new Date().toISOString(),
      report_type: 'entity_risk_assessment'
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `entity_${entity.name.replace(/\s/g, '_')}_risk_report.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    alert(`✅ Report for ${entity.name} exported successfully!`);
  };

  const handleViewDetails = (entity: Entity) => {
    setSelectedEntity(entity);
    setShowDetail(true);
  };

  const getRiskColor = (score: number) => {
    if (score >= 85) return 'text-red-500';
    if (score >= 70) return 'text-orange-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getRiskBgColor = (score: number) => {
    if (score >= 85) return 'bg-red-500/20';
    if (score >= 70) return 'bg-orange-500/20';
    if (score >= 40) return 'bg-yellow-500/20';
    return 'bg-green-500/20';
  };

  const filteredEntities = entities.filter(e =>
    e.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    e.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Entity Workspace</h1>
        <p className="text-gray-400 text-sm mt-1">Search and manage entities, view risk profiles</p>
      </div>

      {/* Search */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="relative">
          <input
            type="text"
            placeholder="Search entities by name or type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 pl-10 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
          />
          <span className="absolute left-3 top-3 text-gray-400">🔍</span>
        </div>
      </div>

      {/* Entity List */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Entities</h2>
          <p className="text-xs text-gray-500 mt-1">Click on any entity to view details</p>
        </div>
        <div className="divide-y divide-gray-700">
          {filteredEntities.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No entities found</div>
          ) : (
            filteredEntities.map((entity) => (
              <div
                key={entity.id}
                onClick={() => handleViewDetails(entity)}
                className="p-4 hover:bg-gray-700/50 cursor-pointer transition-colors"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-white">{entity.name}</h3>
                    <p className="text-sm text-gray-400">{entity.type}</p>
                  </div>
                  <div className={`px-3 py-1 rounded-full ${getRiskBgColor(entity.risk_score)}`}>
                    <span className={`text-sm font-bold ${getRiskColor(entity.risk_score)}`}>
                      {entity.risk_score}%
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Entity Detail Modal */}
      {showDetail && selectedEntity && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[85vh] overflow-y-auto">
            <div className="sticky top-0 bg-gray-800 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-bold text-white">Entity Details</h2>
              <button onClick={() => setShowDetail(false)} className="text-gray-400 hover:text-white">✕</button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Header */}
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-2xl font-bold text-white">{selectedEntity.name}</h3>
                  <p className="text-gray-400">{selectedEntity.type}</p>
                </div>
                <div className={`px-4 py-2 rounded-full ${getRiskBgColor(selectedEntity.risk_score)}`}>
                  <span className={`text-xl font-bold ${getRiskColor(selectedEntity.risk_score)}`}>
                    {selectedEntity.risk_score}% Risk
                  </span>
                </div>
              </div>

              {/* Metadata Info */}
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(selectedEntity.metadata).map(([key, value]) => (
                  <div key={key} className="bg-gray-700/30 rounded-lg p-3">
                    <p className="text-gray-400 text-sm capitalize">{key}:</p>
                    <p className="text-white">{String(value)}</p>
                  </div>
                ))}
              </div>

              {/* Risk Factors */}
              <div>
                <h4 className="font-semibold text-white mb-3">Risk Factors</h4>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Transaction Pattern</span>
                    <span className="text-red-400">High Risk</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Vendor Concentration</span>
                    <span className="text-orange-400">Medium Risk</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Compliance History</span>
                    <span className="text-green-400">Low Risk</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-700">
                <button
                  onClick={() => {
                    setShowDetail(false);
                    handleInvestigate(selectedEntity);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  🔍 Investigate
                </button>
                <button
                  onClick={() => handleExportReport(selectedEntity)}
                  className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  📊 Export Report
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EntityWorkspace;
