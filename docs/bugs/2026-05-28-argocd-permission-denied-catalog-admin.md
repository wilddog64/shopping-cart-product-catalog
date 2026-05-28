# Bug: ArgoCD Permission Denied for Catalog Admin

**Date:** 2026-05-28
**Severity:** Medium — prevents manual sync and management for scoped admins
**Status:** Open
**Assignee:** Gemini CLI

## Symptom
Users in the `catalog-admins` group receive a "permission denied" error when attempting to manually sync the `shopping-cart-product-catalog` application in ArgoCD.

## Root Cause Analysis
The ArgoCD RBAC configuration (`argocd-rbac-cm`) contains a naming mismatch. The policy is defined for `product-catalog`, but the actual application name is `shopping-cart-product-catalog`.

**Current (Incorrect) Policy:**
```csv
p, role:catalog-admin, applications, *, shopping-cart/product-catalog, allow
```

**Actual Resource:**
Project: `shopping-cart`
Application: `shopping-cart-product-catalog`

## Proposed Resolution
Update the RBAC policy in the infrastructure repository (`shopping-cart-infra`) to match the actual application name.

**Target:** `argocd-rbac-cm` ConfigMap
**New Policy:**
```csv
p, role:catalog-admin, applications, *, shopping-cart/shopping-cart-product-catalog, allow
```

## Verification
1. Log in to ArgoCD as a user in the `catalog-admins` group.
2. Attempt to manually Sync the `shopping-cart-product-catalog` application.
3. Verify the operation succeeds without a permission error.
