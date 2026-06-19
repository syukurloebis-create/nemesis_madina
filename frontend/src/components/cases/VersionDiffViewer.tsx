// src/components/cases/VersionDiffViewer.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface VersionDiffViewerProps {
    caseId: string;
}

const VersionDiffViewer: React.FC<VersionDiffViewerProps> = ({ caseId }) => {
    const [versionA, setVersionA] = useState<number>(1);
    const [versionB, setVersionB] = useState<number>(2);
    const [differences, setDifferences] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [maxVersion, setMaxVersion] = useState<number>(100);

    useEffect(() => {
        const getMaxVersion = async () => {
            try {
                // Gunakan getEventTimeline, bukan getCaseTimeline
                const timeline = await api.getEventTimeline(caseId, 1, 0);
                if (timeline.events && timeline.events.length > 0) {
                    const maxVer = timeline.events[0].version;
                    setMaxVersion(maxVer);
                    setVersionB(Math.min(2, maxVer));
                }
            } catch (error) {
                console.error('Error getting max version:', error);
            }
        };
        getMaxVersion();
    }, [caseId]);

    const handleCompare = async () => {
        if (versionA === versionB) {
            toast.error('Please select different versions to compare');
            return;
        }
        
        setLoading(true);
        try {
            const result = await api.compareVersions(caseId, versionA, versionB);
            setDifferences(result.differences || []);
            toast.success(`Compared version ${versionA} vs ${versionB}`);
        } catch (error: any) {
            console.error('Error comparing versions:', error);
            toast.error(error.message || 'Failed to compare versions');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex gap-4 items-end flex-wrap">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Version A</label>
                    <input
                        type="number"
                        min={1}
                        max={maxVersion}
                        value={versionA}
                        onChange={(e) => setVersionA(parseInt(e.target.value) || 1)}
                        className="px-3 py-2 border border-gray-300 rounded-md w-24"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Version B</label>
                    <input
                        type="number"
                        min={1}
                        max={maxVersion}
                        value={versionB}
                        onChange={(e) => setVersionB(parseInt(e.target.value) || 1)}
                        className="px-3 py-2 border border-gray-300 rounded-md w-24"
                    />
                </div>
                <button
                    onClick={handleCompare}
                    disabled={loading || versionA === versionB}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                    {loading ? 'Comparing...' : 'Compare'}
                </button>
            </div>

            {differences.length > 0 && (
                <div className="mt-4">
                    <h4 className="font-medium text-gray-900 mb-2">Differences:</h4>
                    <div className="space-y-2">
                        {differences.map((diff, idx) => (
                            <div key={idx} className="bg-gray-50 p-3 rounded-md">
                                <div className="font-mono text-sm font-semibold">{diff.field}:</div>
                                <div className="grid grid-cols-2 gap-4 mt-1 text-sm">
                                    <div>
                                        <span className="text-red-600">Version {versionA}:</span>
                                        <pre className="text-xs mt-1 bg-white p-2 rounded overflow-auto">
                                            {JSON.stringify(diff.from, null, 2)}
                                        </pre>
                                    </div>
                                    <div>
                                        <span className="text-green-600">Version {versionB}:</span>
                                        <pre className="text-xs mt-1 bg-white p-2 rounded overflow-auto">
                                            {JSON.stringify(diff.to, null, 2)}
                                        </pre>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {differences.length === 0 && !loading && versionA !== versionB && (
                <div className="text-gray-500 text-sm">No differences found between version {versionA} and {versionB}</div>
            )}
            
            {versionA === versionB && !loading && (
                <div className="text-yellow-600 text-sm">Please select different versions to compare</div>
            )}
        </div>
    );
};

export default VersionDiffViewer;