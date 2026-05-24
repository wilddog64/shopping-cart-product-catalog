# Retrospective — shopping-cart-product-catalog PR #28

**Date:** 2026-05-24
**PR:** #28 — merged to main (SHA `c2b5a43`)
**Participants:** Claude, Codex, Copilot

## What Went Well

- **ExternalSecret resource integration:** Added `k8s/base/externalsecret.yaml` provisioning `product-catalog-secrets` from Vault, eliminating the placeholder Secret pattern and fixing `CreateContainerConfigError` on fresh cluster deploys.
- **Kustomize label alignment:** Removed redundant kustomize-controlled labels (`app.kubernetes.io/name`, `app.kubernetes.io/part-of`) from ExternalSecret, leaving only instance + component labels. Build output now matches live resource state; `kubectl kustomize k8s/base/` runs warning-free.
- **Copilot catch on label conflict:** Copilot review thread flagged the ExternalSecret label duplication in the initial commit, preventing downstream kustomize build misalignment.

## What Went Wrong

- None recorded.

## Process Rules Added

| Rule | File |
|------|------|
| ExternalSecret label scope rules — do not include standard CommonLabels when they conflict with external label injectors | `docs/retro/2026-05-24-shopping-cart-product-catalog-pr28-retrospective.md` |

## Decisions Made

- ExternalSecret `product-catalog-secrets` is the source-of-truth for all app-layer credentials; placeholder Secret no longer part of kustomization.
- StandardLabels from CommonLabels remain on deployment, service, and pod resources; ExternalSecret uses minimal label set to avoid conflicts with existing live instance.

## Theme

Fast-follow to PR #26 (ESO adoption). Addressed label duplication that emerged during testing. Copilot review caught the issue before merge.

---

## Previous Release Context

- **PR #26:** Adopted ESO (External Secrets Operator) for Vault-based secret provisioning; removed placeholder Secret manifests.
- **PR #23:** Added 1,000-product seed job + full-text search (FTS) index.
- **PR #24:** Fixed product list ordering (ORDER BY id) + CI SHA bump.

## Files Changed

- `k8s/base/externalsecret.yaml` — new file, Vault integration
- `k8s/base/kustomization.yaml` — added ExternalSecret resource
- `CHANGELOG.md` — Unreleased section updated with ExternalSecret entry
