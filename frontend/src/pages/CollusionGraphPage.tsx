// src/pages/CollusionGraphPage.tsx
import React from 'react';
import { CollusionGraphVisualization } from '../components/graph/CollusionGraphVisualization';
import { FROZEN_CASE_ID } from '../config/constants';

export default function CollusionGraphPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Intelijen Graf Kolusi</h1>
        <p className="text-gray-400 mt-1">Visualisasi jaringan hubungan antar entitas dan pola kolusi</p>
      </div>
      <CollusionGraphVisualization caseId={FROZEN_CASE_ID} />
    </div>
  );
}