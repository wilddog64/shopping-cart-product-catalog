# Retrospective — shopping-cart-product-catalog PR #29

**Date:** 2026-05-24
**PR:** #29 — merged to main @ `6ca5e88d`
**Participants:** Claude, Codex, Copilot

## What Went Well

- **ArgoCD drift fix via IgnoreExtraneous:** Added `argocd.argoproj.io/compare-options: IgnoreExtraneous` annotation to ExternalSecret `target.template.metadata` — eliminates perpetual OutOfSync state caused by ESO-managed labels not matching sync diff. Live cluster now converges on first apply.
- **Sync-wave ordering:** Changed ExternalSecret sync-wave from `"0"` to `"-1"` (pre-wave) — ensures Vault credentials are provisioned before wave-0 pods attempt to mount the Secret. Prevents race condition during fresh cluster deploys where pods would fail with `CreateContainerConfigError` while waiting for ESO to sync.
- **Copilot review clarity:** Copilot flagged the merge-claim language in PR #28 retrospective; required clarification that PR #28 was already merged before PR #29 was created. Retrospective now clearly scopes the work.

## What Went Wrong

- **Branch rebase requirement:** PR required rebase before merge because PR #28 had already landed on main. Both PRs were developed in parallel; PR #28 merged first, forcing PR #29 rebase. Mitigated by: (1) sequential PR planning for dependent work, (2) clear tracking of parallel branch state in specs.

## Process Rules Added

| Rule | File |
|------|------|
| ExternalSecret IgnoreExtraneous annotation required when target Secret is ESO-managed | `docs/retro/2026-05-24-shopping-cart-product-catalog-pr29-retrospective.md` |
| ExternalSecret sync-wave must be "-1" (pre-wave) for credentials to load before dependent pods | `docs/retro/2026-05-24-shopping-cart-product-catalog-pr29-retrospective.md` |

## Decisions Made

- ExternalSecret `target.template.metadata.annotations` is the location for ArgoCD-specific diff rules; placed here to avoid conflicts with instance-level annotations on the ExternalSecret resource itself.
- Sync-wave "-1" is now standard for all credential/secret provisioning resources in product-catalog; wave ordering: `-1` (secrets) → `0` (deployments) → `+N` (dependent services).

## Theme

Fast-follow to PR #28 (ExternalSecret adoption). Fixed two critical ArgoCD-ESO integration issues: perpetual OutOfSync and race condition during pod startup. Both issues resolved via standard Kubernetes patterns (sync-wave + annotation-based diff filtering).

---

## Previous Release Context

- **PR #28:** Adopted ExternalSecret for Vault-based secret provisioning; added `k8s/base/externalsecret.yaml`; removed placeholder Secret manifests.
- **PR #26:** Initial ESO (External Secrets Operator) adoption.
- **PR #23:** Added 1,000-product seed job + full-text search (FTS) index.

## Files Changed

- `k8s/base/externalsecret.yaml` — added sync-wave `-1` and IgnoreExtraneous annotation to target template
- `docs/retro/2026-05-24-shopping-cart-product-catalog-pr28-retrospective.md` — added (same commit)
