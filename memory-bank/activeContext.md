# Active Context: Product Catalog Service

## Current Status (2026-05-27)
**feature/v1.5.0 Milestone: Initialization**
The product seed race condition has been resolved in v1.4.0. Focus now shifts to the v1.5.0 milestone tasks.

## Recent Changes
- **v1.4.0 SHIPPED:** Added \`initContainer\` wait to \`seed-job.yaml\` to resolve race condition between table creation and seeding.
- **Branch Created:** \`feature/v1.5.0\` for the next development cycle.

## Next Steps
- Implement integration tests using Testcontainers (as noted in gaps).
- Initialize Alembic for database migration management.

## Agent Instructions
(Existing rules preserved...)
1. **CI only** — do NOT run \`pytest\` or \`mypy\` locally without activating the virtualenv.
2. **Memory-bank discipline** — do NOT update \`memory-bank/activeContext.md\` until CI shows \`completed success\`.
3. **SHA verification** — verify commit SHA with \`gh api repos/wilddog64/shopping-cart-product-catalog/commits/<sha>\` before reporting.
4. **Do NOT merge PRs** — open the PR and stop.
5. **No unsolicited changes** — flat structure is intentional, do not refactor to services/repositories.
