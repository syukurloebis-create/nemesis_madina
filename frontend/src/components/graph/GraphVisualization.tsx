import React, { useEffect, useRef, useState } from 'react';

interface GraphNode {
  id: string;
  label: string;
  type: string;
  risk_score?: number;
}

interface GraphEdge {
  from: string;
  to: string;
  type: string;
  confidence?: number;
}

const GraphVisualization: React.FC<{ caseId?: string }> = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [nodes] = useState<GraphNode[]>([
    { id: '1', label: 'PT. Maju Jaya', type: 'vendor', risk_score: 92 },
    { id: '2', label: 'CV. Karya Mandiri', type: 'vendor', risk_score: 88 },
    { id: '3', label: 'Kementerian PUPR', type: 'institution', risk_score: 65 },
    { id: '4', label: 'PT. Bangun Nusantara', type: 'vendor', risk_score: 78 },
    { id: '5', label: 'Dr. Ahmad Fauzi', type: 'individual', risk_score: 68 },
  ]);
  const [edges] = useState<GraphEdge[]>([
    { from: '1', to: '3', type: 'contract', confidence: 88 },
    { from: '2', to: '3', type: 'contract', confidence: 92 },
    { from: '1', to: '2', type: 'collusion', confidence: 75 },
    { from: '4', to: '3', type: 'contract', confidence: 85 },
    { from: '5', to: '3', type: 'oversight', confidence: 90 },
  ]);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 400 });

  useEffect(() => {
    const updateDimensions = () => {
      if (canvasRef.current) {
        const rect = canvasRef.current.getBoundingClientRect();
        setDimensions({ width: rect.width, height: rect.height });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  useEffect(() => {
    if (!canvasRef.current || nodes.length === 0) return;
    drawGraph();
  }, [nodes, edges, selectedNode, dimensions]);

  const drawGraph = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = dimensions.width;
    canvas.height = dimensions.height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (canvas.width === 0 || canvas.height === 0) return;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.3;
    const nodePositions: Record<string, { x: number; y: number }> = {};

    nodes.forEach((node, idx) => {
      const angle = (idx / nodes.length) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      nodePositions[node.id] = { x, y };
    });

    // Draw edges
    edges.forEach(edge => {
      const fromPos = nodePositions[edge.from];
      const toPos = nodePositions[edge.to];
      if (!fromPos || !toPos) return;

      ctx.beginPath();
      ctx.moveTo(fromPos.x, fromPos.y);
      ctx.lineTo(toPos.x, toPos.y);
      
      if (edge.type === 'collusion') {
        ctx.strokeStyle = '#ef4444';
        ctx.setLineDash([5, 5]);
      } else {
        ctx.strokeStyle = '#6b7280';
        ctx.setLineDash([]);
      }
      ctx.lineWidth = 2;
      ctx.stroke();

      // Arrow
      const angle = Math.atan2(toPos.y - fromPos.y, toPos.x - fromPos.x);
      const arrowX = toPos.x - 15 * Math.cos(angle);
      const arrowY = toPos.y - 15 * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(arrowX, arrowY);
      ctx.lineTo(arrowX - 8 * Math.sin(angle), arrowY + 8 * Math.cos(angle));
      ctx.lineTo(arrowX + 8 * Math.sin(angle), arrowY - 8 * Math.cos(angle));
      ctx.fillStyle = edge.type === 'collusion' ? '#ef4444' : '#6b7280';
      ctx.fill();
    });

    // Draw nodes
    nodes.forEach(node => {
      const pos = nodePositions[node.id];
      if (!pos) return;

      let color;
      if (node.risk_score && node.risk_score >= 85) color = '#ef4444';
      else if (node.risk_score && node.risk_score >= 70) color = '#f97316';
      else if (node.risk_score && node.risk_score >= 40) color = '#eab308';
      else color = '#22c55e';

      ctx.beginPath();
      ctx.arc(pos.x, pos.y, 28, 0, 2 * Math.PI);
      ctx.fillStyle = color + '20';
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.font = 'bold 12px Arial';
      ctx.fillStyle = '#e5e7eb';
      const label = node.label.length > 15 ? node.label.slice(0, 12) + '...' : node.label;
      ctx.fillText(label, pos.x - 25, pos.y - 15);
      
      ctx.font = '10px Arial';
      ctx.fillStyle = '#9ca3af';
      ctx.fillText(node.type, pos.x - 15, pos.y + 32);
      
      if (node.risk_score) {
        ctx.font = 'bold 10px Arial';
        ctx.fillStyle = color;
        ctx.fillText(`${node.risk_score}%`, pos.x - 12, pos.y + 48);
      }

      if (selectedNode?.id === node.id) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 33, 0, 2 * Math.PI);
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 3;
        ctx.stroke();
      }
    });
  };

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const canvasX = x * scaleX;
    const canvasY = y * scaleY;
    
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(canvas.width, canvas.height) * 0.3;
    
    nodes.forEach((node, idx) => {
      const angle = (idx / nodes.length) * 2 * Math.PI;
      const nodeX = centerX + radius * Math.cos(angle);
      const nodeY = centerY + radius * Math.sin(angle);
      const dist = Math.sqrt((canvasX - nodeX) ** 2 + (canvasY - nodeY) ** 2);
      if (dist < 35) {
        setSelectedNode(node);
      }
    });
  };

  return (
    <div className="space-y-4">
      <canvas
        ref={canvasRef}
        className="w-full h-96 bg-gray-800 rounded-xl border border-gray-700 cursor-pointer"
        onClick={handleCanvasClick}
        style={{ minHeight: '400px' }}
      />
      {selectedNode && (
        <div className="bg-gray-700/50 rounded-lg p-4">
          <div className="flex justify-between items-start">
            <div>
              <h4 className="font-semibold text-white">{selectedNode.label}</h4>
              <div className="grid grid-cols-2 gap-4 mt-2 text-sm">
                <div>
                  <span className="text-gray-400">Type:</span>
                  <span className="text-white ml-2">{selectedNode.type}</span>
                </div>
                <div>
                  <span className="text-gray-400">Risk Score:</span>
                  <span className={`ml-2 font-bold ${selectedNode.risk_score && selectedNode.risk_score >= 85 ? 'text-red-400' : selectedNode.risk_score && selectedNode.risk_score >= 70 ? 'text-orange-400' : 'text-green-400'}`}>
                    {selectedNode.risk_score}%
                  </span>
                </div>
              </div>
            </div>
            <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-white">✕</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphVisualization;
