import asyncio
import time
import random
import hashlib
import json
from dataclasses import dataclass, field, asdict, is_dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Set, List, Tuple
import logging
from collections import deque

from .dashboard_snapshot_builder import DashboardSnapshotBuilder
from .dashboard_snapshot import DashboardSnapshot

logger = logging.getLogger(__name__)


def _serialize_snapshot_to_dict(snapshot: Any) -> Dict[str, Any]:
    """
    Helper to serialize any snapshot object to dict deterministically.
    Supports: to_dict(), model_dump(), dict(), dataclass, vars()
    """
    if hasattr(snapshot, 'to_dict'):
        return snapshot.to_dict()
    elif hasattr(snapshot, 'model_dump'):
        return snapshot.model_dump()
    elif hasattr(snapshot, 'dict'):
        return snapshot.dict()
    elif is_dataclass(snapshot):
        return asdict(snapshot)
    else:
        return vars(snapshot)


@dataclass
class SnapshotCacheEntry:
    """Cache entry with metadata and stale-while-revalidate support"""
    snapshot: DashboardSnapshot
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(seconds=60))
    version: int = 1
    snapshot_hash: str = ""
    hit_count: int = 0
    last_error: Optional[str] = None
    error_count: int = 0
    build_duration_ms: float = 0
    last_build_success: Optional[datetime] = None
    last_build_failure: Optional[datetime] = None
    
    def __post_init__(self):
        """Generate hash from snapshot content if not provided"""
        if not self.snapshot_hash:
            self.snapshot_hash = self._compute_snapshot_hash()
    
    def _compute_snapshot_hash(self) -> str:
        """Compute deterministic hash from snapshot"""
        try:
            data = _serialize_snapshot_to_dict(self.snapshot)
            content = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        except Exception as e:
            logger.warning(f"Failed to compute snapshot hash: {e}")
            return f"v{self.version}"
    
    def is_same_snapshot(self, other: 'SnapshotCacheEntry') -> bool:
        """Check if two entries represent the same snapshot content"""
        return self.snapshot_hash == other.snapshot_hash
    
    def get_changed_keys(self, other: 'SnapshotCacheEntry') -> List[str]:
        """Get list of changed keys between two snapshots"""
        if not self.snapshot_hash == other.snapshot_hash:
            # If hashes differ, compare structures
            try:
                data1 = _serialize_snapshot_to_dict(self.snapshot)
                data2 = _serialize_snapshot_to_dict(other.snapshot)
                
                changed = []
                all_keys = set(data1.keys()) | set(data2.keys())
                for key in all_keys:
                    if data1.get(key) != data2.get(key):
                        changed.append(key)
                return changed
            except Exception:
                return ["*"]  # Unable to determine specific changes
        return []  # No changes
    
    @property
    def age_seconds(self) -> float:
        """Age of the cache entry in seconds"""
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    @property
    def is_stale(self) -> bool:
        """Check if entry is stale (expired)"""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def ttl_remaining(self) -> float:
        """Remaining TTL in seconds"""
        remaining = (self.expires_at - datetime.now(timezone.utc)).total_seconds()
        return max(0, remaining)


