# Copilot PR #22 Review Findings

**Date:** 2026-05-23
**PR:** #22 — feat: add product-catalog seed job with 8 sample products
**Fix commit:** `95c48b7`

## Finding 1 — Missing /tmp volume for readOnlyRootFilesystem

**File:** `k8s/base/seed-job.yaml` line 60
**Flagged:** `readOnlyRootFilesystem: true` set but no writable `/tmp` volume mounted; `psql`/`sh` need a writable temp directory and may fail at runtime.

**Fix:**
```yaml
# Before — no volumes section, no volumeMounts
        securityContext:
          readOnlyRootFilesystem: true

# After — added emptyDir volume + mount
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        securityContext:
          readOnlyRootFilesystem: true
      volumes:
      - name: tmp
        emptyDir: {}
```

**Root cause:** Spec template copied securityContext from the Deployment but omitted the accompanying `/tmp` emptyDir pattern used there.

**Process note:** Any container with `readOnlyRootFilesystem: true` must include an `emptyDir` mount for `/tmp`. Add this as a spec checklist item.

---

## Finding 2 — gen_random_uuid() portability

**File:** `k8s/base/seed-job.yaml` line 47
**Flagged:** `gen_random_uuid()` requires `pgcrypto` on PostgreSQL < 13; seed Job fails on fresh clusters with older postgres.

**Fix:**
```sql
-- Before
(gen_random_uuid(), 'LAPTOP-001', ...),

-- After — hardcoded UUID v4 literals
('c54557c7-c2d6-444a-93e3-19d61538b76a', 'LAPTOP-001', ...),
```
All 8 rows replaced with pre-generated UUID v4 literals.

**Root cause:** `gen_random_uuid()` is a PG13+ builtin but is not available without `pgcrypto` on older versions; using literals eliminates the dependency entirely.

**Process note:** Seed Jobs targeting arbitrary postgres versions must use literal UUIDs or shell-generated values, not `gen_random_uuid()`.

---

## Finding 3 — Stale configmap.yaml not in kustomization resources

**File:** `k8s/base/configmap.yaml` line 41
**Flagged:** `kustomization.yaml` uses `configMapGenerator` (sourced from `configmap.env`) but `configmap.yaml` is not in `resources:` — it is dead code that causes configuration drift confusion.

**Fix:** Removed `k8s/base/configmap.yaml` entirely. `configMapGenerator` with `configmap.env` is the sole source of truth.

**Root cause:** Pre-existing stale file from an earlier migration to `configMapGenerator`; never cleaned up.

**Process note:** When migrating a ConfigMap to `configMapGenerator`, always delete the original `configmap.yaml` in the same commit to prevent confusion.
