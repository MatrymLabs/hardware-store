# Hardware Store control panel. Verbs DO, nouns SHOW. Gates only report; fix mutates.
PY ?= .venv/bin/python

# --- Gate caches: explicit, writable anywhere, identical for both benches.
# ruff and mypy default to .ruff_cache/.mypy_cache in the working directory. On CX-021 that location
# was not writable for one bench, which had to run the gate with environment prefixes and record
# them in its return. An order naming `make check` while one bench decorates it has two commands
# wearing one name, so the location is declared here. `?=`, never `=`: a caller that still needs to
# redirect must be able to, and must be able to tell if it failed to.
RUFF_CACHE_DIR ?= /tmp/matrymlabs-hardware-store-ruff-cache
MYPY_CACHE_DIR ?= /tmp/matrymlabs-hardware-store-mypy-cache
export RUFF_CACHE_DIR MYPY_CACHE_DIR
PIP ?= .venv/bin/pip

.PHONY: env fix lint typecheck test check registry store-check search help

help:
	@echo "env         create .venv and install dev tools"
	@echo "fix         auto-format + auto-fix lint (mutates)"
	@echo "lint        ruff check (gate)"
	@echo "typecheck   mypy (gate)"
	@echo "test        pytest the tool suite (gate)"
	@echo "store-check run the integrity gate over the Store (gate)"
	@echo "check       lint + typecheck + test + store-check (the full gate)"
	@echo "search q=... search the catalog, e.g. make search q='rate limiting'"

env:
	python3 -m venv .venv
	$(PIP) install -e ".[dev]"

fix:
	$(PY) -m ruff format .
	$(PY) -m ruff check --fix .

lint:
	$(PY) -m ruff check .

typecheck:
	$(PY) -m mypy hardware_store

test:
	$(PY) -m pytest -q

# registry.json MIRRORS the cards and store_check enforces it. The generator has always existed as
# store_lib.write_registry, reached by promote and consume, but never from the control panel - so a
# card edited by hand left the mirror stale with hand-editing as the only visible way out. That is
# the "fix the generator, never the file" rule failing for want of a target, not for want of a
# generator. Twice filed as "the mirror has no generator", and twice wrong.
registry:
	@$(PY) -c "from pathlib import Path; from hardware_store.store_lib import write_registry; \
	  n=len(write_registry(Path('.'))); print(f'registry: rebuilt from catalog/, {n} entries')"

store-check:
	$(PY) -m hardware_store.store_check

check: lint typecheck test store-check

search:
	$(PY) -m hardware_store.store_search "$(q)"
