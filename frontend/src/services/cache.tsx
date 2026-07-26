// Simple cache service
export class CacheService {
  private cache: Map<string, any> = new Map();

  set(key: string, value: any) {
    this.cache.set(key, value);
  }

  get(key: string) {
    return this.cache.get(key);
  }

  clear() {
    this.cache.clear();
  }
}

export const cacheService = new CacheService();
