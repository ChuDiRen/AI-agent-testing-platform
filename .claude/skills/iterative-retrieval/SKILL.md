---
description: Progressive context refinement for subagents
---

# Iterative Retrieval Skill

## Overview
A pattern for efficiently gathering context when the solution space is large or unknown. Instead of dumping all files, the agent searches iteratively.

## Workflow

### 1. Broad Search (Scout)
- **Action**: Use `SearchCodebase` or `WebSearch` with high-level keywords.
- **Goal**: Identify candidate files, libraries, or concepts.
- **Output**: A list of potential targets.

### 2. Deep Dive (Probe)
- **Action**: Read the specific files identified in Step 1.
- **Goal**: Understand implementation details and dependencies.
- **Refinement**: If the file is not relevant, discard and go back to the list.

### 3. Trace (Follow)
- **Action**: Follow imports, function calls, and references.
- **Goal**: Build a mental graph of the relevant subsystem.

### 4. Synthesize
- **Action**: Summarize findings into a coherent context block.
- **Usage**: Pass this refined context to the next agent (e.g., Implementer or Architect).

## When to Use
- Understanding a new codebase.
- Debugging complex errors with unknown origins.
- Planning features that touch multiple modules.
