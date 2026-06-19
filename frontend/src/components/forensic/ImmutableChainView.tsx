# src/components/forensic/ImmutableChainView.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link2, Hash, Shield, AlertTriangle, CheckCircle, Eye } from 'lucide-react';

interface Event {
  sequence: number;
  eventType: string;
  eventHash: string;
  previousHash: string | null;
  recomputedHash: string;
  verified: boolean;
  trustDelta: number;
  payload: any;
  metadata: any;
}

interface ImmutableChainViewProps {
  events: Event[];
  onEventClick: (event: Event) => void;
}

export const ImmutableChainView: React.FC<ImmutableChainViewProps> = ({ events, onEventClick }) => {
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

  const getStatusIcon = (verified: boolean) => {
    return verified ? <CheckCircle className="w-4 h-4 text-green-500" /> : <AlertTriangle className="w-4 h-4 text-red-500" />;
  };

  const getTrustColor = (trustDelta: number) => {
    if (trustDelta > 0) return 'text-green-500';
    if (trustDelta < 0) return 'text-red-500';
    return 'text-gray-500';
  };

  return (
    <div className="bg-gray-900/95 rounded-xl border border-cyan-500/30 overflow-hidden">
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-cyan-400 flex items-center gap-2">
          <Link2 className="w-5 h-5" />
          Immutable Event Chain
        </h3>
        <p className="text-xs text-gray-500 mt-1">Cryptographic lineage with tamper-evident verification</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-800/50">
            <tr className="text-left text-gray-400 border-b border-gray-700">
              <th className="p-3">Seq</th>
              <th className="p-3">Event Type</th>
              <th className="p-3">Event Hash</th>
              <th className="p-3">Previous Hash</th>
              <th className="p-3">Status</th>
              <th className="p-3">Trust Δ</th>
              <th className="p-3"></th>
            </tr>
          </thead>
          <tbody>
            <AnimatePresence>
              {events.map((event, idx) => (
                <motion.tr
                  key={event.sequence}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-b border-gray-800 hover:bg-gray-800/30 cursor-pointer"
                  onClick={() => onEventClick(event)}
                >
                  <td className="p-3 font-mono text-cyan-400">#{event.sequence}</td>
                  <td className="p-3 font-medium text-white">{event.eventType}</td>
                  <td className="p-3 font-mono text-xs text-gray-400">{event.eventHash.slice(0, 16)}...</td>
                  <td className="p-3 font-mono text-xs text-gray-500">{event.previousHash?.slice(0, 16) || '—'}...</td>
                  <td className="p-3">{getStatusIcon(event.verified)}</td>
                  <td className={`p-3 font-mono ${getTrustColor(event.trustDelta)}`}>
                    {event.trustDelta > 0 ? '+' : ''}{event.trustDelta}
                  </td>
                  <td className="p-3">
                    <button className="p-1 hover:bg-gray-700 rounded">
                      <Eye className="w-4 h-4 text-gray-400" />
                    </button>
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Forensic Event Card Modal */}
      <AnimatePresence>
        {selectedEvent && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="fixed inset-0 flex items-center justify-center z-50 bg-black/80 backdrop-blur"
            onClick={() => setSelectedEvent(null)}
          >
            <div className="bg-gray-900 rounded-xl border border-cyan-500 p-6 max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
              <div className="flex justify-between items-center mb-4">
                <h4 className="text-xl font-bold text-cyan-400">Forensic Event Card</h4>
                <button onClick={() => setSelectedEvent(null)} className="text-gray-400 hover:text-white">✕</button>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><label className="text-gray-500">Event ID</label><div className="font-mono text-sm">{selectedEvent.eventHash.slice(0, 32)}...</div></div>
                  <div><label className="text-gray-500">Previous Hash</label><div className="font-mono text-sm">{selectedEvent.previousHash?.slice(0, 32) || '—'}</div></div>
                  <div><label className="text-gray-500">Recomputed Hash</label><div className="font-mono text-sm">{selectedEvent.recomputedHash.slice(0, 32)}...</div></div>
                  <div><label className="text-gray-500">Integrity Proof</label><div className={selectedEvent.verified ? 'text-green-500' : 'text-red-500'}>{selectedEvent.verified ? 'VERIFIED' : 'COMPROMISED'}</div></div>
                </div>
                <div>
                  <label className="text-gray-500">Original Payload</label>
                  <pre className="mt-1 p-3 bg-gray-800 rounded text-xs overflow-auto">{JSON.stringify(selectedEvent.payload, null, 2)}</pre>
                </div>
                <div>
                  <label className="text-gray-500">Metadata</label>
                  <pre className="mt-1 p-3 bg-gray-800 rounded text-xs overflow-auto">{JSON.stringify(selectedEvent.metadata, null, 2)}</pre>
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <Shield className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm">Tamper Probability: <span className="font-mono text-cyan-400">{selectedEvent.verified ? '0.00%' : '100.00%'}</span></span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};