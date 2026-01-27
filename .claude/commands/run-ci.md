---
description: Run local CI/CD checks to ensure code quality before pushing
argument-hint: [fix] (optional: try to auto-fix issues)
---

# Run CI Command

## Instructions

1.  **Identify Project Type & Toolchain**
    - Detect language: Node.js, Python, Rust, Go, etc.
    - Detect tools: ESLint, Prettier, Black, Pytest, Cargo, Maven, Gradle.

2.  **Execute Pipeline Steps**
    - **Step 1: Dependency Check**
        - Ensure all packages are installed.
        - Run audit commands (`npm audit`, `pip audit`) if available.
    - **Step 2: Linting & Formatting**
        - Run linters. If `fix` argument is present, use `--fix` flags.
        - Check formatting.
    - **Step 3: Type Checking**
        - Run `tsc` (TypeScript), `mypy` (Python), etc.
    - **Step 4: Testing**
        - Run unit tests.
        - Run integration tests if feasible locally.
    - **Step 5: Build Check**
        - Attempt a build to ensure no compilation errors (`npm run build`, `cargo build`).

3.  **Error Handling**
    - If any step fails, stop and report the error.
    - Provide suggestions for fixing the error.
    - If `fix` was requested, report which issues were auto-fixed and which require manual intervention.

4.  **Summary**
    - Output a checklist of passed/failed steps.
    - Confirm if the code is safe to push.
