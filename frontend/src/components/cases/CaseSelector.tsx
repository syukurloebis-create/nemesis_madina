import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCaseStore } from '../../stores/caseStore';

interface CaseSelectorProps {
    onSelect?: (caseId: string) => void;
}

const CaseSelector: React.FC<CaseSelectorProps> = ({ onSelect }) => {
    const navigate = useNavigate();
    const { cases, fetchCases, loading } = useCaseStore();
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchCases();
    }, []);

    const filteredCases = cases.filter(c => 
        c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleSelect = (caseId: string) => {
        if (onSelect) {
            onSelect(caseId);
        } else {
            navigate(`/investigation/${caseId}`);
        }
    };

    if (loading) {
        return <div className="text-gray-500">Loading cases...</div>;
    }

    return (
        <div className="bg-white rounded-lg shadow">
            <div className="p-4 border-b border-gray-200">
                <input
                    type="text"
                    placeholder="Search cases..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
            </div>
            <div className="divide-y divide-gray-200 max-h-96 overflow-auto">
                {filteredCases.length === 0 ? (
                    <div className="p-4 text-gray-500 text-center">No cases found</div>
                ) : (
                    filteredCases.map((caseItem) => (
                        <div
                            key={caseItem.id}
                            onClick={() => handleSelect(caseItem.id)}
                            className="p-4 hover:bg-gray-50 cursor-pointer"
                        >
                            <div className="font-medium text-gray-900">{caseItem.title}</div>
                            <div className="text-sm text-gray-500 mt-1">
                                ID: {caseItem.id.slice(0, 8)}... | Status: {caseItem.status} | Created: {new Date(caseItem.created_at).toLocaleDateString()}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default CaseSelector;
