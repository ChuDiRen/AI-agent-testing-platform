---
description: Interactive guide to the Intelligent Development Closed Loop
argument-hint: [phase]
---

# Dev Loop Command

## Overview
This command acts as the central orchestrator for the development workflow, guiding you through the 6-stage closed loop.

## Usage
`CLAUDE.md` command: `/dev-loop [phase]`

## Phases
1.  **Plan**: Start a new feature or task.
2.  **Dev**: Write code and tests.
3.  **Verify**: Run CI and checks.
4.  **Review**: Analyze code and PRs.
5.  **Deploy**: Commit and release.
6.  **Learn**: Retrospective and memory update.

## Workflow Logic

### Phase 1: Plan
- Suggest running `/feature-dev` for new features.
- Suggest `/plan` for smaller tasks.
- Check if `task_plan.md` exists.

### Phase 2: Dev
- Suggest `/tdd` for implementation.
- Remind about `security-guidance`.

### Phase 3: Verify
- Run `/verify` (lint, type-check, test).
- Run `/e2e` if applicable.

### Phase 4: Review
- Run `/code-review` for local changes.
- Suggest `/pr-review-toolkit:review-pr` if on a PR branch.

### Phase 5: Deploy
- Run `/commit-push-pr` to ship.
- Run `/deploy` for deployment.

### Phase 6: Learn
- Run `/learn` to extract session patterns.
- Prompt to save new terms/rules to Core Memory.

## Example
User: `/dev-loop plan`
Agent: "Starting Planning Phase. Let's define the scope. Running /feature-dev..."
