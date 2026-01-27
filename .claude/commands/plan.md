---
description: Create a comprehensive implementation plan
argument-hint: [goal]
---

# Plan Command

## Instructions

1.  **Invoke Planner Agent**
    - Use the `planner` agent to analyze the goal.
    - *Note: If agent delegation is not available, simulate the planner persona.*

2.  **Generate Plan**
    - Create a detailed step-by-step plan.
    - Save it to `docs/plans/current-plan.md` (create directory if needed).

3.  **Review Plan**
    - Present the plan to the user.
    - Ask for confirmation or adjustments.

4.  **Initialize Progress Tracking**
    - Create a checklist in the plan file to track status.
