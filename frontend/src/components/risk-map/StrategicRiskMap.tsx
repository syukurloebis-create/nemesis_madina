// StrategicRiskMap.tsx - Risk Heatmap
import React from 'react';
import { MapPin, AlertTriangle, CheckCircle } from 'lucide-react';

interface StrategicRiskMapProps {
  data: any;
}

export const StrategicRiskMap: React.FC<StrategicRiskMapProps> = ({ data }) => {
  // Mock data - akan diganti dengan API data
  const regions = [
    { name: 'Kecamatan A', risk: 'HIGH', score: 92 },
    { name: 'Kecamatan B', risk: 'MEDIUM', score: 65 },
    { name: 'Kecamatan C', risk: 'LOW', score: 28 },
    { name: 'Kecamatan D', risk: 'HIGH', score: 85 },
    { name: 'Kecamatan E', risk: 'MEDIUM', score: 55 },
  ];

  const getRiskColor = (risk: string) => {
    switch(risk) {
      case 'HIGH': return 'text-red-500 bg-red-500/20 border-red-500/30';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/20 border-yellow-500/30';
      case 'LOW': return 'text-green-500 bg-green-500/20 border-green-500/30';
      default: return 'text-gray-500 bg-gray-500/20 border-gray-500/30';
    }
  };

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">📍 STRATEGIC RISK MAP</h3>
        <span className="text-xs text-gray-500">Based on AI analysis</span>
      </div>
      
      <div className="space-y-3">
        {regions.map((region, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <MapPin className={`w-4 h-4 ${getRiskColor(region.risk).split(' ')[0]}`} />
            <div className="flex-1">
              <div className="flex justify-between text-sm">
                <span className="text-gray-300">{region.name}</span>
                <span className={`font-medium ${getRiskColor(region.risk).split(' ')[0]}`}>
                  {region.risk}
                </span>
              </div>
              <div className="w-full h-1.5 bg-gray-800 rounded-full mt-1 overflow-hidden">
                <div 
                  className={`h-full rounded-full ${region.risk === 'HIGH' ? 'bg-red-500' : region.risk === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${region.score}%` }}
                />
              </div>
            </div>
            <span className="text-xs text-gray-500">{region.score}</span>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-4 pt-3 border-t border-dark-border">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-red-500" />
          <span className="text-xs text-gray-500">HIGH</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-yellow-500" />
          <span className="text-xs text-gray-500">MEDIUM</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-green-500" />
          <span className="text-xs text-gray-500">LOW</span>
        </div>
      </div>
    </div>
  );
};

export default StrategicRiskMap;
