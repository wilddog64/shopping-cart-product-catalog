# Retrospective — fix/products-order-by

**Date:** 2026-05-23
**Milestone:** Products ORDER BY fix + CI SHA bump
**PR:** #24 — merged to main (`28955c89245d82111f2e0801723b49fe32cee730`)
**Participants:** Claude, Copilot

## What Went Well
- One-line fix correctly identified and applied (`.order_by(Product.id)`)
- CI SHA bump discovered proactively while diagnosing the FTS issue
- Copilot caught a documentation inaccuracy (UUIDv5 vs insertion-order explanation)
- All Copilot threads replied to and resolved before merge

## What Went Wrong
- Stale infra SHA (`999f8d7`) was never bumped when `shopping-cart-infra` updated trivy-action from `@0.30.0` to `@v0.35.0` in PR #64 — caused CI to break silently after PR #23 merged; no image was built for weeks
- Bug doc originally had inaccurate wording ("mixed insertion order from multiple seed runs") — corrected after Copilot review

## Process Rules Added
| Rule | File |
|------|------|
| When bumping a shared workflow SHA in infra repo, update all downstream callers | (process note, not in CLAUDE.md) |

## Decisions Made
- Router-layer DB queries are pre-existing pattern — refactoring to service/CRUD layer deferred as separate task (not part of bug fix)
- CI SHA bump bundled into the same PR as the ORDER BY fix because it was blocking image deployment

## Theme
A one-line ORDER BY fix uncovered a silent CI breakage: the pinned `shopping-cart-infra` SHA in `ci.yml` referenced a deleted version of `trivy-action`, causing every push to main to fail silently since PR #23. No new image had been built, so FTS (added in PR #23) and ORDER BY were both missing from the deployed pod. The fix bundled both corrections into a single PR.
