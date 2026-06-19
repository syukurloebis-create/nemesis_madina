import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface Entity {
  id: string;
  name: string;
  type: string;
  risk_score: number;
  risk_level: string;
  related_cases: number;
  last_updated: string;
  metadata: Record<string, any>;
}

interface EntityDetailProps {
  entityId: string;
  onClose: () => void;
}

const EntityDetail: React.FC<EntityDetailProps> = ({ entityId, onClose }) => {
  const [entity, setEntity] = useState<Entity | null>(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuthStore();

  useEffect(() => {
    fetchEntityDetail();
  }, [entityId]);

  const fetchEntityDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost/entities/${entityId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setEntity(data);
      } else {
        // Mock data
        setEntity({
          id: entityId,
          name: 'PT. Maju Jaya',
          type: 'vendor',
          risk_score: 92,
          risk_level: 'critical',
          related_cases: 5,
          last_updated: new Date().toISOString(),
          metadata: {
            registration: '1234567890',
            established: '2010',
            employees: 250,
            revenue: 'Rp 500M'
          }
        });
      }
    } catch (error) {
      console.error('Failed to fetch entity:', error);
    } finally {
      setLoading(false);
    }
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

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading entity details...</div>;
  }

  if (!entity) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="sticky top-0 bg-gray-800 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
          <h2 className="text-xl font-bold text-white">Entity Details</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white">✕</button>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-2xl font-bold text-white">{entity.name}</h3>
              <p className="text-gray-400">Type: {entity.type}</p>
            </div>
            <div className={`px-4 py-2 rounded-full ${getRiskBgColor(entity.risk_score)}`}>
              <span className={`text-xl font-bold ${getRiskColor(entity.risk_score)}`}>
                {entity.risk_score}% Risk
              </span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-700/30 rounded-lg p-3">
              <p className="text-gray-400 text-sm">Related Cases</p>
              <p className="text-2xl font-bold text-white">{entity.related_cases}</p>
            </div>
            <div className="bg-gray-700/30 rounded-lg p-3">
              <p className="text-gray-400 text-sm">Last Updated</p>
              <p className="text-sm text-white">{new Date(entity.last_updated).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Metadata */}
          <div>
            <h4 className="font-semibold text-white mb-3">Entity Information</h4>
            <div className="space-y-2">
              {Object.entries(entity.metadata).map(([key, value]) => (
                <div key={key} className="flex justify-between py-2 border-b border-gray-700">
                  <span className="text-gray-400 capitalize">{key}:</span>
                  <span className="text-white">{String(value)}</span>
                </div>
              ))}
            </div>
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
                <span className="text-yellow-400">Low Risk</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
              Investigate
            </button>
            <button className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600">
              Export Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EntityDetail;
