---
trigger: always_on
---

PROJECT GOAT Development Rules

- Never simplify the architecture.
- Preserve deterministic behavior.
- All models must be immutable.
- All IDs must remain deterministic.
- Preserve canonical hashing and fingerprints.
- Preserve replayability.
- Preserve auditability.
- Never introduce ML, Bayesian methods, LLM reasoning, or probabilistic logic unless explicitly requested.
- Maintain backward compatibility with previous frozen steps.
- Every implementation must include:
  - comprehensive tests
  - SQLite persistence
  - reporting
  - public API exports
  - documentation
- Never modify frozen architecture unless explicitly instructed.
- Run dedicated tests before full regression.
- Do not stop after generating an implementation plan.