# Bug: CI build-push-deploy fails — stale infra SHA references trivy-action@0.30.0

**Date:** 2026-05-23
**File:** `.github/workflows/ci.yml`
**Branch:** `fix/products-order-by`

---

## Problem

`Build, Scan & Push` job fails on every push to `main` with:

```
Unable to resolve action `aquasecurity/trivy-action@0.30.0`, unable to find version `0.30.0`
```

No Docker image is built or pushed to ghcr.io, so the deployed pod on ubuntu-k3s runs the
pre-FTS image (before PR #23). This means `?q=` fulltext search silently returns all products.

**Root cause:** `ci.yml` calls the shared `build-push-deploy.yml` in `shopping-cart-infra`
at a pinned commit SHA `999f8d70277b92d928412ff694852b05044dbb75`. That old commit referenced
`aquasecurity/trivy-action@0.30.0`. The infra workflow was subsequently updated to `@v0.35.0`
(PR #64 / commit `e7df259`), but the product-catalog PIN was never bumped.

---

## Reproduction

```
git push origin main  # or merge a PR
```

Expected: CI builds image, pushes `ghcr.io/wilddog64/shopping-cart-product-catalog:latest`
Actual: `Build, Scan & Push` job fails; no image pushed

---

## Fix

### Change 1 — `.github/workflows/ci.yml` line 86

Update the pinned SHA to the current `shopping-cart-infra` main HEAD so the workflow
uses the already-fixed `@v0.35.0` trivy-action reference.

**Exact old block (line 86):**

```yaml
    uses: wilddog64/shopping-cart-infra/.github/workflows/build-push-deploy.yml@999f8d70277b92d928412ff694852b05044dbb75
```

**Exact new block:**

```yaml
    uses: wilddog64/shopping-cart-infra/.github/workflows/build-push-deploy.yml@dd7496bf6ad61b74879039beeef72bb3ccc5fd1d
```

---

## Files Changed

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | Update pinned infra SHA from `999f8d7` to `dd7496b` |
| `CHANGELOG.md` | Add `[Unreleased]` entry for this fix |

---

## Rules

- Code change limited to `.github/workflows/ci.yml` and `CHANGELOG.md`
- CI must pass after this change

---

## Definition of Done

- [ ] `.github/workflows/ci.yml` line 86 SHA updated to `dd7496bf6ad61b74879039beeef72bb3ccc5fd1d`
- [ ] CHANGELOG updated
- [ ] Committed and pushed to `fix/products-order-by`
- [ ] memory-bank updated with commit SHA

**Commit message (exact):**
```
fix(ci): bump infra SHA to dd7496b — resolves trivy-action@0.30.0 not found
```
