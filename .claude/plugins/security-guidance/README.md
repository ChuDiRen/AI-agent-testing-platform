# Security Guidance

## Overview
Security reminder hook that warns about potential security issues when editing files.

## Components
- **Hook**: `PreToolUse`
  - Monitors 9 security patterns including:
    - Command injection
    - XSS
    - Eval usage
    - Dangerous HTML
    - Pickle deserialization
    - `os.system` calls

## Usage
This plugin works automatically. You will see warnings if you attempt to edit files with insecure patterns.
