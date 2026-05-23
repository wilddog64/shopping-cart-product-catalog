# Copilot PR #23 Review Findings

**Date:** 2026-05-23
**PR:** #23 — feat: 1,000-product seed with MinIO images and full-text search
**Fix commit:** `e86c6b5`

## Finding 1 — FTS index and query expressions don't match (GIN index not used)

**File:** `src/product_catalog/routers/products.py` line 46, `k8s/base/fts-index-job.yaml` line 38
**Flagged:** Index uses `name || ' ' || COALESCE(description, '') || ' ' || COALESCE(category, '')`; query uses `concat_ws(' ', name, description, category)`. PostgreSQL requires syntactically identical expressions to use a functional GIN index — mismatch forces a sequential scan.

**Fix:** Updated `fts-index-job.yaml` to use `concat_ws` to match the query:
```sql
-- Before
USING GIN(
  to_tsvector('english',
    name || ' ' ||
    COALESCE(description, '') || ' ' ||
    COALESCE(category, '')
  )
);

-- After — matches concat_ws(' ', ...) in products.py
USING GIN(to_tsvector('english', concat_ws(' ', name, description, category)));
```

**Root cause:** Index SQL was written from the spec's example which used `||`/COALESCE; the Python query was written independently using SQLAlchemy's `concat_ws`. Two authors, different idioms.

**Process note:** The FTS index SQL and the SQLAlchemy query filter must use the exact same PostgreSQL expression. Define the canonical expression once in the spec and copy it to both files.

---

## Finding 2 — psql URL exposes DB password in process argument list

**File:** `k8s/base/fts-index-job.yaml` line 37
**Flagged:** `psql "postgresql://${DB_USERNAME}:${DB_PASSWORD}@..."` puts the password in the process argument string, visible in `ps aux` and container logs.

**Fix:**
```bash
# Before
psql "postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}" <<'SQL'

# After — password in env var, not argument; fail-fast flag added
PGPASSWORD="${DB_PASSWORD}" psql \
  -h "${DB_HOST}" -p "${DB_PORT}" \
  -U "${DB_USERNAME}" -d "${DB_NAME}" \
  -v ON_ERROR_STOP=1 <<'SQL'
```

**Root cause:** URL format is convenient but leaks credentials. PGPASSWORD env var is the standard psql credential mechanism.

**Process note:** All psql commands in Jobs must use `PGPASSWORD` + `-h/-U/-d` flags. Never put credentials in the connection URL.

---

## Finding 3 — pip install fails with readOnlyRootFilesystem: true

**File:** `k8s/base/seed-job.yaml` line 37
**Flagged:** `pip install --quiet psycopg2-binary` writes to `/usr/local/lib/python*/site-packages` which is read-only with `readOnlyRootFilesystem: true`. Job fails before running seed.py.

**Fix:**
```bash
# Before
pip install --quiet psycopg2-binary
python3 /scripts/seed.py

# After — install to /tmp (writable emptyDir); set PYTHONPATH
pip install --quiet --target /tmp/packages psycopg2-binary
PYTHONPATH=/tmp/packages python3 /scripts/seed.py
```

**Root cause:** The `/tmp` emptyDir was added for psql compatibility but not used for pip install targeting.

**Process note:** Any container with `readOnlyRootFilesystem: true` that runs `pip install` must use `--target /tmp/<dir>` and set `PYTHONPATH` accordingly.