class DashboardSnapshotCacheManager:
    def __init__(
        self,
        builder: DashboardSnapshotBuilder,
        ttl_seconds: int = 60,
        warm_refresh_interval: int = 55,
        build_timeout_seconds: int = 20,
        max_error_count: int = 3,
        max_stale_age_seconds: int = 600,  # 10 minutes
        cleanup_interval_seconds: int = 300,  # 5 minutes
        max_parallel_refreshes: int = 4,
        refresh_jitter_seconds: int = 5,
        shutdown_timeout_seconds: int = 30
    ):
        self.builder = builder
        self.ttl_seconds = ttl_seconds
        self.warm_refresh_interval = warm_refresh_interval
        self.build_timeout_seconds = build_timeout_seconds
        self.max_error_count = max_error_count
        self.max_stale_age_seconds = max_stale_age_seconds
        self.cleanup_interval_seconds = cleanup_interval_seconds
        self.max_parallel_refreshes = max_parallel_refreshes
        self.refresh_jitter_seconds = refresh_jitter_seconds
        self.shutdown_timeout_seconds = shutdown_timeout_seconds
        
        # Cache storage - protected by global lock for mutation
        self._cache: Dict[str, SnapshotCacheEntry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        
        # Single-flight refresh tracking
        self._refresh_tasks: Dict[str, asyncio.Task] = {}
        self._refresh_lock = asyncio.Lock()
        
        # Statistics - using atomic counters with lock
        self._stats_lock = asyncio.Lock()
        self._stats = {
            "hit": 0,
            "miss": 0,
            "refresh": 0,
            "last_refresh": None,
            "last_error": None,
            "error_count": 0,
            "build_count": 0,
            "failed_build_count": 0,
            "last_successful_build": None,
            "last_failed_build": None
        }
        
        # Build metrics
        self._metrics_lock = asyncio.Lock()
        self._build_durations: deque = deque(maxlen=100)
        self._last_build_duration_ms: float = 0
        
        # Background tasks management - using strong references
        self._background_tasks: Set[asyncio.Task] = set()
        self._shutdown_event = asyncio.Event()
        
        # Semaphore for parallel refreshes
        self._refresh_semaphore = asyncio.Semaphore(max_parallel_refreshes)
        
        # Health status
        self._is_warm = False
        self._warm_start_time = None
        self._is_closed = False
        
        # Background tasks references
        self._refresh_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info(
            f"CacheManager initialized with TTL={ttl_seconds}s, "
            f"warm_interval={warm_refresh_interval}s, "
            f"timeout={build_timeout_seconds}s, "
            f"max_stale_age={max_stale_age_seconds}s, "
            f"max_parallel_refreshes={max_parallel_refreshes}"
        )
    
    async def _ensure_lock(self, key: str) -> asyncio.Lock:
        """Get or create lock for a key atomically"""
        async with self._global_lock:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            return self._locks[key]
    
    async def _inc_stats(self, stat_name: str, value: int = 1):
        """Thread-safe statistics increment"""
        async with self._stats_lock:
            self._stats[stat_name] = self._stats.get(stat_name, 0) + value
    
    async def _set_stats(self, stat_name: str, value):
        """Thread-safe statistics set"""
        async with self._stats_lock:
            self._stats[stat_name] = value
    
    async def _get_stats_snapshot(self) -> Dict[str, Any]:
        """Get thread-safe stats snapshot"""
        async with self._stats_lock:
            return dict(self._stats)
    
    async def _add_build_duration(self, duration_ms: float, success: bool = True):
        """Thread-safe build duration addition"""
        async with self._metrics_lock:
            if success:
                self._build_durations.append(duration_ms)
                self._last_build_duration_ms = duration_ms
    
    async def _get_build_durations_snapshot(self) -> Tuple[deque, float]:
        """Get thread-safe build durations snapshot"""
        async with self._metrics_lock:
            return (
                deque(self._build_durations),  # Copy
                self._last_build_duration_ms
            )
    
    def _remove_background_task(self, task: asyncio.Task):
        """Remove task from background tasks set"""
        self._background_tasks.discard(task)
    
    def _task_done_callback(self, task: asyncio.Task):
        """Callback for background task completion"""
        # Always try to get result to clean up exceptions
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # Only log if not closed to avoid noise during shutdown
            if not self._is_closed:
                logger.exception(f"Background task failed: {e}")
    
    async def _get_cache_snapshot(self) -> Dict[str, SnapshotCacheEntry]:
        """Get thread-safe cache snapshot"""
        async with self._global_lock:
            return dict(self._cache)
    
    async def _get_full_snapshot(self) -> Dict[str, Any]:
        """Get complete snapshot of all state atomically"""
        async with self._global_lock:
            cache_copy = dict(self._cache)
        
        stats = await self._get_stats_snapshot()
        durations, last_duration = await self._get_build_durations_snapshot()
        
        return {
            "cache": cache_copy,
            "stats": stats,
            "durations": durations,
            "last_duration": last_duration
        }
    
    async def compare_snapshots(self, key1: str = "default", key2: str = "default") -> Dict[str, Any]:
        """Compare two snapshot entries and return differences"""
        async with self._global_lock:
            entry1 = self._cache.get(key1)
            entry2 = self._cache.get(key2)
        
        if not entry1 or not entry2:
            return {"error": "One or both entries not found"}
        
        return {
            "same_hash": entry1.snapshot_hash == entry2.snapshot_hash,
            "version_diff": entry2.version - entry1.version,
            "age_diff_seconds": entry2.age_seconds - entry1.age_seconds,
            "changed_keys": entry1.get_changed_keys(entry2) if not entry1.is_same_snapshot(entry2) else [],
            "entry1": {
                "version": entry1.version,
                "hash": entry1.snapshot_hash[:8],
                "created_at": entry1.created_at.isoformat()
            },
            "entry2": {
                "version": entry2.version,
                "hash": entry2.snapshot_hash[:8],
                "created_at": entry2.created_at.isoformat()
            }
        }
    
    async def get_snapshot(self, key: str = "default") -> DashboardSnapshot:
        """
        Get snapshot with stale-while-revalidate pattern.
        Returns stale data if available while refreshing in background.
        Optimized for minimal lock contention.
        """
        if self._is_closed:
            raise RuntimeError("Cache manager is closed")
        
        # Fast path: read cache without global lock for O(1) performance
        entry = self._cache.get(key)
        
        if entry:
            # Update hit count with per-key lock
            lock = await self._ensure_lock(key)
            async with lock:
                entry.hit_count += 1
                await self._inc_stats("hit")
            
            # Check if stale
            if entry.is_stale:
                logger.debug(f"Cache STALE for key={key}, triggering background refresh")
                await self._trigger_background_refresh(key)
            
            logger.debug(
                f"Cache HIT for key={key}, "
                f"age={entry.age_seconds:.1f}s, "
                f"ttl_remaining={entry.ttl_remaining:.1f}s, "
                f"hits={entry.hit_count}"
            )
            return entry.snapshot
        
        # Cache miss - need to build with lock
        await self._inc_stats("miss")
        logger.info(f"Cache MISS for key={key}, building...")
        return await self._build_or_replace_snapshot(key, is_manual=False)
    
    async def _build_or_replace_snapshot(
        self, 
        key: str, 
        is_manual: bool = False,
        count_as_refresh: bool = False
    ) -> DashboardSnapshot:
        """
        Core method to build and replace snapshot in cache.
        Consolidates ALL build logic from _build_snapshot and refresh_now.
        
        Args:
            key: Cache key
            is_manual: If True, forces rebuild even if cache is valid
            count_as_refresh: If True, increments refresh counter
        """
        # Ensure lock exists for this key
        lock = await self._ensure_lock(key)
        
        # Acquire lock for this specific key
        async with lock:
            # Get current entry if exists
            async with self._global_lock:
                entry = self._cache.get(key)
            
            # If not manual and entry exists and not stale, return it
            if not is_manual and entry and not entry.is_stale:
                entry.hit_count += 1
                await self._inc_stats("hit")
                logger.debug(f"Cache HIT after lock for key={key}")
                return entry.snapshot
            
            # Build new snapshot
            try:
                logger.info(f"{'Manual' if is_manual else 'Building'} snapshot for key={key}")
                start_time = time.perf_counter()
                
                snapshot = await asyncio.wait_for(
                    self.builder.build_snapshot(),
                    timeout=self.build_timeout_seconds
                )
                
                build_duration_ms = (time.perf_counter() - start_time) * 1000
                await self._add_build_duration(build_duration_ms, success=True)
                await self._inc_stats("build_count")
                await self._set_stats("last_successful_build", datetime.now(timezone.utc))
                
                # Create new entry
                new_entry = SnapshotCacheEntry(
                    snapshot=snapshot,
                    expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds),
                    version=entry.version + 1 if entry else 1,
                    last_error=None,
                    error_count=0,
                    build_duration_ms=build_duration_ms,
                    last_build_success=datetime.now(timezone.utc)
                )
                
                # Only increment version if content actually changed
                if entry and entry.snapshot_hash and entry.snapshot_hash == new_entry.snapshot_hash:
                    new_entry.version = entry.version  # Keep same version
                    # Preserve created_at for identical snapshots
                    new_entry.created_at = entry.created_at
                elif entry:
                    new_entry.version = entry.version + 1
                
                # Store in cache
                async with self._global_lock:
                    self._cache[key] = new_entry
                
                # Update stats
                if count_as_refresh:
                    await self._inc_stats("refresh")
                
                await self._set_stats("last_refresh", datetime.now(timezone.utc))
                await self._set_stats("error_count", 0)
                self._is_warm = True
                self._warm_start_time = datetime.now(timezone.utc)
                
                logger.info(
                    f"{'Manual refresh' if is_manual else 'Snapshot'} cached for key={key}, "
                    f"TTL={self.ttl_seconds}s, "
                    f"duration={build_duration_ms:.1f}ms, "
                    f"version={new_entry.version}, "
                    f"hash={new_entry.snapshot_hash[:8]}"
                )
                return snapshot
                
            except asyncio.TimeoutError:
                error_msg = f"Build timeout after {self.build_timeout_seconds}s"
                logger.error(f"Timeout {'manual refresh' if is_manual else 'building'} snapshot for key={key}")
                await self._handle_build_error(key, error_msg)
                raise
                
            except Exception as e:
                error_msg = str(e)
                logger.exception(f"Error {'manual refresh' if is_manual else 'building'} snapshot for key={key}: {e}")
                await self._handle_build_error(key, error_msg)
                raise
    
    async def _handle_build_error(self, key: str, error_msg: str):
        """Handle build errors with exponential backoff"""
        await self._set_stats("last_error", datetime.now(timezone.utc))
        await self._inc_stats("error_count")
        await self._inc_stats("failed_build_count")
        await self._set_stats("last_failed_build", datetime.now(timezone.utc))
        
        # Use per-key lock for updating entry
        lock = await self._ensure_lock(key)
        async with lock:
            # Get entry and update it
            async with self._global_lock:
                entry = self._cache.get(key)
            
            if entry:
                entry.last_error = error_msg
                entry.error_count += 1
                entry.last_build_failure = datetime.now(timezone.utc)
                
                # Exponential backoff for retry
                backoff_seconds = min(5 * (2 ** (entry.error_count - 1)), 60)
                entry.expires_at = datetime.now(timezone.utc) + timedelta(seconds=backoff_seconds)
                
                logger.warning(
                    f"Cache error for key={key}, kept stale data. "
                    f"Error count: {entry.error_count}/{self.max_error_count}, "
                    f"backoff: {backoff_seconds}s"
                )
    
    async def _trigger_background_refresh(self, key: str):
        """Trigger background refresh with single-flight protection"""
        if self._is_closed:
            logger.debug(f"Cache closed, skipping refresh for key={key}")
            return
        
        async with self._refresh_lock:
            # Check if refresh is already in progress
            if key in self._refresh_tasks:
                task = self._refresh_tasks[key]
                if not task.done():
                    logger.debug(f"Refresh already in progress for key={key}")
                    return
            
            # Create new refresh task
            task = asyncio.create_task(self._refresh_cache(key))
            self._refresh_tasks[key] = task
            self._background_tasks.add(task)
            task.add_done_callback(lambda t: self._remove_background_task(t))
            task.add_done_callback(self._task_done_callback)
    
    async def _refresh_cache(self, key: str):
        """Background refresh of cache with error handling and semaphore"""
        # Check if closed at start
        if self._is_closed:
            return
        
        async with self._refresh_semaphore:  # Limit parallel refreshes
            try:
                logger.info(f"Refreshing cache for key={key}")
                
                # Get lock for this key
                lock = await self._ensure_lock(key)
                async with lock:
                    # Check if closed during wait
                    if self._is_closed:
                        return
                    
                    # Double-check if refresh still needed
                    async with self._global_lock:
                        entry = self._cache.get(key)
                    
                    if entry and not entry.is_stale:
                        logger.debug(f"Cache already fresh for key={key}, skipping refresh")
                        return
                    
                    # Build and replace snapshot (counts as refresh)
                    return await self._build_or_replace_snapshot(
                        key, 
                        is_manual=False, 
                        count_as_refresh=True
                    )
                        
            except asyncio.CancelledError:
                logger.debug(f"Refresh task cancelled for key={key}")
                raise
            except Exception as e:
                logger.exception(f"Unexpected error in refresh for key={key}: {e}")
            finally:
                # Clean up refresh task from tracking dict
                async with self._refresh_lock:
                    self._refresh_tasks.pop(key, None)
    
    async def refresh_now(self, key: str = "default") -> DashboardSnapshot:
        """
        Force immediate refresh atomically without invalidating first.
        Replaces cache entry in-place under lock.
        
        Uses the same _build_or_replace_snapshot helper as all other builds.
        """
        logger.info(f"Manual refresh requested for key={key}")
        
        # Use semaphore to respect parallel refresh limits
        async with self._refresh_semaphore:
            # Build and replace snapshot (manual, counts as refresh)
            return await self._build_or_replace_snapshot(
                key,
                is_manual=True,
                count_as_refresh=True
            )
    
    async def invalidate(self, key: str = "default"):
        """Force invalidate cache - locks are never deleted to avoid race conditions"""
        async with self._global_lock:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"Cache invalidated for key={key}")
            # Locks are never deleted to avoid race conditions
            # This is safe because locks are very small objects
    
    async def invalidate_all(self):
        """Invalidate all cache entries"""
        # First cancel any ongoing refresh tasks
        async with self._refresh_lock:
            tasks_to_cancel = list(self._refresh_tasks.values())
            for task in tasks_to_cancel:
                if not task.done():
                    task.cancel()
            self._refresh_tasks.clear()
        
        # Wait for cancelled tasks to complete
        if tasks_to_cancel:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks_to_cancel, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some refresh tasks did not cancel in time")
        
        # Then clear cache
        async with self._global_lock:
            self._cache.clear()
            logger.info("All cache invalidated and refresh tasks cancelled")
    
    async def cleanup_expired(self):
        """Clean up expired entries older than max_stale_age"""
        # Check if closed
        if self._is_closed:
            return
        
        async with self._global_lock:
            now = datetime.now(timezone.utc)
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.is_stale and entry.age_seconds > self.max_stale_age_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self._cache[key]
                logger.info(f"Cleaned up expired entry: {key} (age > {self.max_stale_age_seconds}s)")
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired entries")
    
    async def preload(self, keys: List[str] = None):
        """Preload cache at startup"""
        if keys is None:
            keys = ["default"]
            
        logger.info(f"Preloading cache for keys: {keys}")
        for key in keys:
            try:
                await self._build_or_replace_snapshot(key, is_manual=False, count_as_refresh=False)
            except Exception as e:
                logger.error(f"Failed to preload key={key}: {e}")
        
        async with self._global_lock:
            self._is_warm = len(self._cache) > 0
        
        if self._is_warm:
            self._warm_start_time = datetime.now(timezone.utc)
            logger.info(f"Cache preloaded successfully with {len(self._cache)} entries")
    
    async def start_warm_refresh(self, keys: List[str] = None):
        """Start background warm refresh task with jitter and parallel refreshes"""
        if keys is None:
            keys = ["default"]
            
        if self._refresh_task and not self._refresh_task.done():
            logger.warning("Warm refresh task already running")
            return
        
        async def warm_refresh_loop():
            # Check if closed at start
            if self._is_closed:
                return
            
            while not self._shutdown_event.is_set() and not self._is_closed:
                try:
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, self.refresh_jitter_seconds)
                    await asyncio.sleep(self.warm_refresh_interval + jitter)
                    
                    if self._shutdown_event.is_set() or self._is_closed:
                        break
                    
                    # Refresh all keys in parallel with semaphore limit
                    refresh_tasks = []
                    async with self._global_lock:
                        for key in keys:
                            if key in self._cache:
                                # Check if refresh is already in progress
                                async with self._refresh_lock:
                                    if key not in self._refresh_tasks or self._refresh_tasks[key].done():
                                        refresh_tasks.append(self._refresh_cache(key))
                    
                    if refresh_tasks:
                        await asyncio.gather(*refresh_tasks, return_exceptions=True)
                        
                except asyncio.CancelledError:
                    logger.info("Warm refresh task cancelled")
                    break
                except Exception as e:
                    logger.error(f"Warm refresh loop error: {e}")
            
            logger.info("Warm refresh loop exited")
        
        self._shutdown_event.clear()
        self._refresh_task = asyncio.create_task(warm_refresh_loop())
        self._background_tasks.add(self._refresh_task)
        self._refresh_task.add_done_callback(lambda t: self._remove_background_task(t))
        self._refresh_task.add_done_callback(self._task_done_callback)
        logger.info(f"Warm refresh task started with interval={self.warm_refresh_interval}s ±{self.refresh_jitter_seconds}s")
    
    async def start_cleanup_task(self):
        """Start background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            logger.warning("Cleanup task already running")
            return
        
        async def cleanup_loop():
            # Check if closed at start
            if self._is_closed:
                return
            
            while not self._shutdown_event.is_set() and not self._is_closed:
                try:
                    await asyncio.sleep(self.cleanup_interval_seconds)
                    
                    if self._shutdown_event.is_set() or self._is_closed:
                        break
                    
                    await self.cleanup_expired()
                    
                except asyncio.CancelledError:
                    logger.info("Cleanup task cancelled")
                    break
                except Exception as e:
                    logger.error(f"Cleanup loop error: {e}")
            
            logger.info("Cleanup loop exited")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
        self._background_tasks.add(self._cleanup_task)
        self._cleanup_task.add_done_callback(lambda t: self._remove_background_task(t))
        self._cleanup_task.add_done_callback(self._task_done_callback)
        logger.info(f"Cleanup task started with interval={self.cleanup_interval_seconds}s")
    
    async def stop_warm_refresh(self):
        """Stop background warm refresh task"""
        self._shutdown_event.set()
        if self._refresh_task:
            self._refresh_task.cancel()
            try:
                await asyncio.wait_for(self._refresh_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            self._refresh_task = None
            logger.info("Warm refresh task stopped")
    
    async def stop_cleanup_task(self):
        """Stop background cleanup task"""
        self._shutdown_event.set()
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await asyncio.wait_for(self._cleanup_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
            self._cleanup_task = None
            logger.info("Cleanup task stopped")
    
    async def close(self):
        """Gracefully close the cache manager"""
        if self._is_closed:
            return
            
        self._is_closed = True
        self._shutdown_event.set()
        logger.info("Closing cache manager...")
        
        # Stop background tasks
        await self.stop_warm_refresh()
        await self.stop_cleanup_task()
        
        # Cancel any ongoing refresh tasks
        async with self._refresh_lock:
            for key, task in list(self._refresh_tasks.items()):
                if not task.done():
                    task.cancel()
                    logger.debug(f"Cancelled refresh task for key={key}")
            self._refresh_tasks.clear()
        
        # Wait for all background tasks to complete with timeout
        if self._background_tasks:
            # Take a snapshot of current tasks
            tasks = tuple(self._background_tasks)
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.shutdown_timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.warning(f"Some background tasks did not complete within {self.shutdown_timeout_seconds}s")
            
            # Clear the set after gathering
            self._background_tasks.clear()
        
        # Clear cache but keep locks
        async with self._global_lock:
            self._cache.clear()
            # Locks are kept to avoid race conditions
        
        logger.info("Cache manager closed")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics with atomic snapshot"""
        # Get complete snapshot atomically
        snapshot = await self._get_full_snapshot()
        
        stats = snapshot["stats"]
        cache_snapshot = snapshot["cache"]
        durations = snapshot["durations"]
        last_duration = snapshot["last_duration"]
        
        # Build cache entries from snapshot
        cache_entries = {}
        for key, entry in cache_snapshot.items():
            cache_entries[key] = {
                "created_at": entry.created_at.isoformat(),
                "expires_at": entry.expires_at.isoformat(),
                "age_seconds": round(entry.age_seconds, 1),
                "ttl_remaining": round(entry.ttl_remaining, 1),
                "version": entry.version,
                "snapshot_hash": entry.snapshot_hash[:8] if entry.snapshot_hash else None,
                "hit_count": entry.hit_count,
                "is_stale": entry.is_stale,
                "last_error": entry.last_error,
                "error_count": entry.error_count,
                "build_duration_ms": round(entry.build_duration_ms, 1),
                "last_build_success": entry.last_build_success.isoformat() if entry.last_build_success else None,
                "last_build_failure": entry.last_build_failure.isoformat() if entry.last_build_failure else None
            }
        
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        total = stats["hit"] + stats["miss"]
        hit_ratio = stats["hit"] / total if total > 0 else 0
        
        return {
            "hit_count": stats["hit"],
            "miss_count": stats["miss"],
            "refresh_count": stats["refresh"],
            "build_count": stats["build_count"],
            "failed_build_count": stats["failed_build_count"],
            "hit_ratio": round(hit_ratio * 100, 2),
            "total_requests": total,
            "last_refresh": stats["last_refresh"].isoformat() if stats["last_refresh"] else None,
            "last_error": stats["last_error"].isoformat() if stats["last_error"] else None,
            "last_successful_build": stats["last_successful_build"].isoformat() if stats["last_successful_build"] else None,
            "last_failed_build": stats["last_failed_build"].isoformat() if stats["last_failed_build"] else None,
            "error_count": stats["error_count"],
            "ttl_seconds": self.ttl_seconds,
            "cache_size": len(cache_entries),
            "is_warm": self._is_warm,
            "warm_start_time": self._warm_start_time.isoformat() if self._warm_start_time else None,
            "is_refreshing": len(self._refresh_tasks),
            "last_build_duration_ms": round(last_duration, 1),
            "average_build_duration_ms": round(avg_duration, 1),
            "cache_uptime_seconds": round((datetime.now(timezone.utc) - self._warm_start_time).total_seconds()) if self._warm_start_time else 0,
            "oldest_snapshot_age_seconds": max([e.age_seconds for e in cache_snapshot.values()]) if cache_snapshot else 0,
            "newest_snapshot_age_seconds": min([e.age_seconds for e in cache_snapshot.values()]) if cache_snapshot else 0,
            "cache_entries": cache_entries
        }
    
    async def get_health(self) -> Dict[str, Any]:
        """Get cache health status with comprehensive checks"""
        # Get stats snapshot
        stats = await self._get_stats_snapshot()
        
        # Get cache snapshot
        cache_snapshot = await self._get_cache_snapshot()
        
        # Get build durations for metrics
        durations, last_duration = await self._get_build_durations_snapshot()
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        total = stats["hit"] + stats["miss"]
        hit_ratio = stats["hit"] / total if total > 0 else 0
        
        # Check cache status
        stale_entries = 0
        very_old_entries = 0
        empty_cache = len(cache_snapshot) == 0
        
        for entry in cache_snapshot.values():
            if entry.is_stale:
                stale_entries += 1
                if entry.age_seconds > self.max_stale_age_seconds:
                    very_old_entries += 1
        
        # Check if refresh is stuck
        is_refresh_stuck = len(self._refresh_tasks) > 0 and stats["last_refresh"] and (
            (datetime.now(timezone.utc) - stats["last_refresh"]).total_seconds() > self.warm_refresh_interval * 2
        )
        
        # Check if cache is too old
        is_cache_too_old = stats["last_refresh"] and (
            (datetime.now(timezone.utc) - stats["last_refresh"]).total_seconds() > self.max_stale_age_seconds
        )
        
        # Determine health status
        status = "healthy"
        if self._is_closed:
            status = "closed"
        elif not self._is_warm:
            status = "warming"
        elif empty_cache:
            status = "empty"
        elif stats["error_count"] > self.max_error_count * 2:
            status = "critical"
        elif stats["error_count"] > self.max_error_count:
            status = "degraded"
        elif very_old_entries > 0 or is_cache_too_old:
            status = "stale"
        elif stale_entries > len(cache_snapshot) * 0.5:  # > 50% stale
            status = "degraded"
        elif is_refresh_stuck:
            status = "degraded"
        
        return {
            "status": status,
            "is_warm": self._is_warm,
            "cache_size": len(cache_snapshot),
            "stale_entries": stale_entries,
            "very_old_entries": very_old_entries,
            "hit_ratio": round(hit_ratio * 100, 2),
            "error_count": stats["error_count"],
            "is_refreshing": len(self._refresh_tasks) > 0,
            "is_refresh_stuck": is_refresh_stuck,
            "is_cache_too_old": is_cache_too_old,
            "ttl_seconds": self.ttl_seconds,
            "last_build_duration_ms": round(last_duration, 1),
            "average_build_duration_ms": round(avg_duration, 1),
            "is_closed": self._is_closed,
            "background_tasks": len(self._background_tasks),
            "cache_uptime_seconds": round((datetime.now(timezone.utc) - self._warm_start_time).total_seconds()) if self._warm_start_time else 0
        }