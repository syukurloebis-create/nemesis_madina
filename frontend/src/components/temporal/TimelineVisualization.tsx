// src/components/temporal/TimelineVisualization.tsx
import React from 'react';

interface TimelineEvent {
  id: string;
  case_id: string;
  case_title: string;
  event_type: string;
  event_data: Record<string, any>;
  timestamp: string;
  user: string;
  hash: string;
  previous_hash: string;
}

interface TimelineVisualizationProps {
  events: TimelineEvent[];
  currentIndex: number;
  onSelectEvent: (index: number) => void;
}

const eventIcons: Record<string, string> = {
  case_created: '📋',
  evidence_added: '📎',
  risk_score_updated: '📊',
  relationship_detected: '🔗',
  status_changed: '🔄',
  anomaly_detected: '⚠️',
  case_resolved: '✅'
};

const eventColors: Record<string, string> = {
  case_created: 'border-blue-500 bg-blue-50',
  evidence_added: 'border-yellow-500 bg-yellow-50',
  risk_score_updated: 'border-orange-500 bg-orange-50',
  relationship_detected: 'border-purple-500 bg-purple-50',
  status_changed: 'border-green-500 bg-green-50',
  anomaly_detected: 'border-red-500 bg-red-50',
  case_resolved: 'border-gray-500 bg-gray-50'
};

export const TimelineVisualization: React.FC<TimelineVisualizationProps> = ({
  events,
  currentIndex,
  onSelectEvent
}) => {
  return (
    <div className="relative">
      <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-300"></div>
      
      <div className="space-y-6 relative">
        {events.map((event, idx) => (
          <div
            key={event.id}
            className={`relative flex gap-4 p-4 rounded-lg border-2 cursor-pointer transition-all ${
              eventColors[event.event_type] || 'border-gray-200 bg-gray-50'
            } ${currentIndex === idx ? 'ring-2 ring-blue-500 shadow-lg' : 'hover:shadow-md'}`}
            onClick={() => onSelectEvent(idx)}
          >
            <div className={`absolute left-6 top-6 w-4 h-4 rounded-full border-2 bg-white ${
              currentIndex === idx ? 'border-blue-500' : 'border-gray-400'
            }`}></div>
            
            <div className="text-2xl ml-4">{eventIcons[event.event_type] || '📌'}</div>
            
            <div className="flex-1">
              <div className="flex justify-between items-start flex-wrap gap-2">
                <div>
                  <h3 className="font-medium text-gray-900">
                    {event.event_type.replace(/_/g, ' ').toUpperCase()}
                  </h3>
                  <p className="text-sm text-gray-500 mt-1">Case: {event.case_title}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">{new Date(event.timestamp).toLocaleString()}</p>
                  <p className="text-xs text-gray-400 mt-1">By: {event.user}</p>
                </div>
              </div>
              
              <div className="mt-2 text-sm text-gray-600">
                {Object.entries(event.event_data).map(([key, value]) => (
                  <span key={key} className="inline-block mr-3 text-xs bg-gray-100 px-2 py-1 rounded">
                    {key}: {String(value)}
                  </span>
                ))}
              </div>
              
              <div className="mt-2 text-xs text-gray-400 font-mono">Hash: {event.hash}...</div>
            </div>
            
            {currentIndex === idx && (
              <div className="absolute -left-1 top-1/2 transform -translate-y-1/2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
