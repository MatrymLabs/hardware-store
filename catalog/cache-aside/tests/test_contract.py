"""Contract tests for cache_aside."""

from __future__ import annotations

import pytest
from cache_aside import CacheAside, CacheError


class _Clock:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


class _Loader:
    def __init__(self, value: int) -> None:
        self.value = value
        self.calls = 0

    def __call__(self) -> int:
        self.calls += 1
        return self.value


def test_miss_loads_then_hit_serves_from_cache() -> None:
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=10, clock=_Clock())
    load = _Loader(42)
    assert cache.get("k", load) == 42
    assert cache.get("k", load) == 42
    assert load.calls == 1
    assert cache.hits == 1 and cache.misses == 1


def test_expiry_reloads_from_source() -> None:
    clock = _Clock()
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=10, clock=clock)
    load = _Loader(1)
    cache.get("k", load)
    clock.advance(9.9)
    cache.get("k", load)
    assert load.calls == 1
    clock.advance(0.2)
    cache.get("k", load)
    assert load.calls == 2


def test_exact_ttl_boundary_is_expired() -> None:
    clock = _Clock()
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=5, clock=clock)
    load = _Loader(1)
    cache.get("k", load)
    clock.advance(5.0)
    cache.get("k", load)
    assert load.calls == 2


def test_is_cached_reflects_freshness_without_loading() -> None:
    clock = _Clock()
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=10, clock=clock)
    assert cache.is_cached("k") is False
    cache.get("k", _Loader(1))
    assert cache.is_cached("k") is True
    clock.advance(10.0)
    assert cache.is_cached("k") is False


def test_invalidate_evicts_known_changes() -> None:
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=100, clock=_Clock())
    load = _Loader(7)
    cache.get("k", load)
    assert cache.invalidate("k") is True
    assert cache.invalidate("k") is False
    cache.get("k", load)
    assert load.calls == 2


def test_clear_empties_entries_and_preserves_stats_by_default() -> None:
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=100, clock=_Clock())
    cache.get("a", _Loader(1))
    cache.get("b", _Loader(2))
    assert cache.size == 2
    cache.clear()
    assert cache.size == 0
    assert cache.hits == 0 and cache.misses == 2


def test_clear_can_reset_stats() -> None:
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=100, clock=_Clock())
    load = _Loader(1)
    cache.get("k", load)
    cache.get("k", load)
    cache.clear(reset_stats=True)
    assert cache.size == 0
    assert cache.hits == 0 and cache.misses == 0


def test_hit_rate_and_stats_snapshot() -> None:
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=100, clock=_Clock())
    assert cache.hit_rate == 0.0
    load = _Loader(1)
    cache.get("k", load)
    cache.get("k", load)
    cache.get("k", load)
    assert cache.hit_rate == pytest.approx(2 / 3)
    assert cache.stats() == {"hits": 2, "misses": 1, "hit_rate": 0.6667, "size": 1}


def test_failed_loader_is_not_cached() -> None:
    cache: CacheAside[str, int] = CacheAside(ttl_seconds=100, clock=_Clock())
    calls = {"n": 0}

    def flaky() -> int:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("source down")
        return 5

    with pytest.raises(RuntimeError):
        cache.get("k", flaky)
    assert cache.is_cached("k") is False
    assert cache.get("k", flaky) == 5
    assert calls["n"] == 2


@pytest.mark.parametrize("ttl", [0, -1, -0.5, float("nan"), float("inf"), True])
def test_bad_ttl_is_refused(ttl: object) -> None:
    with pytest.raises(CacheError, match="ttl_seconds"):
        CacheAside(ttl_seconds=ttl, clock=_Clock())  # type: ignore[arg-type]
