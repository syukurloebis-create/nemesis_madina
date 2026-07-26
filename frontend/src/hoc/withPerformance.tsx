/**
 * NEMESIS V8+ - Performance HOC
 * Track component render performance
 */

import React, { useEffect, useRef } from 'react';
import { performanceMonitor } from '../services/performance';

export function withPerformance<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName: string
): React.FC<P> {
  return function PerformanceWrapper(props: P) {
    const startTime = useRef(performance.now());

    useEffect(() => {
      const duration = performance.now() - startTime.current;
      performanceMonitor.trackComponentRender(componentName, duration);
    }, []);

    return <WrappedComponent {...props} />;
  };
}
