/**
 * Performance Monitoring
 */
interface PerformanceMetric {
  name: string;
  value: number;
  tags: Record<string, string>;
  timestamp: string;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private maxMetrics = 1000;
  private isEnabled = true;

  track(name: string, value: number, tags: Record<string, string> = {}) {
    if (!this.isEnabled) return;
    this.metrics.push({ name, value, tags, timestamp: new Date().toISOString() });
    if (this.metrics.length > this.maxMetrics) {
      this.metrics = this.metrics.slice(-this.maxMetrics);
    }
  }

  trackComponentRender(name: string, duration: number) {
    this.track(`component:${name}`, duration, { type: 'render' });
  }

  getMetrics(): PerformanceMetric[] {
    return this.metrics;
  }

  clear() {
    this.metrics = [];
  }
}

export const performanceMonitor = new PerformanceMonitor();
export default performanceMonitor;
