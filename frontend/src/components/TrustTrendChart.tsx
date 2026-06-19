import React from 'react';

interface TrustTrendChartProps {
  data: Array<{ date: string; trust: number }>;
  color?: string;
  height?: number;
}

export const TrustTrendChart: React.FC<TrustTrendChartProps> = ({ 
  data, 
  color = "#00ffff",
  height = 250 
}) => {
  // Validate and sanitize data
  const validData = React.useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return [];
    }
    
    // Filter valid data points
    return data.filter(item => {
      const trust = item.trust;
      return typeof trust === 'number' && !isNaN(trust) && isFinite(trust);
    });
  }, [data]);

  if (validData.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center text-gray-500">
          <p className="text-sm">No trust trend data available</p>
        </div>
      </div>
    );
  }

  // Calculate min/max for scaling
  const values = validData.map(d => d.trust);
  const maxValue = Math.max(...values, 0.8);
  const minValue = Math.min(...values, 0.4);
  const range = maxValue - minValue;
  const safeRange = range > 0.01 ? range : 0.5;
  
  const width = 700;
  const paddingLeft = 50;
  const paddingRight = 20;
  const chartWidth = width - paddingLeft - paddingRight;
  
  // Generate points safely
  const points = validData.map((item, i) => {
    const x = paddingLeft + (i / (validData.length - 1)) * chartWidth;
    const trust = item.trust;
    // Clamp trust value between 0 and 1
    const clampedTrust = Math.min(Math.max(trust, 0), 1);
    const y = height - 20 - ((clampedTrust - minValue) / safeRange) * (height - 40);
    // Ensure y is a valid number
    const safeY = isNaN(y) || !isFinite(y) ? height - 20 : y;
    return { x, y: safeY, trust: clampedTrust };
  });

  // Generate line points string
  const linePoints = points.map(p => `${p.x},${p.y}`).join(' ');
  
  // Generate area points string (add bottom corners)
  const areaPoints = `${paddingLeft},${height - 20} ${linePoints} ${width - paddingRight},${height - 20}`;

  // Grid line values
  const gridValues = [0, 0.25, 0.5, 0.75, 1];

  return (
    <div className="relative w-full overflow-x-auto">
      <svg 
        width="100%" 
        height={height} 
        viewBox={`0 0 ${width} ${height}`} 
        preserveAspectRatio="xMidYMid meet"
        style={{ minHeight: height }}
      >
        <defs>
          <linearGradient id="trustGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        
        {/* Grid lines and Y-axis labels */}
        {gridValues.map((ratio) => {
          const y = height - 20 - (ratio * (height - 40));
          const value = minValue + (ratio * safeRange);
          const labelValue = Math.min(Math.max(value, 0), 1);
          return (
            <g key={ratio}>
              <line
                x1={paddingLeft}
                y1={y}
                x2={width - paddingRight}
                y2={y}
                stroke="#1a1a2e"
                strokeDasharray="3,3"
              />
              <text
                x={paddingLeft - 8}
                y={y + 4}
                textAnchor="end"
                fill="#666"
                fontSize="10"
              >
                {(labelValue * 100).toFixed(0)}%
              </text>
            </g>
          );
        })}
        
        {/* Area fill */}
        <polygon
          points={areaPoints}
          fill="url(#trustGradient)"
        />
        
        {/* Line */}
        <polyline
          points={linePoints}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        
        {/* Data points */}
        {points.map((point, idx) => (
          <circle
            key={idx}
            cx={point.x}
            cy={point.y}
            r="3"
            fill={color}
            stroke="#fff"
            strokeWidth="1"
          />
        ))}
        
        {/* X-axis labels */}
        {validData.map((item, idx) => {
          const x = paddingLeft + (idx / (validData.length - 1)) * chartWidth;
          return (
            <text
              key={idx}
              x={x}
              y={height - 5}
              textAnchor="middle"
              fill="#666"
              fontSize="10"
            >
              {item.date || `Day ${idx + 1}`}
            </text>
          );
        })}
      </svg>
    </div>
  );
};

export default TrustTrendChart;