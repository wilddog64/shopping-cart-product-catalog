# Defer Python runtime major bumps in Dependabot

**Repo:** shopping-cart-product-catalog
**File:** `.github/dependabot.yml`
**Date:** 2026-08-03

## Problem
The weekly Dependabot run opened `python 3.11-slim → 3.14-slim` (PRs #37, #40). Python 3.14
is bleeding-edge; moving the production base image there needs deliberate testing, not an
auto-merge. GitHub Actions and pip minor/patch continue to flow.

## Decision (2026-08-03)
Defer the docker `python` / `library/python` **major** bump via `ignore` rules; stay on the
3.11 line. Close #37 and #40. Consistent with the frontend policy of deferring runtime majors
(each taken deliberately, one migration at a time). GitHub Actions majors are merged separately.

## Change — `.github/dependabot.yml` (docker ecosystem)
Add under the docker block:
```yaml
    ignore:
      - dependency-name: "python"
        update-types: ["version-update:semver-major"]
      - dependency-name: "library/python"
        update-types: ["version-update:semver-major"]
```

## Definition of Done
- [ ] Dependabot config check green on the PR
- [ ] After merge: `@dependabot close` on #37 and #40
