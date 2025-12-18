## 1. Proposal Review
- [x] 1.1 Confirm scope: Android only vs Android+iOS → **Android + iOS**
- [x] 1.2 Confirm Appium connection model: external Appium server vs engine-managed startup → **External (http://127.0.0.1:4723)**
- [x] 1.3 Confirm app launch strategy: app path vs package/activity (Android) / bundleId (iOS) → **app path (Android), bundleId/app (iOS)**

## 2. Implementation (after approval)
- [x] 2.1 Create `mobile-engine/` package structure mirroring `web-engine` (cli/core/parse/extend/utils)
- [x] 2.2 Implement `CasesPlugin` for mobile (pytest options: type/cases/keyDir + appium caps)
- [x] 2.3 Implement `MobileTestRunner` (context → pre_script → steps → post_script → cleanup)
- [x] 2.4 Implement Appium session manager (create/close driver, store in `g_context`)
- [x] 2.5 Implement **70+ keywords** covering all mobile operations (元素操作、等待、断言、设备操作、App管理、Context切换、剪贴板、文件操作、变量操作)
- [x] 2.6 Implement artifacts on failure (screenshot, page source) and Allure attachments
- [x] 2.7 Add examples: 10 YAML case files covering various scenarios

## 3. Packaging & Integration
- [x] 3.1 Add `plugin.yaml` for mobile-engine (params + help)
- [x] 3.2 Add `setup.py` + `requirements.txt` and console entrypoint `mobilerun`
- [x] 3.3 Document configuration and quickstart in `mobile-engine/README.md` (316 lines, full keyword reference)
