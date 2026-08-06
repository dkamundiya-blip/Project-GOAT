# VERSION 1.0 BRANCH PLAN & RELEASE ENGINEERING GUIDE

## 1. VERSION 0.9 RELEASE FREEZE EXECUTION

To complete the formal release freeze of Project GOAT Version 0.9, execute the following exact Git commands:

```bash
# Step 1: Stage all frozen files, documentation, and completion reports
git add .

# Step 2: Commit the Version 0.9 release completion state
git commit -m "RELEASE: Project GOAT Version 0.9 — Master System Integration, Version Certification & Release Freeze"

# Step 3: Create annotated release freeze tags
git tag -a GOAT_v0.9_FROZEN -m "Project GOAT Version 0.9 Officially Certified and Permanently Frozen"
git tag -a v0.9.0 -m "Project GOAT Release Version 0.9.0"

# Step 4: Push commit and release tags to remote repository
git push origin main --tags

# Step 5: Branch out to initialize Version 1.0 feature development
git checkout -b feature/v1.0-dashboard
```

---

## 2. VERSION 1.0 ROADMAP & FEATURE OBJECTIVES

Version 1.0 builds upon the frozen quantitative research foundation of Version 0.9 to introduce live execution infrastructure, broker connectivity, and real-time dashboard UI.

### Key Version 1.0 Objectives
1. **Interactive Real-Time Quantitative Research Dashboard** (`feature/v1.0-dashboard`):
   - Frontend UI connected to Step 9.7 Dashboard Backend.
   - Real-time visualization of microstructure observations, edge candidate discovery, knowledge graph topologies, and research intelligence reports.
2. **Deriv WebSocket & FIX Protocol Connectors**:
   - Production connection to Deriv API streams for live tick data ingestion.
3. **Execution Infrastructure & Risk Engine**:
   - Order execution management system (OEMS), position tracking, and strict risk controls.
4. **Automated Live Strategy Paper-Trading**:
   - Execution of promoted edges in live paper-trading mode.

---

## 3. BRANCHING & DEVELOPMENT RULES FOR VERSION 1.0

- Main branch (`main`) stays anchored to frozen `v0.9.0`.
- All Version 1.0 work takes place in `feature/v1.0-dashboard` and targeted feature branches.
- Version 0.9 code remains immutable and frozen.
