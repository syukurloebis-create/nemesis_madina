import React from 'react';
import { X, Shield, User, Calendar, FileText, Link2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface DecisionDetailsProps {
  decision: any;
  onClose: () => void;
}

export const DecisionDetails: React.FC<DecisionDetailsProps> = ({ decision, onClose }) => {
  if (!decision) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 300, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 300, opacity: 0 }}
        className="fixed top-0 right-0 w-96 h-full bg-gray-900/95 backdrop-blur border-l border-cyan-500/30 shadow-xl z-50 overflow-y-auto"
      >
        <div className="p-4 border-b border-gray-800 flex items-center justify-between sticky top-0 bg-gray-900/95">
          <h3 className="text-lg font-semibold text-cyan-400 flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Decision Details
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-800 rounded-lg">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">Title</div>
            <div className="text-white font-medium">{decision.title}</div>
          </div>

          <div>
            <div className="text-xs text-gray-500 mb-1">Description</div>
            <div className="text-sm text-gray-300">{decision.description}</div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <div className="text-xs text-gray-500 mb-1">Status</div>
              <div className={`inline-flex px-2 py-1 rounded text-xs ${
                decision.status === 'active' ? 'bg-green-500/20 text-green-400' :
                decision.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {decision.status?.toUpperCase()}
              </div>
            </div>
            <div>
              <div className="text-xs text-gray-500 mb-1">Impact</div>
              <div className={`text-sm font-medium ${decision.impact > 0 ? 'text-green-400' : decision.impact < 0 ? 'text-red-400' : 'text-gray-400'}`}>
                {decision.impact > 0 ? '+' : ''}{decision.impact}%
              </div>
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-500 mb-1">Actor</div>
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-white">{decision.actor}</span>
            </div>
          </div>

          <div>
            <div className="text-xs text-gray-500 mb-1">Timestamp</div>
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-white">{new Date(decision.timestamp).toLocaleString()}</span>
            </div>
          </div>

          <div className="pt-4">
            <button className="w-full py-2 bg-cyan-600/20 text-cyan-400 rounded-lg text-sm hover:bg-cyan-600/30 transition flex items-center justify-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Request Review
            </button>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

export default DecisionDetails;
