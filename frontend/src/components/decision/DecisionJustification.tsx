// DecisionJustification.tsx - Show justification with evidence
import React, { useState } from 'react';
import { 
  AlertTriangle, 
  ChevronDown, 
  ChevronUp,
  FileText,
  Shield,
  CheckCircle,
  ExternalLink
} from 'lucide-react';
import { DecisionJustification as DecisionJustificationType } from '../../types/decision';

interface DecisionJustificationProps {
  justification: DecisionJustificationType[];
  className?: string;
}

const JustificationItem: React.FC<{ 
  item: DecisionJustificationType; 
  index: number;
}> = ({ item, index }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-dark-bg rounded-lg border border-dark-border overflow-hidden">
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-dark-card/50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3 flex-1">
          <span className="text-xs text-gray-500 font-mono">#{index + 1}</span>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-medium text-white capitalize">
                {item.factor.replace(/_/g, ' ')}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-0.5 line-clamp-1">{item.description}</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500">Contribution</span>
            <span className="text-sm font-bold text-yellow-400">{item.contribution}%</span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-3 pb-3 space-y-2 border-t border-dark-border pt-2">
          <p className="text-sm text-gray-300">{item.description}</p>
          
          {item.evidence && item.evidence.length > 0 && (
            <div className="bg-dark-card rounded-lg p-2">
              <p className="text-xs text-gray-500 flex items-center gap-1.5 mb-1.5">
                <FileText className="w-3 h-3" />
                Evidence Supporting This Decision
              </p>
              <ul className="space-y-1">
                {item.evidence.map((ev, i) => (
                  <li key={i} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                      <span className="text-gray-400">{ev.title}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                        ev.trust_score >= 80 ? 'bg-green-500/20 text-green-400' :
                        ev.trust_score >= 60 ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {ev.trust_score}%
                      </span>
                      {ev.link && (
                        <button className="text-blue-400 hover:text-blue-300">
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const DecisionJustification: React.FC<DecisionJustificationProps> = ({ 
  justification, 
  className = '' 
}) => {
  if (!justification || justification.length === 0) {
    return (
      <div className={`bg-gray-500/10 border border-gray-500/30 rounded-lg p-4 text-center ${className}`}>
        <p className="text-sm text-gray-400">Tidak ada justifikasi untuk keputusan ini</p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wider">
          Decision Justification
        </h4>
        <span className="text-xs text-gray-500">{justification.length} factors</span>
      </div>
      {justification.map((item, index) => (
        <JustificationItem key={index} item={item} index={index} />
      ))}
    </div>
  );
};

export default DecisionJustification;
