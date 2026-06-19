// src/components/temporal/TimelineControls.tsx
import React from 'react';

interface TimelineControlsProps {
  isPlaying: boolean;
  onPlayPause: () => void;
  onPrevious: () => void;
  onNext: () => void;
  speed: number;
  onSpeedChange: (speed: number) => void;
  currentIndex: number;
  totalEvents: number;
}

export const TimelineControls: React.FC<TimelineControlsProps> = ({
  isPlaying,
  onPlayPause,
  onPrevious,
  onNext,
  speed,
  onSpeedChange,
  currentIndex,
  totalEvents
}) => {
  const speeds = [0.5, 1, 2, 4];

  return (
    <div className="flex items-center gap-4 flex-wrap">
      <div className="flex gap-2">
        <button
          onClick={onPrevious}
          disabled={currentIndex === 0}
          className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ⏮
        </button>
        <button
          onClick={onPlayPause}
          className="p-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-colors"
        >
          {isPlaying ? '⏸' : '▶'}
        </button>
        <button
          onClick={onNext}
          disabled={currentIndex === totalEvents - 1}
          className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          ⏭
        </button>
      </div>
      
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-500">Speed:</span>
        <div className="flex gap-1">
          {speeds.map(s => (
            <button
              key={s}
              onClick={() => onSpeedChange(s)}
              className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                speed === s
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
      
      <div className="text-sm text-gray-500">
        Event {currentIndex + 1} of {totalEvents}
      </div>
    </div>
  );
};
