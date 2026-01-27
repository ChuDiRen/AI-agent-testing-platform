---
description: Run the verification loop to ensure system stability
argument-hint: [scope] (all/fast/full)
---

# Verify Command

## Instructions

1.  **Determine Scope**
    - `fast`: Linters + Unit Tests only.
    - `full`: Linters + Unit Tests + Integration + E2E.
    - `all`: All of the above + Security Audit.

2.  **Execute Stages**
    - **Stage 1: Static Analysis** (`npm run lint`, `tsc`, etc.)
    - **Stage 2: Unit Tests** (`npm test`)
    - **Stage 3: Integration/E2E** (if `full` or `all`)
    - **Stage 4: Security** (if `all` - invoke `security-reviewer` agent)

3.  **Report**
    - Generate a summary report.
    - 🟢 PASS: All checks passed.
    - 🔴 FAIL: List specific failures.

4.  **Auto-Correct (Optional)**
    - If trivial errors (linting), attempt to fix and re-run.
