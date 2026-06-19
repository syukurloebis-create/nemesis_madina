# src/components/core/TrustCoreIndex.tsx
import React, { useEffect, useState } from 'react';
import { motion, useSpring } from 'framer-motion';
import { Shield, Activity, Link2, Globe, AlertTriangle, Cpu } from 'lucide-react';

interface TrustMetrics {
  systemTrustScore: number;
  chainIntegrity: number;
  federationHealth: number;
  anomalyDensity: number;
  businessViolations: number;
  tamperProbability: number;
}

export const TrustCoreIndex: React.FC = () => {
  const [metrics, setMetrics] = useState<TrustMetrics>({
    systemTrustScore: 97.82,
    chainIntegrity: 99.5,
    federationHealth: 98.2,
    anomalyDensity: 2.3,
    businessViolations: 1.2,
    tamperProbability: 0.8,
  });

  const scoreSpring = useSpring({
    value: metrics.systemTrustScore,
    stiffness: 50,
    damping: 10,
  });

  const orbits = [
    { name: 'Integrity', value: metrics.chainIntegrity, icon: Link2, color: '#00ffff' },
    { name: 'Federation', value: metrics.federationHealth, icon: Globe, color: '#00ff88' },
    { name: 'Event', value: 100 - metrics.anomalyDensity, icon: Activity, color: '#ffaa00' },
    { name: 'Replay', value: 98.5, icon: Cpu, color: '#aa00ff' },
    { name: 'Threat', value: 100 - metrics.tamperProbability, icon: AlertTriangle, color: '#ff4444' },
  ];

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-gray-900 to-black rounded-2xl overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-900/20 via-transparent to-transparent" />
      
      {/* Central Trust Core */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
        <motion.div
          className="relative w-48 h-48 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 shadow-2xl shadow-cyan-500/50"
          animate={{ scale: [1, 1.05, 1] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          <div className="absolute inset-2 rounded-full bg-gray-900 flex flex-col items-center justify-center">
            <Shield className="w-8 h-8 text-cyan-400 mb-2" />
            <motion.div className="text-4xl font-bold text-white">
              {metrics.systemTrustScore.toFixed(1)}%
            </motion.div>
            <div className="text-xs text-cyan-400 mt-1">TRUST CORE</div>
          </div>
        </motion.div>
      </div>

      {/* Orbiting Metrics */}
      {orbits.map((orbit, idx) => {
        const angle = (idx / orbits.length) * Math.PI * 2;
        const radius = 180;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        const Icon = orbit.icon;
        
        return (
          <motion.div
            key={orbit.name}
            className="absolute top-1/2 left-1/2 w-24 h-24 rounded-full bg-gray-800/50 backdrop-blur border border-cyan-500/30 flex flex-col items-center justify-center"
            style={{ x, y }}
            animate={{ rotate: 360 }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            <Icon className="w-5 h-5" style={{ color: orbit.color }} />
            <div className="text-xs text-white mt-1">{orbit.name}</div>
            <div className="text-sm font-bold" style={{ color: orbit.color }}>
              {orbit.value.toFixed(1)}%
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};