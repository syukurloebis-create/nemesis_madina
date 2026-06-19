# src/components/anchor/RootHashPanel.tsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Anchor, Copy, Check, Shield, Clock, Fingerprint } from 'lucide-react';

interface RootHashPanelProps {
  rootHash: string;
  timestamp: string;
  verified: boolean;
}

export const RootHashPanel: React.FC<RootHashPanelProps> = ({ rootHash, timestamp, verified }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(rootHash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-gray-900/95 rounded-xl border border-cyan-500/30 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-cyan-400 flex items-center gap-2">
          <Anchor className="w-5 h-5" />
          Chain of Trust Anchor
        </h3>
        <div className={`flex items-center gap-2 px-2 py-1 rounded ${verified ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
          <Shield className={`w-4 h-4 ${verified ? 'text-green-400' : 'text-red-400'}`} />
          <span className={`text-xs ${verified ? 'text-green-400' : 'text-red-400'}`}>
            {verified ? 'VERIFIED' : 'COMPROMISED'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500">Current Root Hash</span>
            <button onClick={handleCopy} className="text-gray-500 hover:text-white">
              {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
            </button>
          </div>
          <div className="font-mono text-xs bg-black/50 p-3 rounded border border-gray-800 break-all">
            {rootHash}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-500 mb-1">Last Checkpoint</div>
            <div className="flex items-center gap-2">
              <Clock className="w-3 h-3 text-gray-500" />
              <span className="text-sm">{new Date(timestamp).toLocaleString()}</span>
            </div>
          </div>
          <div>
            <div className="text-xs text-gray-500 mb-1">Federation Proof</div>
            <div className="flex items-center gap-2">
              <Fingerprint className="w-3 h-3 text-cyan-400" />
              <span className="text-sm text-cyan-400">Active</span>
            </div>
          </div>
        </div>

        {/* Trust Pulse Monitor */}
        <div className="mt-4 pt-4 border-t border-gray-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500">Integrity Pulse</span>
            <div className="flex items-center gap-1">
              <motion.div
                className="w-2 h-2 rounded-full bg-green-500"
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
              <span className="text-xs text-green-400">Live</span>
            </div>
          </div>
          <div className="h-20 bg-black/50 rounded-lg overflow-hidden">
            <svg width="100%" height="80" className="font-mono">
              {Array.from({ length: 50 }).map((_, i) => (
                <rect
                  key={i}
                  x={i * 12}
                  y={40 - Math.sin(i * 0.3) * 20}
                  width="4"
                  height={Math.abs(Math.sin(i * 0.3) * 40)}
                  fill={verified ? '#00ff88' : '#ff4444'}
                  opacity={0.6}
                />
              ))}
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
};