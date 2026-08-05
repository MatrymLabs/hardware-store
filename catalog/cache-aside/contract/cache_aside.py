"""Contract: cache_aside -- lazy TTL caching with explicit invalidation.

  CacheAside(ttl_seconds, clock)
      A validated in-memory cache. `ttl_seconds` must be finite and positive; `clock` is injected
      so tests and deterministic consumers never sleep.

  get(key, loader) -> V
      Return a fresh cached value when present. Otherwise call `loader`, cache its return value
      until `now + ttl_seconds`, and return it. Loader exceptions propagate and are not cached.

  invalidate(key) -> bool
      Evict a known changed key immediately and report whether anything was present.

  clear(reset_stats=False)
      Evict all entries. Stats are preserved unless explicitly reset.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class CacheAsideContract(Protocol[K, V]):
    ttl_seconds: float

    def get(self, key: K, loader: Callable[[], V]) -> V: ...

    def is_cached(self, key: K) -> bool: ...

    def invalidate(self, key: K) -> bool: ...

    def clear(self, *, reset_stats: bool = False) -> None: ...

    @property
    def hits(self) -> int: ...

    @property
    def misses(self) -> int: ...

    @property
    def hit_rate(self) -> float: ...

    @property
    def size(self) -> int: ...

    def stats(self) -> dict[str, float | int]: ...
