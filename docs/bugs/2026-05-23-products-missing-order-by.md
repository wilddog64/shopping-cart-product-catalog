# Bug: GET /api/products returns only first-category products — missing ORDER BY

**Date:** 2026-05-23
**File:** `src/product_catalog/routers/products.py`
**Branch:** `main` (fix on `fix/products-order-by`)

---

## Problem

`GET /api/products` always returns the first page populated with laptops even though the
database contains 1,000 products across 20 subcategories and 4 top-level categories.

**Root cause:** The SQLAlchemy query at line 51 has no `.order_by()` call. PostgreSQL
returns rows in undefined heap order, which in practice is the physical insertion order.
Because the seed job inserts all 50 laptop products first (subcategory index 0), they occupy
the lowest physical pages and are always returned on page 1 without an explicit sort.

---

## Reproduction

```
GET /api/products
```

Expected: first page shows a mix of categories (Electronics, Accessories, Monitors, Peripherals).
Actual: first 20 results are all `LAPTOP-*` products.

---

## Fix

### Change 1 — `src/product_catalog/routers/products.py` line 51

Add `.order_by(Product.id)` before `.offset().limit()` so results are stable and consistent
across pages, and naturally varied because the DB has mixed insertion order from multiple seed runs.

**Exact old block (lines 50–51):**

```python
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
```

**Exact new block:**

```python
    total = query.count()
    items = query.order_by(Product.id).offset((page - 1) * page_size).limit(page_size).all()
```

---

## Files Changed

| File | Change |
|------|--------|
| `src/product_catalog/routers/products.py` | Add `.order_by(Product.id)` to list query |

---

## Rules

- Code change limited to `src/product_catalog/routers/products.py`
- `pytest` must pass with no new failures
- CHANGELOG update required

---

## Definition of Done

- [ ] Line 51 updated with `.order_by(Product.id)`
- [ ] `pytest` passes
- [ ] First page of `GET /api/products` returns mixed categories
- [ ] Committed and pushed to `fix/products-order-by`
- [ ] CHANGELOG updated
- [ ] memory-bank updated with commit SHA

**Commit message (exact):**
```
fix(products): add ORDER BY id to list query — prevents first page from returning only first-inserted subcategory
```
