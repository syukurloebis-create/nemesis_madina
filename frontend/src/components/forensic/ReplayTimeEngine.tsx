// src/components/forensic/ReplayTimeEngine.tsx
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, Play, Pause, SkipBack, SkipForward, RotateCcw } from 'lucide-react';
import { Slider } from '@/components/ui/slider';

interface ReplayTimeEngineProps {
  startDate: Date;
  endDate: Date;
  onTimeChange: (timestamp: Date) => void;
  eventsAtTime: Array<{ timestamp: Date; eventType: string; integrity: boolean }>;
}

export const ReplayTimeEngine: React.FC<ReplayTimeEngineProps> = ({
  startDate,
  endDate,
  onTimeChange,
  eventsAtTime,
}) => {
  const [currentTime, setCurrentTime] = useState<Date>(endDate);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);

  const totalDuration = endDate.getTime() - startDate.getTime();
  const progress = ((currentTime.getTime() - startDate.getTime()) / totalDuration) * 100;

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying) {
      interval = setInterval(() => {
        const newTime = new Date(currentTime.getTime() + 1000 * speed);
        if (newTime <= endDate) {
          setCurrentTime(newTime);
          onTimeChange(newTime);
        } else {
          setIsPlaying(false);
        }
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentTime, speed, endDate, onTimeChange]);

  const handleTimeChange = (value: number[]) => {
    const newTime = new Date(startDate.getTime() + (value[0] / 100) * totalDuration);
    setCurrentTime(newTime);
    onTimeChange(newTime);
    setIsPlaying(false);
  };

  return (
    <div className="bg-gray-900/95 rounded-xl border border-amber-500/30 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-amber-400 flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Temporal Replay Engine
        </h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSpeed(0.5)}
            className={`px-2 py-1 text-xs rounded ${speed === 0.5 ? 'bg-amber-500 text-black' : 'bg-gray-800 text-gray-400'}`}
          >
            0.5x
          </button>
          <button
            onClick={() => setSpeed(1)}
            className={`px-2 py-1 text-xs rounded ${speed === 1 ? 'bg-amber-500 text-black' : 'bg-gray-800 text-gray-400'}`}
          >
            1x
          </button>
          <button
            onClick={() => setSpeed(2)}
            className={`px-2 py-1 text-xs rounded ${speed === 2 ? 'bg-amber-500 text-black' : 'bg-gray-800 text-gray-400'}`}
          >
            2x
          </button>
        </div>
      </div>

      {/* Timeline Slider */}
      <div className="mb-6">
        <Slider
          value={[progress]}
          onValueChange={handleTimeChange}
          max={100}
          step={0.1}
          className="cursor-pointer"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-2">
          <span>{startDate.toLocaleString()}</span>
          <span>{currentTime.toLocaleString()}</span>
          <span>{endDate.toLocaleString()}</span>
        </div>
      </div>

      {/* Playback Controls */}
      <div className="flex items-center justify-center gap-4 mb-6">
        <button onClick={() => handleTimeChange([0])} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700">
          <SkipBack className="w-5 h-5" />
        </button>
        <button onClick={() => setIsPlaying(!isPlaying)} className="p-3 bg-amber-500 rounded-full hover:bg-amber-400">
          {isPlaying ? <Pause className="w-6 h-6 text-black" /> : <Play className="w-6 h-6 text-black" />}
        </button>
        <button onClick={() => handleTimeChange([100])} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700">
          <SkipForward className="w-5 h-5" />
        </button>
        <button onClick={() => handleTimeChange([progress])} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700">
          <RotateCcw className="w-5 h-5" />
        </button>
      </div>

      {/* Event Timeline */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        <p className="text-xs text-gray-500 mb-2">Events at this timestamp:</p>
        {eventsAtTime.length === 0 ? (
          <div className="text-center text-gray-600 text-sm py-4">No events at this timestamp</div>
        ) : (
          eventsAtTime.map((event, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
            >
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${event.integrity ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm">{event.eventType}</span>
              </div>
              <span className="text-xs text-gray-500">{event.timestamp.toLocaleTimeString()}</span>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};