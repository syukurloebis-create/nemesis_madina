// src/components/evidence/EvidenceManager.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { useEvidenceStore } from '../../stores/evidenceStore';
import toast from 'react-hot-toast';

interface EvidenceManagerProps {
    caseId: string;
    onEvidenceSelect: (evidenceId: string) => void;
}

const EvidenceManager: React.FC<EvidenceManagerProps> = ({ caseId, onEvidenceSelect }) => {
    const { evidence, setEvidence, isLoading, setLoading } = useEvidenceStore();
    const [uploading, setUploading] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    useEffect(() => {
        if (caseId) {
            loadEvidence();
        }
    }, [caseId]);

    const loadEvidence = async () => {
        setLoading(true);
        try {
            const data = await api.listEvidence(caseId);
            console.log('Evidence data:', data);
            // Handle different response formats
            const evidenceList = data.evidence || data || [];
            setEvidence(evidenceList);
            if (evidenceList.length === 0) {
                console.log('No evidence found for case:', caseId);
            }
        } catch (error) {
            console.error('Failed to load evidence:', error);
            toast.error('Failed to load evidence');
        } finally {
            setLoading(false);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        
        setUploading(true);
        try {
            await api.uploadEvidence(caseId, selectedFile);
            toast.success('Evidence uploaded successfully');
            setSelectedFile(null);
            // Reset file input
            const fileInput = document.getElementById('evidence-file-input') as HTMLInputElement;
            if (fileInput) fileInput.value = '';
            await loadEvidence();
        } catch (error: any) {
            toast.error(error.message || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const handleVerify = async (evidenceId: string) => {
        try {
            const result = await api.verifyEvidence(evidenceId);
            if (result.status === 'VERIFIED') {
                toast.success('Evidence integrity verified');
            } else {
                toast.warning('Evidence integrity check failed');
            }
        } catch (error) {
            toast.error('Verification failed');
        }
    };

    if (isLoading) {
        return (
            <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold">Evidence Files</h3>
                </div>
                <div className="p-8 text-center text-gray-500">Loading evidence...</div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Evidence Files</h3>
            </div>
            
            {/* Upload Section */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <div className="flex gap-2">
                    <input
                        id="evidence-file-input"
                        type="file"
                        onChange={handleFileSelect}
                        className="flex-1 text-sm"
                    />
                    <button
                        onClick={handleUpload}
                        disabled={!selectedFile || uploading}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                </div>
            </div>
            
            {/* Evidence List */}
            <div className="divide-y divide-gray-200 max-h-96 overflow-auto">
                {evidence.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No evidence uploaded yet
                    </div>
                ) : (
                    evidence.map((item: any) => (
                        <div 
                            key={item.id} 
                            className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => onEvidenceSelect(item.id)}
                        >
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <div className="font-medium text-gray-900">{item.filename}</div>
                                    <div className="text-sm text-gray-500 mt-1">
                                        Size: {item.file_size?.toLocaleString()} bytes | 
                                        Uploaded: {new Date(item.uploaded_at).toLocaleString()}
                                    </div>
                                    <div className="text-xs text-gray-400 font-mono mt-1">
                                        SHA256: {item.sha256_hash?.slice(0, 16)}...
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleVerify(item.id);
                                    }}
                                    className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 ml-4"
                                >
                                    Verify
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default EvidenceManager;