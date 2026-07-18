"""
Timer untuk mengukur durasi operasi.
"""

import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

from backend.core.context import get_request_id


@dataclass
class TimingResult:
    """Hasil timing untuk satu operasi."""
    operation: str
    duration_ms: float
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TimingCollector:
    """
    Collector untuk timing data.
    """

    def __init__(self):
        self._timings: list = []
        self._engine_timings: Dict[str, list] = {}

    def add_timing(self, timing: TimingResult):
        """Tambahkan timing."""
        self._timings.append(timing)
        engine = timing.metadata.get("engine")
        if engine:
            if engine not in self._engine_timings:
                self._engine_timings[engine] = []
            self._engine_timings[engine].append(timing)

    def get_timings(self) -> list:
        """Dapatkan semua timings."""
        return self._timings

    def get_engine_timings(self, engine: str) -> list:
        """Dapatkan timings untuk engine tertentu."""
        return self._engine_timings.get(engine, [])

    def get_summary(self) -> Dict[str, Any]:
        """Dapatkan ringkasan timings."""
        if not self._timings:
            return {"total_ops": 0}

        total = len(self._timings)
        success = sum(1 for t in self._timings if t.success)
        avg_duration = sum(t.duration_ms for t in self._timings) / total

        return {
            "total_ops": total,
            "success_count": success,
            "error_count": total - success,
            "avg_duration_ms": round(avg_duration, 2),
            "engines": {
                name: {
                    "count": len(timings),
                    "avg_duration_ms": round(
                        sum(t.duration_ms for t in timings) / len(timings),
                        2
                    ) if timings else 0,
                    "min_ms": round(min(t.duration_ms for t in timings), 2) if timings else 0,
                    "max_ms": round(max(t.duration_ms for t in timings), 2) if timings else 0
                }
                for name, timings in self._engine_timings.items()
            }
        }


# Singleton collector
_timing_collector = TimingCollector()


def get_timing_collector() -> TimingCollector:
    """Dapatkan timing collector singleton."""
    return _timing_collector


@contextmanager
def measure_time(operation: str, **metadata):
    """
    Context manager untuk mengukur durasi operasi.

    Usage:
        with measure_time("fraud_engine", engine="fraud", case_id=case_id):
            result = await fraud_detector.detect(case_id)
    """
    start_time = time.perf_counter()
    success = True
    error = None

    try:
        yield
    except Exception as e:
        success = False
        error = str(e)
        raise
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        timing = TimingResult(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            error=error,
            metadata={
                **metadata,
                "request_id": get_request_id() or "N/A"
            }
        )
        _timing_collector.add_timing(timing)

        # Log timing
        logger = logging.getLogger(__name__)
        status = "✓" if success else "✗"
        logger.debug(
            f"[TIMING] {operation}: {duration_ms:.1f}ms {status}",
            extra={
                "operation": operation,
                "duration_ms": round(duration_ms, 2),
                "success": success,
                "metadata": metadata
            }
        )