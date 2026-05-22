# Retrospective — OIDC Issuer Fix

**Date:** 2026-05-22
**PR:** #21 — merged to main (`e9872e101f4658de2dd113913bce30de395a2988`)
**Participants:** Claude, Copilot

## What Went Well
- Copilot caught the missing pod rollout trigger (configmap checksum)
- configMapGenerator implemented for automatic rolling restarts
- Product-catalog OIDC configuration cleanly aligned with external Keycloak issuer

## What Went Wrong
- Initial fix set both oauth2.issuer-uri and jwk-set-uri to external URL; only issuer-uri needs to be external

## Process Notes
- When fixing OIDC issuer mismatches: issuer-uri must match KC_HOSTNAME_URL (external); jwk-set-uri should stay internal
- ConfigMap changes with envFrom do not trigger pod restarts — use configMapGenerator or checksum annotation

## Theme
Fixed Keycloak OIDC issuer URL mismatch in product-catalog service. KC_HOSTNAME_STRICT=true means Keycloak always advertises the external domain as issuer; all OIDC clients must match. Also improved rollout automation via Kustomize configMapGenerator.
