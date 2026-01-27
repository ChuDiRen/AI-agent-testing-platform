---
description: Continuous verification loop for high-reliability development
---

# Verification Loop Skill

## Overview
A systematic approach to verifying code changes using multiple layers of feedback.

## Process

### 1. Static Analysis
- Run linters (ESLint, Pylint).
- Run type checkers (TypeScript, MyPy).
- **Action**: Fix all warnings and errors.

### 2. Unit Testing
- Run relevant unit tests.
- **Action**: Ensure 100% pass rate for touched files.

### 3. Integration/E2E Testing
- Run critical integration paths.
- **Action**: Verify system stability.

### 4. Self-Correction
- If any step fails, analyze the error log.
- Apply a fix.
- Restart the loop from Step 1.

### 5. Final Sign-off
- Only when all steps pass, mark the task as verified.
