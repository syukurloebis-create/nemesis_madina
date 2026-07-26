/**
 * Virtual List Component
 * Efficient rendering of large lists
 */
import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';

interface VirtualListProps<T> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  itemHeight: number;
  className?: string;
  containerHeight?: number;
  overscan?: number;
  onEndReached?: () => void;
  endReachedThreshold?: number;
  loading?: boolean;
  emptyMessage?: React.ReactNode;
}

export function VirtualList<T>({
  items,
  renderItem,
  itemHeight,
  className = '',
  containerHeight = 400,
  overscan = 3,
  onEndReached,
  endReachedThreshold = 0.8,
  loading = false,
  emptyMessage = 'No items to display'
}: VirtualListProps<T>) {
  const [scrollTop, setScrollTop] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const totalHeight = items.length * itemHeight;
  const visibleStart = Math.floor(scrollTop / itemHeight);
  const visibleCount = Math.ceil(containerHeight / itemHeight) + overscan * 2;
  const start = Math.max(0, visibleStart - overscan);
  const end = Math.min(items.length, visibleStart + visibleCount + overscan);
  const visibleItems = items.slice(start, end);
  const offsetY = start * itemHeight;

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop: newScrollTop, scrollHeight, clientHeight } = e.currentTarget;
    setScrollTop(newScrollTop);

    // Check if end reached
    if (onEndReached && scrollHeight - newScrollTop - clientHeight < clientHeight * (1 - endReachedThreshold)) {
      onEndReached();
    }
  }, [onEndReached, endReachedThreshold]);

  // Scroll to specific item
  const scrollToIndex = useCallback((index: number) => {
    if (containerRef.current) {
      containerRef.current.scrollTop = index * itemHeight;
    }
  }, [itemHeight]);

  // Scroll to top
  const scrollToTop = useCallback(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = 0;
    }
  }, []);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, []);

  if (items.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height: containerHeight }}>
        {typeof emptyMessage === 'string' ? (
          <p className="text-gray-500 dark:text-gray-400">{emptyMessage}</p>
        ) : (
          emptyMessage
        )}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`overflow-auto ${className}`}
      style={{ height: containerHeight }}
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            transform: `translateY(${offsetY}px)`,
          }}
        >
          {visibleItems.map((item, index) => (
            <div
              key={start + index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, start + index)}
            </div>
          ))}
        </div>
      </div>
      {loading && (
        <div className="flex justify-center py-4">
          <div className="w-6 h-6 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}

// Virtual List with infinite scroll
export function InfiniteVirtualList<T>({
  items,
  renderItem,
  itemHeight,
  className = '',
  containerHeight = 400,
  overscan = 3,
  onLoadMore,
  hasMore = false,
  loading = false,
  emptyMessage = 'No items to display'
}: VirtualListProps<T> & {
  onLoadMore?: () => void;
  hasMore?: boolean;
}) {
  const handleEndReached = useCallback(() => {
    if (onLoadMore && hasMore && !loading) {
      onLoadMore();
    }
  }, [onLoadMore, hasMore, loading]);

  return (
    <VirtualList
      items={items}
      renderItem={renderItem}
      itemHeight={itemHeight}
      className={className}
      containerHeight={containerHeight}
      overscan={overscan}
      onEndReached={handleEndReached}
      loading={loading}
      emptyMessage={emptyMessage}
    />
  );
}