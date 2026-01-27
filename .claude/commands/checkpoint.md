---
description: Save current verification state as a checkpoint
argument-hint: [message]
---

# Checkpoint Command

## Instructions

1.  **Run Verification**
    - Run `run-ci` or equivalent checks.
    - Ensure the system is in a stable state.

2.  **Git Tag/Commit**
    - Create a specific commit or tag marking this checkpoint.
    - Format: `checkpoint: [message]` or `chk-[timestamp]`.

3.  **Save Context**
    - (Optional) Save current open files list or active task context to `.claude/checkpoints/`.

4.  **Notify**
    - Confirm checkpoint saved.
