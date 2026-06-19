// src/components/evidence/CustodyTimeline.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface CustodyTimelineProps {
  evidenceId: string;
}

const CustodyTimeline: React.FC<CustodyTimelineProps> = ({ evidenceId }) => {
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (evidenceId) {
      loadHistory();
    }
  }, [evidenceId]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getCustodyHistory(evidenceId);
      setHistory(data.history || []);
    } catch (error) {
      console.error('Failed to load custody history:', error);
      toast.error('Failed to load custody history');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-gray-500">Loading custody timeline...</div>;
  }

  if (history.length === 0) {
    return <div className="text-gray-500">No custody history available</div>;
  }

  return (
    <div className="relative">
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
      <div className="space-y-6">
        {history.map((item, idx) => (
          <div key={item.id || idx} className="relative flex gap-4">
            <div className="absolute left-0 w-8 h-8 rounded-full bg-blue-100 border-2 border-blue-500 flex items-center justify-center z-10">
              <span className="text-sm">🔄</span>
            </div>
            <div className="ml-10 flex-1 bg-white rounded-lg shadow-sm p-4">
              <div className="flex justify-between items-start">
                <div>
                  <span className="font-semibold text-gray-900">Custody Transfer</span>
                </div>
                <span className="text-xs text-gray-500">
                  {item.transferred_at ? new Date(item.transferred_at).toLocaleString() : 'N/A'}
                </span>
              </div>
              <div className="mt-2 text-sm">
                <span className="text-red-600">From: {item.from_custodian}</span>
                {' → '}
                <span className="text-green-600">To: {item.to_custodian}</span>
              </div>
              {item.reason && (
                <div className="mt-1 text-xs text-gray-500">
                  Reason: {item.reason}
                </div>
              )}
              <div className="mt-1 text-xs text-gray-400">
                Transferred by: {item.transferred_by || 'system'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CustodyTimeline;