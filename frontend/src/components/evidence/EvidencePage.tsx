import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

interface Evidence {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: string;
  uploaded_at: string;
}

interface Case {
  id: string;
  title: string;
}

export default function EvidencePage() {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<string>('');
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCases();
  }, []);

  useEffect(() => {
    if (selectedCase) {
      loadEvidence();
    }
  }, [selectedCase]);

  const loadCases = async () => {
    try {
      const response = await api.getCases();
      setCases(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to load cases:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadEvidence = async () => {
    try {
      const response = await api.getEvidence(selectedCase);
      setEvidence(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Failed to load evidence:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || !selectedCase) return;

    setUploading(true);
    for (const file of Array.from(files)) {
      try {
        await api.uploadEvidence(selectedCase, file);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
      }
    }
    await loadEvidence();
    setUploading(false);
    event.target.value = '';
  };

  if (loading) {
    return <div className="p-6 text-center text-gray-400">Loading...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-cyan-400 mb-6">Evidence Management</h1>

      {/* Case Selection */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <label className="block text-gray-300 mb-2">Select Case</label>
        <select
          value={selectedCase}
          onChange={(e) => setSelectedCase(e.target.value)}
          className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-white"
        >
          <option value="">-- Select Case --</option>
          {cases.map((c) => (
            <option key={c.id} value={c.id}>{c.title}</option>
          ))}
        </select>
      </div>

      {/* Upload Area */}
      {selectedCase && (
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border-2 border-dashed border-gray-600 text-center">
          <p className="text-gray-300 mb-2">Upload Evidence</p>
          <input
            type="file"
            multiple
            onChange={handleFileUpload}
            disabled={uploading}
            className="block w-full text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:bg-cyan-600 file:text-white file:cursor-pointer"
          />
          <p className="text-gray-500 text-sm mt-2">PDF, JPG, PNG, DOC, TXT | Max 50MB per file</p>
          {uploading && <p className="text-cyan-400 mt-2">Uploading...</p>}
        </div>
      )}

      {/* Evidence List */}
      <div className="bg-gray-800 rounded-lg p-4">
        <h2 className="text-lg font-semibold text-cyan-400 mb-3">Evidence List</h2>
        <p className="text-gray-400 mb-3">Total {evidence.length} evidence items</p>
        
        {evidence.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No evidence uploaded yet</div>
        ) : (
          <div className="space-y-2">
            {evidence.map((e) => (
              <div key={e.id} className="flex justify-between items-center p-3 bg-gray-700/50 rounded">
                <div>
                  <p className="text-gray-200">{e.filename}</p>
                  <p className="text-gray-500 text-sm">{e.file_type} • {(e.file_size / 1024).toFixed(1)} KB</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${e.status === 'verified' ? 'bg-green-600' : 'bg-yellow-600'}`}>
                  {e.status || 'pending'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
