---
description: E2E（端到端）测试命令
---

# 命令：test-e2e

## 功能描述

使用Playwright进行端到端自动化测试，验证前端功能的完整性和用户体验。

## 使用方式

```
/test-e2e
```

或

```
/test-e2e <页面或功能描述>
```

## 参数说明

- `--page=PageName` - 测试指定页面
- `--scenario=ScenarioName` - 测试指定场景
- `--headed` - 显示浏览器界面（无头模式默认）
- `--slow-mo=1000` - 减慢操作速度（毫秒）
- `--screenshot` - 截图保存
- `--video` - 录制视频
- `--trace` - 记录trace
- `--report=html` - 生成HTML报告

## 执行流程

1. **测试准备**：
   - 启动本地开发服务器
   - 确认应用可访问
   - 准备测试数据

2. **场景识别**：
   - 识别用户场景
   - 设计测试路径
   - 定义验证点

3. **测试编写**：
   - 使用Playwright API
   - 模拟用户操作
   - 验证页面元素
   - 检查数据变化

4. **测试执行**：
   - 启动浏览器
   - 执行测试步骤
   - 截图/录制（可选）
   - 收集测试数据

5. **报告生成**：
   - 生成测试报告
   - 包含截图/视频
   - 标注失败步骤

## 测试场景结构

```typescript
// e2e/tests/user-flow.spec.ts
import { test, expect } from '@playwright/test';

test.describe('用户注册登录流程', () => {
  test('用户成功注册并登录', async ({ page }) => {
    // 1. 访问首页
    await page.goto('http://localhost:5173');

    // 2. 点击注册按钮
    await page.click('text=注册');

    // 3. 填写注册表单
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');

    // 4. 提交表单
    await page.click('button[type="submit"]');

    // 5. 验证跳转到首页
    await expect(page).toHaveURL('http://localhost:5173/home');
    await expect(page.locator('text=欢迎, testuser')).toBeVisible();
  });

  test('使用错误密码登录失败', async ({ page }) => {
    // 登录操作
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // 验证错误提示
    await expect(page.locator('.error-message'))
      .toHaveText('用户名或密码错误');
  });
});
```

## 测试用例模板

```typescript
// e2e/tests/product-flow.spec.ts
test.describe('商品浏览流程', () => {
  test('浏览商品列表', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // 验证商品列表加载
    await expect(page.locator('.product-card')).toHaveCount(10);
  });

  test('查看商品详情', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // 点击第一个商品
    await page.click('.product-card:first-child');

    // 验证商品详情页
    await expect(page).toHaveURL(/\/product\/\d+/);
    await expect(page.locator('.product-title')).toBeVisible();
    await expect(page.locator('.product-price')).toBeVisible();
  });

  test('搜索商品', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // 输入搜索关键词
    await page.fill('input[placeholder="搜索商品"]', '手机');

    // 点击搜索按钮
    await page.click('button:has-text("搜索")');

    // 验证搜索结果
    await expect(page.locator('.product-card')).toHaveCount.gt(0);
    await expect(page.locator('.product-card:first-child'))
      .toContainText('手机');
  });
});
```

## 输出格式

### 终端输出

```markdown
【E2E测试执行中...】

==================== 测试开始 ====================

浏览器：Chromium
测试环境：http://localhost:5173
测试模式：无头模式

==================== 测试场景 ====================

场景1：用户注册登录流程
  ✅ 用户成功注册并登录 (3.2s)
  ✅ 使用错误密码登录失败 (2.1s)

场景2：商品浏览流程
  ✅ 浏览商品列表 (1.5s)
  ✅ 查看商品详情 (2.3s)
  ✅ 搜索商品 (2.8s)

场景3：购物车操作
  ✅ 添加商品到购物车 (1.8s)
  ✅ 查看购物车 (1.2s)
  ❌ 修改商品数量失败 (1.5s)

==================== 测试统计 ====================

总计：8
通过：7
失败：1
通过率：87.5%
执行时间：15.4秒

==================== 报告生成 ====================

HTML报告：e2e/reports/e2e-report.html
截图：e2e/screenshots/
视频：e2e/videos/
Trace：e2e/traces/
```

### 失败分析

```markdown
【失败场景分析】

场景：修改商品数量失败
失败步骤：点击商品数量加号
错误信息：Selector .quantity-plus not found

截图已保存：e2e/screenshots/quantity-plus-not-found.png
Trace文件：e2e/traces/quantity-plus-failure.zip

修复建议：
1. 检查页面上是否存在 .quantity-plus 选择器
2. 确认购物车页面是否正确加载
3. 检查DOM结构是否与预期一致
4. 使用Page Developer Tools检查实际元素选择器
```

## 相关文件

```
e2e/
├── tests/              # 测试用例
│   ├── auth-flow.spec.ts
│   ├── product-flow.spec.ts
│   └── cart-flow.spec.ts
├── fixtures/           # 测试数据
├── pages/              # 页面对象模型（可选）
├── reports/            # 测试报告
├── screenshots/        # 截图
├── videos/            # 视频
└── traces/            # Trace文件
```

## 示例

```
/test-e2e --scenario=购物车 --headed --screenshot --video
```

```
/test-e2e --page=ProductDetail
```

## 相关命令

- `/develop-frontend` - 前端开发
- `/test-api` - API测试
- `/deploy` - 部署
