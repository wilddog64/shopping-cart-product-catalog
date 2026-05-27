# Active Context: Product Catalog Service

## Current Status (2026-05-27)
**fix/seed-job-race-condition IN PROGRESS**
Resolving a race condition where the product-catalog-seed job fails because it starts before the application pod has finished creating the database tables.

## Recent Changes
- **Added initContainer to seed-job.yaml:** The job now waits for \`http://product-catalog:8080/health\` to return a successful response before starting the seed process. This ensures SQLAlchemy \`create_all()\` has completed.

## Active Task
- **Fix Seed Race Condition:** Add wait-for-service initContainer to \`k8s/base/seed-job.yaml\`.

## Agent Instructions
(Existing rules preserved...)
1. **CI only** — do NOT run \`pytest\` or \`mypy\` locally without activating the virtualenv.
2. **Memory-bank discipline** — do NOT update \`memory-bank/activeContext.md\` until CI shows \`completed success\`.
3. **SHA verification** — verify commit SHA with \`gh api repos/wilddog64/shopping-cart-product-catalog/commits/<sha>\` before reporting.
4. **Do NOT merge PRs** — open the PR and stop.
5. **No unsolicited changes** — flat structure is intentional, do not refactor to services/repositories.
