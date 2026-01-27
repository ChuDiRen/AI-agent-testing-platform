---
description: Extract patterns and knowledge from the current session
argument-hint: [pattern/topic]
---

# Learn Command

## Instructions

1.  **Analyze Session History**
    - Review the recent interactions, code changes, and decisions.
    - Look for:
        - Recurring bug fixes.
        - New architectural patterns used.
        - User preferences (e.g., naming conventions).

2.  **Extract Knowledge**
    - Formulate the knowledge into a clear rule or guide.
    - Example: "When using Library X, always initialize it with Y."

3.  **Persist**
    - **If it's a Rule**: Update `.claude/rules/learned-rules.md`.
    - **If it's a Skill**: Create a new skill in `.claude/skills/`.
    - **If it's Project Info**: Update `README.md` or `docs/`.

4.  **Confirm**
    - Tell the user what was learned and where it was saved.
