---
description: Manual context compaction and memory management
---

# Strategic Compact Skill

## Overview
Techniques to manage the LLM's context window effectively, ensuring long-running sessions remain coherent and efficient.

## Strategies

### 1. Summarize & Forget
- **Trigger**: Context usage > 70% or changing topics.
- **Action**: Summarize the completed task or conversation segment.
- **Command**: "Summarize what we've done so far regarding X, then let's clear the history/context of those details." (Note: Actual context clearing depends on tool capabilities, but summarization helps).

### 2. Documentation as Memory
- **Trigger**: Key decisions made or patterns discovered.
- **Action**: Write them to `docs/` or `.claude/knowledge/`.
- **Benefit**: Allows the model to "forget" the conversation but "remember" the outcome by reading the doc later.

### 3. File-Based Context
- **Trigger**: Working on a large set of files.
- **Action**: Instead of reading all files constantly, create a `context.md` that contains only the *signatures* or *interfaces* of the modules, not the implementation.

### 4. Checkpoint
- **Trigger**: Major milestone reached.
- **Action**: Use `/checkpoint` command to save state, then potentially restart the session if the tool allows, reloading only the checkpoint summary.
