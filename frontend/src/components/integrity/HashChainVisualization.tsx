// src/components/integrity/HashChainVisualization.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface HashChainVisualizationProps {
    caseId: string;
    evidenceId?: string;
}

const HashChainVisualization: React.FC<HashChainVisualizationProps> = ({ caseId, evidenceId }) => {
    const [chain, setChain] = useState<any[]>([]);
    const [integrityStatus, setIntegrityStatus] = useState<string>('CHECKING');
    const [chainIntact, setChainIntact] = useState<boolean>(false);
    const [loading, setLoading] = useState(true);
    const [totalEvents, setTotalEvents] = useState(0);
    const [totalHashes, setTotalHashes] = useState(0);

    useEffect(() => {
        fetchChain();
    }, [caseId]);

    const fetchChain = async () => {
        setLoading(true);
        try {
            // Use verify endpoint to get integrity status
            const result = await api.verifyCaseIntegrity(caseId);
            setIntegrityStatus(result.status);
            setChainIntact(result.chain_intact);
            setTotalEvents(result.events_verified);
            setTotalHashes(result.events_verified);
            
            // Also fetch chain data menggunakan getEventChain
            const chainData = await api.getEventChain(caseId);
            setChain(chainData.chain || []);
            
        } catch (error) {
            console.error('Failed to fetch chain:', error);
            setIntegrityStatus('ERROR');
            toast.error('Failed to fetch chain integrity');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = () => {
        switch (integrityStatus) {
            case 'PASS': return 'text-green-600';
            case 'FAIL': return 'text-red-600';
            case 'ERROR': return 'text-red-600';
            default: return 'text-yellow-600';
        }
    };

    const getStatusBadge = () => {
        switch (integrityStatus) {
            case 'PASS': return 'bg-green-100 text-green-800';
            case 'FAIL': return 'bg-red-100 text-red-800';
            case 'ERROR': return 'bg-red-100 text-red-800';
            default: return 'bg-yellow-100 text-yellow-800';
        }
    };

    if (loading) {
        return <div className="text-gray-500">Loading hash chain...</div>;
    }

    return (
        <div className="space-y-4">
            {/* Status Summary */}
            <div className="bg-gray-50 p-4 rounded-lg">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <div className="text-sm text-gray-500">Integrity Status</div>
                        <div className={`text-xl font-bold ${getStatusColor()}`}>
                            {integrityStatus}
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-500">Chain Intact</div>
                        <div className={`text-xl font-bold ${chainIntact ? 'text-green-600' : 'text-red-600'}`}>
                            {chainIntact ? 'Yes' : 'No'}
                        </div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-500">Total Events</div>
                        <div className="text-xl font-bold text-gray-900">{totalEvents}</div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-500">Total Hashes</div>
                        <div className="text-xl font-bold text-gray-900">{totalHashes}</div>
                    </div>
                </div>
                <div className="mt-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge()}`}>
                        {integrityStatus === 'PASS' ? '✓ Chain Verified' : integrityStatus === 'FAIL' ? '✗ Chain Broken' : '⚠ Check Failed'}
                    </span>
                </div>
            </div>

            {/* Hash Chain Visualization */}
            <div className="border rounded-lg overflow-hidden">
                <div className="bg-gray-100 px-4 py-2 font-medium">Visualisasi Hash Chain</div>
                <div className="divide-y divide-gray-200 max-h-96 overflow-auto">
                    {chain.length === 0 ? (
                        <div className="p-4 text-gray-500 text-center">No chain data available</div>
                    ) : (
                        chain.slice(0, 50).map((item, idx) => (
                            <div key={idx} className="p-3 hover:bg-gray-50">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <span className="font-mono text-sm font-medium">{item.event_type}</span>
                                        <span className="text-xs text-gray-500 ml-2">v{item.version}</span>
                                    </div>
                                    <div className="text-xs text-gray-400">
                                        {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}
                                    </div>
                                </div>
                                <div className="mt-1">
                                    <code className="text-xs text-gray-500 break-all">
                                        Hash: {item.event_hash?.slice(0, 16)}...
                                    </code>
                                </div>
                                {item.previous_hash && (
                                    <div className="mt-1">
                                        <code className="text-xs text-gray-400 break-all">
                                            ← Prev: {item.previous_hash.slice(0, 16)}...
                                        </code>
                                    </div>
                                )}
                            </div>
                        ))
                    )}
                </div>
                {chain.length > 50 && (
                    <div className="bg-gray-50 px-4 py-2 text-sm text-gray-500 text-center">
                        Showing first 50 of {chain.length} events
                    </div>
                )}
            </div>
        </div>
    );
};

export default HashChainVisualization;