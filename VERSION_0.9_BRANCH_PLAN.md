# PROJECT GOAT — VERSION 0.9 BRANCHING & RELEASE MANAGEMENT PLAN

**Current Release Base**: Version 0.8 (v0.8.0)  
**Frozen Git Release Tag**: `GOAT_v0.8_FROZEN`  
**Plan Date**: 2026-08-01  

---

## 1. Branch Architecture

To protect the immutable baseline of Version 0.8 while enabling Version 0.9 development, the Release Engineering Team specifies the following branching topology:

```
[ main ] ───────────────────────● (GOAT_v0.8_FROZEN / v0.8.0)
                                 \
                                  └────► [ feature/v0.9-deriv-live ] (Version 0.9 Development)
```

| Branch / Tag Name | Purpose / Description | Status |
|---|---|---|
| `main` | Production release branch containing frozen Version 0.8 baseline | **FROZEN & IMMUTABLE** |
| `GOAT_v0.8_FROZEN` | Annotated Git release tag marking final Version 0.8 state | **FROZEN & IMMUTABLE** |
| `v0.8.0` | Semantic version release tag | **FROZEN & IMMUTABLE** |
| `feature/v0.9-deriv-live` | Active development branch for Version 0.9 functionality | **OPEN FOR DEVELOPMENT** |

---

## 2. Immutability & Backport Rules

1. **Version 0.8 Immutability**: The code state under tag `GOAT_v0.8_FROZEN` on branch `main` is strictly immutable. No feature work or refactoring may be committed directly to `main`.
2. **Version 0.9 Isolation**: All Version 0.9 code changes, new broker adapters (Weltrade, Forex), and live network daemon workers MUST be developed exclusively on `feature/v0.9-deriv-live`.
3. **Emergency Patch Policy**: In the rare event that a critical security vulnerability or database corruption bug is discovered in Version 0.8:
   - A dedicated hotfix branch (`hotfix/v0.8.1-patch`) will be branched directly from `GOAT_v0.8_FROZEN`.
   - The patch must pass all 23,210 regression tests.
   - The fix will be tagged as `v0.8.1` and merged back into both `main` and `feature/v0.9-deriv-live`.

---

## 3. Recommended Git Execution Commands

To execute the branching and release tagging operation, the release engineer should run the following commands:

```bash
# 1. Verify working directory cleanliness
git status

# 2. Stage release documentation and metadata
git add .

# 3. Commit Version 0.8 release baseline
git commit -m "Freeze Project GOAT Version 0.8"

# 4. Create annotated Git release tags
git tag -a GOAT_v0.8_FROZEN -m "Project GOAT Version 0.8 - Certified Production Foundation"
git tag -a v0.8.0 -m "Project GOAT Version 0.8"

# 5. Push commits and tags to remote repository
git push origin main
git push origin GOAT_v0.8_FROZEN
git push origin v0.8.0

# 6. Checkout and launch Version 0.9 development branch
git checkout -b feature/v0.9-deriv-live
git push -u origin feature/v0.9-deriv-live
```
