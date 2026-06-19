# src/components/business/StateMachineView.tsx
import React from 'react';
import { motion } from 'framer-motion';
import { GitBranch, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface StateNode {
  id: string;
  name: string;
  type: 'start' | 'process' | 'end' | 'error';
  isActive?: boolean;
  isViolation?: boolean;
}

interface StateTransition {
  from: string;
  to: string;
  isValid: boolean;
  count: number;
}

interface StateMachineViewProps {
  states: StateNode[];
  transitions: StateTransition[];
  currentState: string;
}

export const StateMachineView: React.FC<StateMachineViewProps> = ({ states, transitions, currentState }) => {
  const getNodeColor = (node: StateNode) => {
    if (node.isViolation) return 'border-red-500 bg-red-500/10';
    if (node.isActive) return 'border-green-500 bg-green-500/10 shadow-lg shadow-green-500/20';
    if (node.type === 'start') return 'border-blue-500 bg-blue-500/10';
    if (node.type === 'end') return 'border-purple-500 bg-purple-500/10';
    return 'border-gray-700 bg-gray-800/50';
  };

  const getTransitionColor = (transition: StateTransition) => {
    return transition.isValid ? 'stroke-green-500' : 'stroke-red-500';
  };

  return (
    <div className="bg-gray-900/95 rounded-xl border border-green-500/30 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-green-400 flex items-center gap-2">
          <GitBranch className="w-5 h-5" />
          State Machine Intelligence
        </h3>
        <div className="text-right">
          <div className="text-xs text-gray-500">Current State</div>
          <div className="text-sm font-mono text-green-400">{currentState}</div>
        </div>
      </div>

      <div className="relative min-h-[300px] flex items-center justify-center">
        <svg width="100%" height="300" className="absolute inset-0">
          {transitions.map((transition, idx) => {
            const fromState = states.find(s => s.id === transition.from);
            const toState = states.find(s => s.id === transition.to);
            if (!fromState || !toState) return null;
            
            return (
              <motion.line
                key={idx}
                x1={fromState.id === 'start' ? 50 : 200}
                y1={80 + states.findIndex(s => s.id === transition.from) * 50}
                x2={toState.id === 'end' ? 550 : 400}
                y2={80 + states.findIndex(s => s.id === transition.to) * 50}
                stroke={transition.isValid ? '#22c55e' : '#ef4444'}
                strokeWidth={2 + transition.count}
                strokeDasharray={transition.isValid ? 'none' : '5,5'}
                opacity={0.6}
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ duration: 1, delay: idx * 0.1 }}
              />
            );
          })}
        </svg>

        <div className="relative z-10 grid grid-cols-3 gap-8 w-full">
          {states.map((state, idx) => (
            <motion.div
              key={state.id}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: idx * 0.1 }}
              className={`p-3 rounded-lg border ${getNodeColor(state)} text-center min-w-[120px]`}
            >
              <div className="flex items-center justify-center gap-2 mb-2">
                {state.type === 'start' && <CheckCircle className="w-4 h-4 text-blue-400" />}
                {state.type === 'end' && <CheckCircle className="w-4 h-4 text-purple-400" />}
                {state.isViolation && <AlertCircle className="w-4 h-4 text-red-400" />}
                <span className="text-sm font-medium">{state.name}</span>
              </div>
              {state.isActive && (
                <div className="text-xs text-green-400">◉ Current</div>
              )}
              {state.isViolation && (
                <div className="text-xs text-red-400">⚠ Violation</div>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-800">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <span>Valid Transition</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-red-500 rounded-full" />
              <span>Invalid Transition</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
              <span>Current State</span>
            </div>
          </div>
          <div className="text-gray-500">
            Integrity: <span className="text-green-400">92%</span>
          </div>
        </div>
      </div>
    </div>
  );
};