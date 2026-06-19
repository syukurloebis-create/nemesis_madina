import React from 'react';
import { motion } from 'framer-motion';
import { Shield, CheckCircle, XCircle, Clock, TrendingUp, TrendingDown } from 'lucide-react';

interface PolicyEvent {
  id: string;
  policyName: string;
  action: 'applied' | 'removed' | 'updated';
  timestamp: string;
  impact: number;
  actor: string;
}

interface PolicyTimelineProps {
  events: PolicyEvent[];
}

export const PolicyTimeline: React.FC<PolicyTimelineProps> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No policy events</p>
      </div>
    );
  }

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'applied':
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'removed':
        return <XCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getImpactColor = (impact: number) => {
    if (impact > 0) return 'text-green-400';
    if (impact < 0) return 'text-red-400';
    return 'text-gray-400';
  };

  return (
    <div className="relative pl-8">
      <div className="absolute left-3 top-0 bottom-0 w-px bg-gradient-to-b from-cyan-500 to-purple-500" />
      
      {events.map((event, idx) => (
        <motion.div
          key={event.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: idx * 0.1 }}
          className="relative mb-6"
        >
          <div className="absolute left-[-24px] top-2 w-3 h-3 rounded-full bg-cyan-500 border-2 border-gray-900" />
          
          <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700 hover:border-cyan-500/30 transition">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                {getActionIcon(event.action)}
                <span className="font-medium text-white">{event.policyName}</span>
                <span className="text-xs text-gray-400">{event.action.toUpperCase()}</span>
              </div>
              <div className="flex items-center gap-2">
                {event.impact !== 0 && (
                  <div className={`flex items-center gap-1 text-xs ${getImpactColor(event.impact)}`}>
                    {event.impact > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    <span>{Math.abs(event.impact)}%</span>
                  </div>
                )}
                <div className="text-xs text-gray-500">
                  <Clock className="w-3 h-3 inline mr-1" />
                  {new Date(event.timestamp).toLocaleString()}
                </div>
              </div>
            </div>
            <div className="text-xs text-gray-500 mt-2">By: {event.actor}</div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default PolicyTimeline;
