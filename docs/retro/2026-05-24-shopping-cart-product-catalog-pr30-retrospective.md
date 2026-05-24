# Retrospective — shopping-cart-product-catalog PR #30

**Date:** 2026-05-24
**PR:** #30 — merged to main (`94d20d0d`)
**Participants:** Claude, Codex, Copilot

## What Went Well

- **Image tag bump**: Bumped `k8s/base/kustomization.yaml` `newTag` from stale PR #22 SHA to PR #29 SHA, deploying the `init_db()` fix that creates `products_search_vector` in the database — unblocking the `product-catalog-fts-index` PostSync job
- **ExternalSecret IgnoreExtraneous**: Added `argocd.argoproj.io/compare-options: IgnoreExtraneous` to ExternalSecret target template, preventing permanent ArgoCD OutOfSync caused by ESO-managed Secret retaining ArgoCD tracking annotations
- **sync-wave -1**: Changed ExternalSecret sync-wave from `0` to `-1` so ESO provisions the Secret before wave-0 Deployments and Jobs — prevents `CreateContainerConfigError` on fresh cluster deploys
- **Copilot catch**: Copilot flagged that PR description only mentioned the image tag bump, missing the ExternalSecret changes. PR description was updated to cover all three changes before merge

## What Went Wrong

- **Stale image tag root cause**: CI builds and pushes a new image on every main merge but does NOT auto-commit the updated tag to `kustomization.yaml`. This caused the Deployment to run PR #22 code through PRs #23–#29. ArgoCD Image Updater is configured in k3d-manager (`scripts/etc/argocd/image-updater/`) but not yet deployed — once `make up` deploys it, this will be automated
- **PR scope creep**: ExternalSecret changes (from PR #29 scope) landed on this branch alongside the image tag fix, making the PR cover three unrelated concerns. Copilot correctly flagged this

## Process Rules Added

| Rule | Detail |
|------|--------|
| Image tag discipline | After every PR merge that changes app behavior, manually bump `newTag` in `kustomization.yaml` until ArgoCD Image Updater is live |
| PR scope discipline | Keep image tag bumps and ExternalSecret changes in separate PRs |

## Decisions Made

- ArgoCD Image Updater will use `write-back-method: argocd` (stores override in Application object, not git commits) — avoids branch protection conflicts
- `products_search_vector` function is created in `init_db()` at startup (not as a migration) — PostSync fts-index job depends on this being present before it runs

## Theme

Cluster stabilization after PR #29. Three separate fixes landed together: the image tag that was blocking fts-index from running, the ExternalSecret OutOfSync loop that was generating constant ArgoCD alerts, and the sync-wave ordering that prevented secrets from being ready before pods. Copilot caught the PR description gap. ArgoCD Image Updater is configured but not yet live — the manual tag process remains until `make up` deploys it.
