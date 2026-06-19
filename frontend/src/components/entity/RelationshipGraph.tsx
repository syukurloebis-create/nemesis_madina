// src/components/entity/RelationshipGraph.tsx
import React, { useEffect, useRef } from 'react';

interface Relationship {
  id: string;
  source: string;
  target: string;
  type: string;
  strength: number;
}

interface Entity {
  id: string;
  name: string;
  type: string;
  risk_score: number;
}

interface RelationshipGraphProps {
  entities: Entity[];
  relationships: Relationship[];
  selectedEntityId?: string;
  onNodeSelect?: (entityId: string) => void;
}

export const RelationshipGraph: React.FC<RelationshipGraphProps> = ({
  entities,
  relationships,
  selectedEntityId,
  onNodeSelect,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || entities.length === 0) return;

    // Clear previous content
    containerRef.current.innerHTML = '';

    // Create canvas for manual rendering (as fallback)
    const canvas = document.createElement('canvas');
    canvas.width = containerRef.current.clientWidth;
    canvas.height = 500;
    canvas.style.width = '100%';
    canvas.style.height = '500px';
    canvas.style.backgroundColor = '#f9fafb';
    canvas.style.borderRadius = '8px';

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Simple manual graph rendering
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;

    // Calculate positions in a circle
    const radius = Math.min(width, height) * 0.35;
    const angleStep = (Math.PI * 2) / entities.length;

    const positions: { [key: string]: { x: number; y: number } } = {};

    entities.forEach((entity, idx) => {
      const angle = idx * angleStep - Math.PI / 2;
      positions[entity.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });

    // Draw edges first
    ctx.beginPath();
    relationships.forEach((rel) => {
      const sourcePos = positions[rel.source];
      const targetPos = positions[rel.target];
      if (sourcePos && targetPos) {
        ctx.beginPath();
        ctx.moveTo(sourcePos.x, sourcePos.y);
        ctx.lineTo(targetPos.x, targetPos.y);
        
        // Set line style based on type
        if (rel.type === 'collusion') {
          ctx.strokeStyle = '#ef4444';
          ctx.lineWidth = 3;
        } else {
          ctx.strokeStyle = '#f59e0b';
          ctx.lineWidth = 2;
        }
        ctx.stroke();
      }
    });

    // Draw nodes
    entities.forEach((entity) => {
      const pos = positions[entity.id];
      if (!pos) return;

      // Node size based on risk score
      const size = 30 + (entity.risk_score / 100) * 20;
      
      // Node color based on type
      let color = '#3b82f6'; // default blue
      if (entity.type === 'vendor') color = '#7c3aed';
      if (entity.type === 'institution') color = '#3b82f6';
      if (entity.type === 'package') color = '#f59e0b';
      
      // Selected highlight
      if (selectedEntityId === entity.id) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#ef4444';
      }
      
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, size, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2;
      ctx.stroke();
      
      // Reset shadow
      ctx.shadowBlur = 0;
      
      // Draw label
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 12px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      let label = entity.name;
      if (label.length > 15) label = label.substring(0, 12) + '...';
      ctx.fillText(label, pos.x, pos.y);
      
      // Draw risk badge
      const riskSize = 16;
      ctx.beginPath();
      ctx.arc(pos.x + size - 5, pos.y - size + 5, riskSize / 2, 0, Math.PI * 2);
      ctx.fillStyle = entity.risk_score >= 80 ? '#ef4444' : '#f59e0b';
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 10px sans-serif';
      ctx.fillText(`${entity.risk_score}%`, pos.x + size - 5, pos.y - size + 5);
    });

    // Add click handler
    canvas.addEventListener('click', (e) => {
      const rect = canvas.getBoundingClientRect();
      const scaleX = canvas.width / rect.width;
      const scaleY = canvas.height / rect.height;
      const mouseX = (e.clientX - rect.left) * scaleX;
      const mouseY = (e.clientY - rect.top) * scaleY;

      for (const entity of entities) {
        const pos = positions[entity.id];
        if (!pos) continue;
        
        const size = 30 + (entity.risk_score / 100) * 20;
        const dx = mouseX - pos.x;
        const dy = mouseY - pos.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance <= size) {
          onNodeSelect?.(entity.id);
          break;
        }
      }
    });

    containerRef.current.appendChild(canvas);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
    };
  }, [entities, relationships, selectedEntityId]);

  if (entities.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
        No relationship data available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="text-lg font-medium text-gray-900">Entity Relationship Graph</h3>
        <p className="text-sm text-gray-500 mt-1">
          {entities.length} entities, {relationships.length} relationships
        </p>
      </div>
      <div ref={containerRef} style={{ width: '100%', minHeight: '500px' }} />
      <div className="p-4 border-t bg-gray-50 flex flex-wrap gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-purple-600"></div>
          <span>Vendor</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-600"></div>
          <span>Institution</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-600"></div>
          <span>Package</span>
        </div>
        <div className="flex items-center gap-2 ml-4">
          <div className="w-4 h-0.5 bg-red-500"></div>
          <span>Collusion</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-orange-500"></div>
          <span>Suspicious</span>
        </div>
        <div className="flex items-center gap-2 ml-4">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span>High Risk</span>
        </div>
      </div>
    </div>
  );
};
