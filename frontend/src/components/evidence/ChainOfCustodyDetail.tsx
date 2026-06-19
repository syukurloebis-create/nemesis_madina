// src/components/evidence/ChainOfCustodyDetail.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { 
  Shield, 
  Eye, 
  Download, 
  Upload, 
  CheckCircle, 
  AlertTriangle,
  Clock,
  User,
  Monitor,
  Calendar,
  FileText,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import toast from 'react-hot-toast';

interface CustodyEvent {
  id: string;
  evidence_id: string;
  from_custodian?: string;
  to_custodian?: string;
  action?: string;
  user_id?: string;
  user_name?: string;
  institution_id?: string;
  institution_name?: string;
  ip_address?: string;
  user_agent?: string;
  reason?: string;
  notes?: string;
  timestamp: string;
  status?: string;
}

interface ChainOfCustodyDetailProps {
  evidenceId: string;
  evidenceName?: string;
}

const getActionIcon = (action: string) => {
  const actionLower = action?.toLowerCase() || '';
  if (actionLower.includes('transfer')) return <Upload className="w-4 h-4 text-green-400" />;
  if (actionLower.includes('view')) return <Eye className="w-4 h-4 text-blue-400" />;
  if (actionLower.includes('download')) return <Download className="w-4 h-4 text-yellow-400" />;
  if (actionLower.includes('verify')) return <CheckCircle className="w-4 h-4 text-cyan-400" />;
  return <Shield className="w-4 h-4 text-gray-400" />;
};

const getActionBadge = (action: string) => {
  const actionLower = action?.toLowerCase() || '';
  if (actionLower.includes('transfer')) return 'bg-green-900 text-green-300';
  if (actionLower.includes('view')) return 'bg-blue-900 text-blue-300';
  if (actionLower.includes('download')) return 'bg-yellow-900 text-yellow-300';
  if (actionLower.includes('verify')) return 'bg-cyan-900 text-cyan-300';
  return 'bg-gray-700 text-gray-300';
};

const getActionText = (action: string) => {
  const actionLower = action?.toLowerCase() || '';
  if (actionLower.includes('transfer')) return 'Transfer Bukti';
  if (actionLower.includes('view')) return 'Bukti Dilihat';
  if (actionLower.includes('download')) return 'Bukti Diunduh';
  if (actionLower.includes('verify')) return 'Integritas Diverifikasi';
  return action || 'Aksi';
};

export const ChainOfCustodyDetail: React.FC<ChainOfCustodyDetailProps> = ({ 
  evidenceId, 
  evidenceName 
}) => {
  const [events, setEvents] = useState<CustodyEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(true);
  const [currentCustodian, setCurrentCustodian] = useState<string | null>(null);

  useEffect(() => {
    if (evidenceId) {
      fetchCustody();
    }
  }, [evidenceId]);

  const fetchCustody = async () => {
    setLoading(true);
    try {
      // Gunakan API method yang sudah ada
      const history = await api.getCustodyHistory(evidenceId);
      const current = await api.getCurrentCustodian(evidenceId);
      
      setCurrentCustodian(current.current_custodian || null);
      
      // Transform history to display format
      const formattedEvents = (history.history || []).map((item: any) => ({
        id: item.id,
        evidence_id: evidenceId,
        action: 'transfer',
        from_custodian: item.from_custodian,
        to_custodian: item.to_custodian,
        reason: item.reason,
        user_name: item.transferred_by,
        timestamp: item.transferred_at,
        status: item.status
      }));
      
      setEvents(formattedEvents);
    } catch (error) {
      console.error('Failed to fetch chain of custody:', error);
      // Jangan tampilkan error toast untuk menghindari spam
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-6 text-center">
        <Shield className="w-8 h-8 mx-auto mb-2 opacity-50 text-gray-500" />
        <p className="text-sm text-gray-500">Belum ada riwayat chain of custody</p>
        <p className="text-xs text-gray-600 mt-1">Record transfer untuk memulai rantai custody</p>
      </div>
    );
  }

  const displayEvents = expanded ? events : events.slice(0, 3);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-white">Chain of Custody</h3>
            {evidenceName && (
              <span className="text-xs text-gray-500 ml-2">{evidenceName}</span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500">{events.length} transfer</span>
            {currentCustodian && (
              <span className="text-xs text-green-400">Current: {currentCustodian}</span>
            )}
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
            >
              {expanded ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
            </button>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="p-4">
        <div className="relative pl-6">
          {/* Timeline line */}
          <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gray-700" />
          
          {displayEvents.map((event, idx) => (
            <div key={event.id} className="relative mb-6 last:mb-0">
              {/* Timeline dot */}
              <div className={`absolute -left-6 w-4 h-4 rounded-full border-2 bg-gray-800 ${getActionBadge(event.action || 'transfer')}`} />
              
              <div className="space-y-2">
                {/* Header */}
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center space-x-2">
                    {getActionIcon(event.action || 'transfer')}
                    <span className="text-sm font-medium text-white">
                      {getActionText(event.action || 'transfer')}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleString('id-ID')}
                  </span>
                </div>
                
                {/* Transfer details */}
                <div className="ml-6 space-y-1 text-xs">
                  <div className="flex items-center space-x-3 flex-wrap gap-y-1">
                    <div className="flex items-center space-x-1">
                      <User className="w-3 h-3 text-gray-500" />
                      <span className="text-gray-400">{event.user_name || 'System'}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3 text-gray-500" />
                      <span className="text-gray-400">{new Date(event.timestamp).toLocaleDateString('id-ID')}</span>
                    </div>
                  </div>
                  
                  {/* Transfer from/to */}
                  <div className="mt-2 text-gray-300">
                    <span className="text-red-400">{event.from_custodian || 'System'}</span>
                    {' → '}
                    <span className="text-green-400">{event.to_custodian || 'Unknown'}</span>
                  </div>
                  
                  {event.reason && (
                    <p className="text-gray-500 mt-1 text-xs">{event.reason}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary Stats */}
      {events.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-700 bg-gray-800/50 flex justify-between text-xs">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <Upload className="w-3 h-3 text-green-400" />
              <span className="text-gray-400">Total: {events.length}</span>
            </div>
            {currentCustodian && (
              <div className="flex items-center space-x-1">
                <Shield className="w-3 h-3 text-cyan-400" />
                <span className="text-gray-400">Current: {currentCustodian}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChainOfCustodyDetail;