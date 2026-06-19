import React from 'react';
import { CollusionGraphVisualization } from '../components/graph/CollusionGraphVisualization';
import { WorkspaceLayout } from '../WorkspaceLayout';

export default function CollusionGraphPage() {
  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Intelijen Graf Kolusi</h1>
          <p className="text-gray-400 mt-1">Visualisasi jaringan hubungan antar entitas dan pola kolusi</p>
        </div>
        <CollusionGraphVisualization />
      </div>
    </WorkspaceLayout>
  );
}
