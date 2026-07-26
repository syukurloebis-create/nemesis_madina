import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';

interface EventTimelineProps {
    caseId: string;
    targetDate?: Date | null;
}

const EventTimeline: React.FC<EventTimelineProps> = ({ caseId, targetDate }) => {
    const [events, setEvents] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadEvents();
    }, [caseId]);

    const loadEvents = async () => {
        setLoading(true);
        try {
            const response = await api.getEvents(caseId, 100);
            setEvents((response.data?.events ?? response.events ?? []) || []);
        } catch (error) {
            console.error('Failed to load events:', error);
        } finally {
            setLoading(false);
        }
    };

    const getEventIcon = (eventType: string) => {
        if (eventType.includes('CASE_CREATED')) return '📋';
        if (eventType.includes('CASE_UPDATED')) return '✏️';
        if (eventType.includes('EVIDENCE_UPLOADED')) return '📎';
        if (eventType.includes('EVIDENCE_TRANSFERRED')) return '🔄';
        if (eventType.includes('CASE_CLOSED')) return '🔒';
        return '📌';
    };

    const getEventColor = (eventType: string) => {
        if (eventType.includes('CASE_CREATED')) return 'border-green-500';
        if (eventType.includes('EVIDENCE_UPLOADED')) return 'border-blue-500';
        if (eventType.includes('EVIDENCE_TRANSFERRED')) return 'border-yellow-500';
        if (eventType.includes('CASE_CLOSED')) return 'border-gray-500';
        return 'border-gray-300';
    };

    if (loading) {
        return <div className="text-gray-500">Loading timeline...</div>;
    }

    if (events.length === 0) {
        return <div className="text-gray-500">No events found for this case</div>;
    }

    return (
        <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
            <div className="space-y-4">
                {events.map((event, idx) => (
                    <div key={idx} className="relative flex gap-4">
                        <div className={`absolute left-0 w-8 h-8 rounded-full bg-white border-2 ${getEventColor(event.event_type)} flex items-center justify-center z-10`}>
                            <span className="text-sm">{getEventIcon(event.event_type)}</span>
                        </div>
                        <div className="ml-10 flex-1 bg-white rounded-lg shadow-sm p-4">
                            <div className="flex justify-between items-start">
                                <div>
                                    <span className="font-semibold text-gray-900">{event.event_type}</span>
                                    <span className="text-xs text-gray-500 ml-2">v{event.version}</span>
                                </div>
                                <span className="text-xs text-gray-500">
                                    {new Date(event.created_at || event.timestamp).toLocaleString()}
                                </span>
                            </div>
                            <div className="text-sm text-gray-600 mt-2">
                                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-32">
                                    {JSON.stringify(event.data, null, 2)}
                                </pre>
                            </div>
                            <div className="text-xs text-gray-400 mt-2 font-mono">
                                Hash: {event.event_hash?.slice(0, 16)}...
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EventTimeline;
