import React, { useState } from 'react';
import { api } from '../../services/api';
import toast from 'react-hot-toast';

interface TimeTravelControllerProps {
    caseId: string;
    onClose: () => void;
    onTimeSelect: (date: Date) => void;
}

const TimeTravelController: React.FC<TimeTravelControllerProps> = ({ caseId, onClose, onTimeSelect }) => {
    const [selectedDate, setSelectedDate] = useState<Date>(new Date());
    const [reconstructedState, setReconstructedState] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const handleReconstruct = async () => {
        setLoading(true);
        try {
            const response = await api.getStateAtTime(caseId, selectedDate.toISOString());
            setReconstructedState(response);
            toast.success(`State reconstructed at ${selectedDate.toLocaleString()}`);
        } catch (error: any) {
            toast.error(error.message || 'Reconstruction failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Time Travel</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">×</button>
                </div>
                
                <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Select Date & Time
                    </label>
                    <input
                        type="datetime-local"
                        value={selectedDate.toISOString().slice(0, 16)}
                        onChange={(e) => setSelectedDate(new Date(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                
                <button
                    onClick={handleReconstruct}
                    disabled={loading}
                    className="w-full px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                    {loading ? 'Reconstructing...' : 'Travel to Selected Time'}
                </button>
                
                {reconstructedState && (
                    <div className="mt-4 p-3 bg-gray-50 rounded-md">
                        <h3 className="font-medium mb-2">State at {selectedDate.toLocaleString()}</h3>
                        <pre className="text-xs overflow-auto max-h-48">
                            {JSON.stringify(reconstructedState, null, 2)}
                        </pre>
                        <button
                            onClick={() => onTimeSelect(selectedDate)}
                            className="mt-2 w-full px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                        >
                            Apply This State
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TimeTravelController;
