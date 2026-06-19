import React from 'react';
import { ZoomIn, ZoomOut, Maximize, RotateCcw, Filter } from 'lucide-react';

interface GraphControlsProps {
  onZoomIn: () => void;
  onZoomOut: () => void;
  onFit: () => void;
  onReset: () => void;
  onLayoutChange: (layout: 'cola' | 'dagre' | 'circle') => void;
  onFilterChange: (filter: string) => void;
  currentLayout: string;
}

export const GraphControls: React.FC<GraphControlsProps> = ({
  onZoomIn,
  onZoomOut,
  onFit,
  onReset,
  onLayoutChange,
  onFilterChange,
  currentLayout,
}) => {
  return (
    <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
      <div className="bg-gray-900/95 backdrop-blur rounded-lg border border-cyan-500/30 p-2 flex gap-1">
        <button onClick={onZoomIn} className="p-2 hover:bg-gray-800 rounded-lg transition text-gray-400 hover:text-white" title="Zoom In">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button onClick={onZoomOut} className="p-2 hover:bg-gray-800 rounded-lg transition text-gray-400 hover:text-white" title="Zoom Out">
          <ZoomOut className="w-4 h-4" />
        </button>
        <div className="w-px h-6 bg-gray-700 mx-1" />
        <button onClick={onFit} className="p-2 hover:bg-gray-800 rounded-lg transition text-gray-400 hover:text-white" title="Fit to Screen">
          <Maximize className="w-4 h-4" />
        </button>
        <button onClick={onReset} className="p-2 hover:bg-gray-800 rounded-lg transition text-gray-400 hover:text-white" title="Reset View">
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      <div className="bg-gray-900/95 backdrop-blur rounded-lg border border-purple-500/30 p-2">
        <select
          value={currentLayout}
          onChange={(e) => onLayoutChange(e.target.value as any)}
          className="bg-transparent text-sm text-gray-300 focus:outline-none cursor-pointer"
        >
          <option value="cola">Force Directed</option>
          <option value="dagre">Hierarchical</option>
          <option value="circle">Circular</option>
        </select>
      </div>

      <div className="bg-gray-900/95 backdrop-blur rounded-lg border border-purple-500/30 p-2">
        <div className="relative">
          <Filter className="absolute left-2 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-500" />
          <input
            type="text"
            placeholder="Filter nodes..."
            onChange={(e) => onFilterChange(e.target.value)}
            className="pl-7 pr-2 py-1 bg-transparent text-sm text-gray-300 focus:outline-none w-32"
          />
        </div>
      </div>
    </div>
  );
};
