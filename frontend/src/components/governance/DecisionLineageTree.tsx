import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronDown, Shield, FileText, CheckCircle, XCircle, Clock, Users, Settings, AlertCircle } from 'lucide-react';

export interface DecisionNode {
  id: string;
  type: 'policy' | 'decision' | 'action' | 'review';
  title: string;
  description: string;
  timestamp: string;
  actor: string;
  status: 'active' | 'applied' | 'rejected' | 'pending';
  children?: DecisionNode[];
}

interface DecisionLineageTreeProps {
  nodes: DecisionNode[];
  onNodeSelect?: (node: DecisionNode) => void;
}

const NodeIcon: React.FC<{ type: string; status: string }> = ({ type, status }) => {
  const icons: Record<string, React.ReactNode> = {
    policy: <Shield className="w-4 h-4" />,
    decision: <FileText className="w-4 h-4" />,
    action: <Settings className="w-4 h-4" />,
    review: <Users className="w-4 h-4" />,
  };
  
  const statusColors: Record<string, string> = {
    active: 'text-green-500',
    applied: 'text-blue-500',
    rejected: 'text-red-500',
    pending: 'text-yellow-500',
  };

  return (
    <div className={`p-1 rounded ${status === 'active' ? 'bg-green-500/20' : status === 'rejected' ? 'bg-red-500/20' : 'bg-blue-500/20'}`}>
      <div className={statusColors[status] || 'text-gray-400'}>
        {icons[type] || <FileText className="w-4 h-4" />}
      </div>
    </div>
  );
};

const TreeNode: React.FC<{
  node: DecisionNode;
  level: number;
  onSelect: (node: DecisionNode) => void;
}> = ({ node, level, onSelect }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const hasChildren = node.children && node.children.length > 0;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded-full">Active</span>;
      case 'applied':
        return <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded-full">Applied</span>;
      case 'rejected':
        return <span className="text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full">Rejected</span>;
      default:
        return <span className="text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-400 rounded-full">Pending</span>;
    }
  };

  return (
    <div className="relative">
      {level > 0 && (
        <div className="absolute left-[-16px] top-0 bottom-0 w-px bg-gradient-to-b from-cyan-500/50 to-purple-500/50" />
      )}
      
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="relative mb-2"
      >
        <div 
          className={`flex items-start gap-3 p-3 rounded-lg border transition-all cursor-pointer hover:bg-gray-800/50 ${
            node.status === 'active' ? 'border-green-500/50 bg-green-500/5' :
            node.status === 'rejected' ? 'border-red-500/50 bg-red-500/5' :
            'border-cyan-500/30 bg-gray-800/30'
          }`}
          onClick={() => onSelect(node)}
        >
          {hasChildren && (
            <button
              onClick={(e) => { e.stopPropagation(); setIsExpanded(!isExpanded); }}
              className="mt-1 p-0.5 hover:bg-gray-700 rounded"
            >
              {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            </button>
          )}
          {!hasChildren && <div className="w-4" />}

          <NodeIcon type={node.type} status={node.status} />

          <div className="flex-1">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="font-medium text-white">{node.title}</span>
                {getStatusBadge(node.status)}
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                {new Date(node.timestamp).toLocaleString()}
              </div>
            </div>
            <p className="text-sm text-gray-400 mt-1">{node.description}</p>
            <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
              <Users className="w-3 h-3" />
              <span>{node.actor}</span>
            </div>
          </div>
        </div>
      </motion.div>

      <AnimatePresence>
        {isExpanded && hasChildren && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="ml-6 pl-4 border-l border-dashed border-gray-700"
          >
            {node.children!.map((child, idx) => (
              <TreeNode key={child.id} node={child} level={level + 1} onSelect={onSelect} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export const DecisionLineageTree: React.FC<DecisionLineageTreeProps> = ({ nodes, onNodeSelect }) => {
  if (!nodes || nodes.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>No decision lineage available</p>
        <p className="text-xs mt-1">Select an entity to view governance history</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {nodes.map((node) => (
        <TreeNode key={node.id} node={node} level={0} onSelect={(n) => onNodeSelect?.(n)} />
      ))}
    </div>
  );
};

export default DecisionLineageTree;
