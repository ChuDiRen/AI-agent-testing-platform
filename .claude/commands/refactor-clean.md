---
description: Identify and remove dead code and technical debt
argument-hint: [target path]
---

# Refactor-Clean Command

## Instructions

1.  **Invoke Refactor Cleaner Agent**
    - Delegate the task to the `refactor-cleaner` agent.

2.  **Scan Target**
    - Analyze the specified path (or whole project if empty) for:
        - Unused exports.
        - Unused variables.
        - Commented-out code blocks.
        - console.log statements (except in CLI tools).

3.  **Propose Changes**
    - List the items to be removed/cleaned.
    - Ask for user approval (unless `Force` flag is simulated).

4.  **Execute & Verify**
    - Delete/Refactor.
    - Run `verify` command to ensure no breakage.
