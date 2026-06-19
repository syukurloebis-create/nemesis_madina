import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface Evidence {
  id: string;
  title: string;
  description: string;
  type: string;
  hash: string;
  status: 'pending' | 'verified' | 'rejected';
  uploaded_by: string;
  uploaded_at: string;
  file_url?: string;
}

interface EvidenceManagerProps {
  caseId: string;
}

const EvidenceManager: React.FC<EvidenceManagerProps> = ({ caseId }) => {
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEvidence, setNewEvidence] = useState({ title: '', description: '', type: 'document' });
  const { token } = useAuthStore();

  useEffect(() => {
    if (caseId) {
      fetchEvidence();
    }
  }, [caseId]);

  const fetchEvidence = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost/cases/${caseId}/evidence`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setEvidence(data.data || data || []);
      } else {
        // Mock data
        setEvidence([
          {
            id: 'evid-001',
            title: 'Financial Transaction Report',
            description: 'Suspicious wire transfer records',
            type: 'document',
            hash: 'a1b2c3d4e5f6...',
            status: 'verified',
            uploaded_by: 'investigator',
            uploaded_at: new Date().toISOString(),
          },
          {
            id: 'evid-002',
            title: 'Email Correspondence',
            description: 'Internal communication between vendors',
            type: 'email',
            hash: 'b2c3d4e5f6g7...',
            status: 'pending',
            uploaded_by: 'investigator',
            uploaded_at: new Date(Date.now() - 86400000).toISOString(),
          },
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch evidence:', error);
    } finally {
      setLoading(false);
    }
  };

  const addEvidence = async () => {
    if (!newEvidence.title) return;
    try {
      const response = await fetch(`http://localhost/cases/${caseId}/evidence`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newEvidence)
      });
      if (response.ok) {
        const data = await response.json();
        setEvidence([...evidence, data.data || data]);
        setShowAddForm(false);
        setNewEvidence({ title: '', description: '', type: 'document' });
      }
    } catch (error) {
      console.error('Failed to add evidence:', error);
    }
  };

  const verifyEvidence = async (evidenceId: string) => {
    try {
      const response = await fetch(`http://localhost/evidence/${evidenceId}/verify`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        setEvidence(evidence.map(e => 
          e.id === evidenceId ? { ...e, status: 'verified' } : e
        ));
      }
    } catch (error) {
      console.error('Failed to verify evidence:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'verified': return 'bg-green-500/20 text-green-400';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'rejected': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'document': return '📄';
      case 'email': return '✉️';
      case 'image': return '🖼️';
      case 'audio': return '🎵';
      case 'video': return '🎬';
      default: return '📎';
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading evidence...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white">Evidence</h3>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="px-3 py-1 text-sm bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30"
        >
          + Add Evidence
        </button>
      </div>

      {showAddForm && (
        <div className="bg-gray-700/30 rounded-lg p-4 space-y-3">
          <input
            type="text"
            placeholder="Title"
            value={newEvidence.title}
            onChange={(e) => setNewEvidence({ ...newEvidence, title: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          />
          <textarea
            placeholder="Description"
            value={newEvidence.description}
            onChange={(e) => setNewEvidence({ ...newEvidence, description: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
            rows={2}
          />
          <select
            value={newEvidence.type}
            onChange={(e) => setNewEvidence({ ...newEvidence, type: e.target.value })}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="document">Document</option>
            <option value="email">Email</option>
            <option value="image">Image</option>
            <option value="audio">Audio</option>
            <option value="video">Video</option>
          </select>
          <div className="flex gap-2">
            <button
              onClick={addEvidence}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
            >
              Save
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {evidence.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No evidence added yet</div>
        ) : (
          evidence.map((item) => (
            <div key={item.id} className="bg-gray-700/30 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-2xl">{getTypeIcon(item.type)}</span>
                <div className="flex-1">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-white">{item.title}</h4>
                      <p className="text-sm text-gray-400 mt-1">{item.description}</p>
                      <div className="flex gap-4 mt-2 text-xs text-gray-500">
                        <span>Hash: {item.hash?.slice(0, 16)}...</span>
                        <span>By: {item.uploaded_by}</span>
                        <span>{new Date(item.uploaded_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(item.status)}`}>
                        {item.status}
                      </span>
                      {item.status === 'pending' && (
                        <button
                          onClick={() => verifyEvidence(item.id)}
                          className="block mt-2 text-xs text-blue-400 hover:text-blue-300"
                        >
                          Verify
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default EvidenceManager;
