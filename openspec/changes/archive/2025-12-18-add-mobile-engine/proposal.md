# Change: Add Mobile Execution Engine (Appium-based)

## Why
The platform currently provides a `web-engine` that executes keyword-driven and data-driven cases (YAML/Excel) using a driver abstraction (Playwright) and a unified execution lifecycle (context → pre_script → steps → post_script → artifacts/reporting). There is no equivalent execution engine for real mobile apps.

Adding a `mobile-engine` enables automated execution against Android/iOS apps via Appium (WebDriver protocol), aligning with the same case format and runner model as `web-engine`.

## What Changes
- Add a new plugin module `mobile-engine` providing a CLI command (planned: `mobilerun`) similar to `webrun`.
- Implement an Appium-backed driver/session manager.
- Implement a keyword set analogous to `webrun.extend.keywords.Keywords`, but for mobile actions.
- Support the same test lifecycle and case structure as `web-engine`:
  - load `context.yaml`
  - render variables via Jinja2
  - execute `pre_script`/`post_script`
  - execute `steps` that call keywords
  - generate artifacts (screenshots on error; optional page source dumps)
- Provide a minimal set of core mobile keywords for MVP:
  - `open_app` / `close_app`
  - `tap_element`
  - `input_text`
  - `wait_for_element`
  - `swipe`
  - `back`
  - `take_screenshot`
  - `assert_element_visible`

## Impact
- Affected specs:
  - New capability spec: `mobile-engine`
- Affected code:
  - New package under repo root: `mobile-engine/` (Python package + plugin.yaml + setup/requirements)
  - No changes required to `web-engine`
- Non-goals (initial MVP):
  - Replacing `web-engine` architecture
  - Full parity with all `web-engine` keywords
  - Natural-language agent execution like `mobile-use` (may be added later as an extension layer)

## Open Questions (need your confirmation)
- Target platforms:
  - Android only, or Android + iOS?
- Driver choices:
  - Android: `uiautomator2` (default?)
  - iOS: `xcuitest` (if iOS is in scope)
- Connection model:
  - Do you already run an external Appium server (`http://127.0.0.1:4723`), or should the engine manage starting it?
- App launch parameters:
  - Android: `appPackage`/`appActivity` vs `app` (apk path)
  - iOS: `bundleId` vs `app` (ipa path)
