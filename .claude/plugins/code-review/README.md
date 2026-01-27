# Code Review Plugin

## Overview
Automated PR code review using multiple specialized agents with confidence-based scoring to filter false positives.

## Components
- **Command**: `/code-review`
- **Agents**: 5 parallel Sonnet agents
  - CLAUDE.md compliance
  - Bug detection
  - Historical context
  - PR history
  - Code comments

## Usage
Run `/code-review` to start the automated review process.
