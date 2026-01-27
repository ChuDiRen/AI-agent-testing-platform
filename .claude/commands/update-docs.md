---
description: Update project documentation based on recent code changes
argument-hint: [scope] (readme/api/all)
---

# Update Documentation Command

## Instructions

1.  **Analyze Changes**
    - Check `git diff` or recent commits to understand what has changed in the codebase.
    - Identify modified files, added functions, changed APIs, or configuration updates.

2.  **Identify Target Documentation**
    - `README.md`: For high-level project changes, setup instructions, or new features.
    - `CONTRIBUTING.md`: For changes in development workflow.
    - `API.md` / `Swagger` / Docstrings: For API signature changes.
    - `CHANGELOG.md`: If not automatically updated.

3.  **Draft Updates**
    - **README**: Update "Installation", "Usage", or "Features" sections.
    - **Code Comments**: Update function docstrings if logic changed but comments didn't.
    - **API Docs**: reflect new parameters, return types, or endpoints.

4.  **Review & Refine**
    - Ensure documentation is clear, concise, and accurate.
    - Check for broken links or outdated references.
    - Verify formatting (Markdown).

5.  **Apply Changes**
    - Write the updates to the files.
    - (Optional) Create a new branch or commit for documentation updates.
