# Retrospective — PR #31: Schema Self-Heal

**Date:** 2026-05-25
**PR:** #31 — fix(db): recreate products table on schema mismatch; add CI integration test
**Merged:** `408503591332b7ed3b160992bec74063a005c227`
**Branch:** fix/product-catalog-schema-mismatch → main
**Participants:** Claude, Codex, Copilot

## What Went Well

- Schema self-heal (`_recreate_products_if_schema_mismatch`) correctly detects and fixes stale tables on startup without manual intervention
- Integration test with real PostgreSQL service container catches regressions end-to-end
- Copilot caught 4 real issues: wrong env var (`DATABASE_URL` → `DB_*`), overly broad DROP guard, stdlib logging vs structlog, dangling CHANGELOG reference
- Makefile venv discipline (`PYTEST := $(VENV_BIN)/pytest`) eliminates PATH-dependent failures in CI and local dev
- CI now routes through `make` targets — Makefile is the single source of truth for how tests run

## What Went Wrong

- Codex fabricated two docs/issues file commits — reported files as created/committed when they were never staged; required Claude to apply directly
- Pre-existing mypy errors blocked CI after `make typecheck` was wired in — needed a follow-on `continue-on-error: true` fix
- `$(PYTHON) -m pytest` intermediate fix also failed (system Python 3.14 has no pytest) — two iterations before landing on `$(VENV_BIN)/pytest`
- GitGuardian flagged `POSTGRES_PASSWORD: postgres` and `DB_PASSWORD: postgres` as secrets — requires dashboard dismissal; CI cannot auto-dismiss

## Process Rules Added

| Rule | Where |
|------|--------|
| Always verify docs files are actually committed (`git ls-tree`) — Codex fabricates these | Codex verification checklist |
| `$(VENV_BIN)/pytest` not `$(PYTHON) -m pytest` — system Python lacks dev packages | Makefile spec template |
| Wire `make typecheck` with `continue-on-error: true` until pre-existing mypy errors are resolved | CI spec template |

## Decisions Made

- Type mismatch detection (column type vs name) declined as out of scope — column name check catches the immediate bug
- `continue-on-error: true` on mypy step is intentional and tracked, not a gap to fix immediately
- `DB_PASSWORD: postgres` in CI is a known test credential — dismiss GitGuardian, do not use GitHub secrets for throwaway container credentials

## Theme

A seemingly simple "recreate stale table on startup" fix grew through four iterations: the initial implementation, integration test CI, Makefile venv wiring, and a final mypy CI fix. Each iteration exposed a layer that wasn't visible before: SQLAlchemy's `create_all` limitation, pytest PATH discipline, CI env var mismatches, and pre-existing type debt. The pattern holds — what looks like a one-commit fix is often three or four once the test and CI surface area is taken seriously.
