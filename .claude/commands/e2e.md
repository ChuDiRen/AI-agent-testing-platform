---
description: Run End-to-End tests or generate them
argument-hint: [url or scenario]
---

# E2E Command

## Instructions

1.  **Check Playwright/Cypress Setup**
    - Verify if an E2E framework is installed.
    - If not, offer to install Playwright.

2.  **Generate Test**
    - Based on the scenario, write a new E2E test file.
    - Use `codegeneration` capabilities to infer selectors.

3.  **Run Test**
    - Execute the test in headless mode.
    - Report results.
    - If failed, capture screenshots/traces (if configured).
