# src/components/core/GlobalTrustBar.tsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Search, Bell, User, Settings, Activity, Zap, Globe } from 'lucide-react';

interface GlobalTrustBarProps {
  trustScore: number;
}

export const GlobalTrustBar: React.FC<GlobalTrustBarProps> = ({ trustScore }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const getTrustColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-gray-900/80 backdrop-blur border-b border-cyan-500/30 sticky top-0 z-50">
      <div className="flex items-center justify-between px-6 py-3">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="relative">
            <Shield className="w-8 h-8 text-cyan-400" />
            <motion.div
              className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
              NEMESIS V8+
            </h1>
            <p className="text-xs text-gray-500">Forensic Intelligence Platform</p>
          </div>
        </div>

        {/* Global Search */}
        <div className="flex-1 max-w-md mx-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search vendor, aggregate, hash, or entity..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg py-2 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Trust Score */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-lg">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span className="text-xs text-gray-400">System Trust</span>
            <span className={`font-mono font-bold ${getTrustColor(trustScore)}`}>
              {trustScore.toFixed(2)}%
            </span>
          </div>
          
          <button className="p-2 hover:bg-gray-800 rounded-lg relative">
            <Bell className="w-5 h-5 text-gray-400" />
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full" />
          </button>
          
          <button className="p-2 hover:bg-gray-800 rounded-lg">
            <Globe className="w-5 h-5 text-gray-400" />
          </button>
          
          <button className="p-2 hover:bg-gray-800 rounded-lg">
            <User className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Animated Trust Pulse */}
      <motion.div
        className="h-0.5 bg-gradient-to-r from-green-500 via-cyan-500 to-purple-500"
        initial={{ width: `${trustScore}%` }}
        animate={{ width: `${trustScore}%` }}
        transition={{ duration: 0.5 }}
      />
    </div>
  );
};