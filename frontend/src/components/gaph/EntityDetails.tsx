// src/components/graph/EntityDetails.tsx
import React from 'react';
import { X, Shield, TrendingUp, TrendingDown, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface EntityDetailsProps {
  entity: {
    id: string;
    label: string;
    type: string;
    trustScore: number;
    riskLevel: string;
  } | null;
  onClose: () => void;
}

export const EntityDetails: React.FC<EntityDetailsProps> = ({ entity, onClose }) => {
  const navigate = useNavigate();

  if (!entity) return null;

  const handleViewDetails = () => {
    navigate(`/entity/${entity.id}`);
    onClose();
  };

  return (
    <AnimatePresence>
      {entity && (
        <motion.div
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 300, opacity: 0 }}
          className="absolute top-0 right-0 w-80 h-full bg-gray-900/95 backdrop-blur border-l border-purple-500/30 shadow-xl z-20"
        >
          <div className="p-4 border-b border-gray-800 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-purple-400">Entity Details</h3>
            <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded-lg">
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          <div className="p-4 space-y-4">
            <div>
              <div className="text-xs text-gray-500 mb-1">Entity ID</div>
              <div className="font-mono text-sm text-white break-all">{entity.id}</div>
            </div>

            <div>
              <div className="text-xs text-gray-500 mb-1">Type</div>
              <div className="text-sm text-white">{entity.type?.toUpperCase() || 'ENTITY'}</div>
            </div>

            <div>
              <div className="text-xs text-gray-500 mb-1">Trust Score</div>
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-cyan-400">{(entity.trustScore * 100).toFixed(1)}%</span>
                <Shield className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${entity.trustScore * 100}%` }} />
              </div>
            </div>

            <div>
              <div className="text-xs text-gray-500 mb-1">Risk Level</div>
              <div className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                entity.riskLevel === 'critical' ? 'bg-red-500/20 text-red-400' :
                entity.riskLevel === 'high' ? 'bg-orange-500/20 text-orange-400' :
                entity.riskLevel === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                'bg-green-500/20 text-green-400'
              }`}>
                {entity.riskLevel?.toUpperCase() || 'LOW'}
              </div>
            </div>

            <div className="pt-4">
              <button
                onClick={handleViewDetails}
                className="w-full py-2 bg-cyan-600/20 text-cyan-400 rounded-lg text-sm font-medium hover:bg-cyan-600/30 transition flex items-center justify-center gap-2"
              >
                <ExternalLink className="w-4 h-4" />
                View Full Profile
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};