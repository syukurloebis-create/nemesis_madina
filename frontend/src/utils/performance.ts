export class PerformanceMonitor {
  track(name: string, value: number) {
    console.log(`📊 ${name}: ${value}ms`);
  }
}

export const performanceMonitor = new PerformanceMonitor();
