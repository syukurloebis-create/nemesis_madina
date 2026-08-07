# retry_policy.py (fixed)
import time  # ADDED
import random
import math
from typing import Dict, List, Optional, Any
from enum import Enum

class RetryStrategy(Enum):
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"
    CIRCUIT_BREAKER = "circuit_breaker"

class RetryPolicy:
    """Retry policy with multiple strategies."""
    
    def __init__(self, strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 max_retries: int = 3):
        self.strategy = strategy
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.max_retries = max_retries
        self._attempt = 0
        self._consecutive_failures = 0
        self._circuit_open = False
        self._circuit_reset_time = None
    
    def get_delay(self, attempt: int) -> float:
        """Get delay for an attempt."""
        if attempt > self.max_retries:
            raise ValueError(f"Max retries {self.max_retries} exceeded")
        
        if self.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif self.strategy == RetryStrategy.LINEAR:
            return min(self.base_delay * attempt, self.max_delay)
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            return min(self.base_delay * (2 ** attempt), self.max_delay)
        elif self.strategy == RetryStrategy.EXPONENTIAL_JITTER:
            delay = self.base_delay * (2 ** attempt)
            jitter = random.uniform(0, delay * 0.1)
            return min(delay + jitter, self.max_delay)
        elif self.strategy == RetryStrategy.CIRCUIT_BREAKER:
            if self._circuit_open:
                if self._circuit_reset_time:
                    elapsed = time.time() - self._circuit_reset_time
                    if elapsed > 30:
                        self._circuit_open = False
                        self._consecutive_failures = 0
                    else:
                        return self.max_delay * 2
            return min(self.base_delay * (2 ** attempt), self.max_delay)
        else:
            return 0.0
    
    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._circuit_open = False
    
    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self.strategy == RetryStrategy.CIRCUIT_BREAKER:
            if self._consecutive_failures >= 5:
                self._circuit_open = True
                self._circuit_reset_time = time.time()
    
    def should_retry(self, attempt: int) -> bool:
        if self._circuit_open:
            return False
        return attempt < self.max_retries