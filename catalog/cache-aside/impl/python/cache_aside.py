"""cache_aside -- lazy TTL caching with explicit invalidation and stats."""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class CacheError(ValueError):
    """A refused cache configuration."""


@dataclass
class CacheAside(Generic[K, V]):
    """A lazy cache: values load on a miss and expire after `ttl_seconds`."""

    ttl_seconds: float
    clock: Callable[[], float] = time.monotonic
    _entries: dict[K, tuple[V, float]] = field(default_factory=dict)
    _hits: int = 0
    _misses: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.ttl_seconds, (int, float)) or isinstance(self.ttl_seconds, bool):
            raise CacheError(f"ttl_seconds must be a finite number, got {self.ttl_seconds!r}")
        ttl = float(self.ttl_seconds)
        if not math.isfinite(ttl):
            raise CacheError(f"ttl_seconds must be a finite number, got {self.ttl_seconds!r}")
        if ttl <= 0:
            raise CacheError(f"ttl_seconds must be > 0, got {self.ttl_seconds!r}")
        self.ttl_seconds = ttl

    def get(self, key: K, loader: Callable[[], V]) -> V:
        """Return a fresh cached value, or load and cache on miss/expiry."""
        now = self.clock()
        entry = self._entries.get(key)
        if entry is not None and entry[1] > now:
            self._hits += 1
            return entry[0]
        self._misses += 1
        value = loader()
        self._entries[key] = (value, now + self.ttl_seconds)
        return value

    def is_cached(self, key: K) -> bool:
        """Whether `key` currently has a fresh cached value."""
        entry = self._entries.get(key)
        return entry is not None and entry[1] > self.clock()

    def invalidate(self, key: K) -> bool:
        """Evict `key` immediately. Returns whether an entry was present."""
        return self._entries.pop(key, None) is not None

    def clear(self, *, reset_stats: bool = False) -> None:
        """Evict all entries, optionally resetting hit/miss counters."""
        self._entries.clear()
        if reset_stats:
            self._hits = 0
            self._misses = 0

    @property
    def hits(self) -> int:
        """How many reads were served from cache."""
        return self._hits

    @property
    def misses(self) -> int:
        """How many reads loaded from the source."""
        return self._misses

    @property
    def hit_rate(self) -> float:
        """Fraction of reads served from cache."""
        total = self._hits + self._misses
        return self._hits / total if total else 0.0

    @property
    def size(self) -> int:
        """How many entries are stored, including expired entries not yet read."""
        return len(self._entries)

    def stats(self) -> dict[str, float | int]:
        """Snapshot suitable for metrics."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self.hit_rate, 4),
            "size": self.size,
        }
