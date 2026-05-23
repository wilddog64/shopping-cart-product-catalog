# Retrospective — Milestone 2: MinIO Image Pipeline + 1,000-Product Seed + FTS

**Date:** 2026-05-23
**Milestone:** MinIO image pipeline, 1,000-product seed, full-text search
**PRs:** infra #62, product-catalog #23, frontend #20 — all merged to main
**Participants:** Claude, Codex, Copilot

## What Went Well
- Codex implemented all 3 specs cleanly across 3 repos in one pass
- Copilot caught 9 real bugs before merge (Go template hyphens, mc curl download, hook race, FTS mismatch, psql credential exposure, pip/readOnlyRootFilesystem, nginx proxy scope, X-Forwarded-Proto, Picsum docs inaccuracy)
- ArgoCD hook-weight ordering pattern correctly sequenced bucket-init → image-upload
- ESO Go template fix (index . "root-key") resolved silent credential failure
- Conflict resolution on PR #23 after PR #22 squash merge completed cleanly

## What Went Wrong
- Spec initially had frontend nginx proxy in minio-data-layer spec AND product-seed spec — duplication caught and fixed before handoff
- image-upload-configmap.yaml missing from DoD checklist — caught after Codex completed
- PR #23 went dirty after PR #22 squash merge — requires merge conflict resolution before CI triggers
- mc binary downloaded via curl in initContainer — supply chain risk; fixed to pinned image

## Process Rules Reinforced
| Rule | Trigger |
|------|---------|
| GIN index SQL must match query expression exactly | FTS mismatch finding |
| psql credentials via PGPASSWORD, never URL | Credential exposure finding |
| pip --target /tmp with PYTHONPATH for readOnlyRootFilesystem | pip install failure |
| nginx proxy scope to specific bucket, not /minio/ | Overly broad proxy finding |
| ArgoCD hook-weight for dependent PostSync jobs | Hook race condition |
| initContainers must use pinned images, not curl downloads | Supply chain finding |

## Decisions Made
- 20 JPEG images (one per subcategory slug) serve 1,000 product rows — intentional design for dev/test environment
- ESO ExternalSecret for MinIO credentials (root-user / root-password keys require Go template `index` accessor)
- Python/Pillow for in-cluster image generation (no external Picsum dependency)

## Theme
This milestone wired the full product image pipeline: MinIO deployed via ArgoCD with ESO credentials, bucket initialized and 20 subcategory images generated in-cluster, 1,000 products seeded with GIN full-text search, all surfaced through a scoped nginx proxy. Nine Copilot findings caught real runtime failures before they reached the cluster — the security and correctness net held.
