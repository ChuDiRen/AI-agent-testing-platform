---
description: Continuous learning skill to extract patterns from sessions
---

# Continuous Learning Skill

## Overview
This skill allows Claude to "learn" from the current session by extracting successful patterns, reusable code snippets, or important project context and saving them for future sessions.

## Usage
When you identify a valuable pattern or piece of knowledge:
1.  **Extract**: Isolate the core concept or code.
2.  **Generalize**: Remove session-specific details.
3.  **Categorize**: Determine where it belongs (e.g., `skills/`, `rules/`, `docs/`).
4.  **Persist**: Create or update a markdown file in `.claude/knowledge/` or `.claude/skills/`.

## Triggers
- "Remember this for later."
- "This is a good pattern, let's save it."
- "Update the project guidelines with this decision."

## Storage Location
- **Patterns**: `.claude/skills/extracted-patterns/`
- **Rules**: `.claude/rules/learned-rules.md`
- **Knowledge**: `.claude/knowledge/`
