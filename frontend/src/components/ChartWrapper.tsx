import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface ChartWrapperProps {
  option: any;
  style?: React.CSSProperties;
  className?: string;
}

export const ChartWrapper: React.FC<ChartWrapperProps> = ({ 
  option, 
  style = {}, 
  className = "" 
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // Small delay to ensure container is rendered
    const timer = setTimeout(() => {
      if (chartRef.current) {
        chartInstance.current = echarts.init(chartRef.current);
        chartInstance.current.setOption(option);
        
        // Handle resize
        const handleResize = () => {
          chartInstance.current?.resize();
        };
        window.addEventListener('resize', handleResize);
        
        return () => {
          window.removeEventListener('resize', handleResize);
          chartInstance.current?.dispose();
        };
      }
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  // Update chart when option changes
  useEffect(() => {
    if (chartInstance.current) {
      chartInstance.current.setOption(option, true);
    }
  }, [option]);

  return (
    <div 
      ref={chartRef} 
      className={className}
      style={{ 
        width: '100%', 
        height: '400px', 
        minHeight: '400px',
        display: 'block',
        ...style 
      }} 
    />
  );
};