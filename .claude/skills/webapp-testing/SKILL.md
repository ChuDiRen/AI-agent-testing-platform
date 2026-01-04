# Web 应用测试技能

## 触发条件
- 关键词：E2E测试、端到端测试、Playwright、Cypress、浏览器测试、UI测试
- 场景：当用户需要进行 Web 应用端到端测试时

## 核心规范

### 规范1：Playwright 项目结构

```
e2e/
├── playwright.config.ts     # Playwright 配置
├── tests/                   # 测试文件
│   ├── auth/
│   │   └── login.spec.ts
│   ├── users/
│   │   └── user-management.spec.ts
│   └── common/
│       └── navigation.spec.ts
├── fixtures/                # 测试 fixtures
│   └── auth.fixture.ts
├── pages/                   # Page Object Models
│   ├── login.page.ts
│   ├── dashboard.page.ts
│   └── users.page.ts
└── utils/                   # 工具函数
    └── helpers.ts
```

### 规范2：Playwright 配置

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }]
  ],
  
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
})
```

### 规范3：Page Object Model

```typescript
// pages/login.page.ts
import { Page, Locator, expect } from '@playwright/test'

export class LoginPage {
  readonly page: Page
  readonly usernameInput: Locator
  readonly passwordInput: Locator
  readonly loginButton: Locator
  readonly errorMessage: Locator

  constructor(page: Page) {
    this.page = page
    this.usernameInput = page.getByPlaceholder('用户名')
    this.passwordInput = page.getByPlaceholder('密码')
    this.loginButton = page.getByRole('button', { name: '登录' })
    this.errorMessage = page.locator('.error-message')
  }

  async goto() {
    await this.page.goto('/login')
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username)
    await this.passwordInput.fill(password)
    await this.loginButton.click()
  }

  async expectErrorMessage(message: string) {
    await expect(this.errorMessage).toContainText(message)
  }

  async expectLoginSuccess() {
    await expect(this.page).toHaveURL('/dashboard')
  }
}

// pages/users.page.ts
export class UsersPage {
  readonly page: Page
  readonly searchInput: Locator
  readonly addButton: Locator
  readonly userTable: Locator

  constructor(page: Page) {
    this.page = page
    this.searchInput = page.getByPlaceholder('搜索用户')
    this.addButton = page.getByRole('button', { name: '新增' })
    this.userTable = page.locator('.user-table')
  }

  async goto() {
    await this.page.goto('/users')
  }

  async search(keyword: string) {
    await this.searchInput.fill(keyword)
    await this.searchInput.press('Enter')
  }

  async clickAdd() {
    await this.addButton.click()
  }

  async getUserRow(username: string) {
    return this.userTable.locator('tr', { hasText: username })
  }

  async deleteUser(username: string) {
    const row = await this.getUserRow(username)
    await row.getByRole('button', { name: '删除' }).click()
    await this.page.getByRole('button', { name: '确认' }).click()
  }
}
```

### 规范4：测试用例编写

```typescript
// tests/auth/login.spec.ts
import { test, expect } from '@playwright/test'
import { LoginPage } from '../../pages/login.page'

test.describe('登录功能', () => {
  let loginPage: LoginPage

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page)
    await loginPage.goto()
  })

  test('使用正确的凭证登录成功', async ({ page }) => {
    await loginPage.login('admin', 'admin123')
    await loginPage.expectLoginSuccess()
    
    // 验证登录后的状态
    await expect(page.getByText('欢迎回来')).toBeVisible()
  })

  test('使用错误的密码登录失败', async () => {
    await loginPage.login('admin', 'wrongpassword')
    await loginPage.expectErrorMessage('用户名或密码错误')
  })

  test('空用户名提交显示验证错误', async ({ page }) => {
    await loginPage.login('', 'password')
    await expect(page.getByText('请输入用户名')).toBeVisible()
  })

  test('记住我功能', async ({ page, context }) => {
    // 勾选记住我
    await page.getByLabel('记住我').check()
    await loginPage.login('admin', 'admin123')
    
    // 关闭页面后重新打开
    await page.close()
    const newPage = await context.newPage()
    await newPage.goto('/dashboard')
    
    // 应该仍然保持登录状态
    await expect(newPage).toHaveURL('/dashboard')
  })
})
```

### 规范5：测试 Fixtures

```typescript
// fixtures/auth.fixture.ts
import { test as base, expect } from '@playwright/test'
import { LoginPage } from '../pages/login.page'

type AuthFixtures = {
  loginPage: LoginPage
  authenticatedPage: void
}

export const test = base.extend<AuthFixtures>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page)
    await use(loginPage)
  },

  authenticatedPage: async ({ page }, use) => {
    // 登录
    const loginPage = new LoginPage(page)
    await loginPage.goto()
    await loginPage.login('admin', 'admin123')
    await expect(page).toHaveURL('/dashboard')
    
    await use()
  },
})

export { expect }

// 使用 fixture
// tests/users/user-management.spec.ts
import { test, expect } from '../../fixtures/auth.fixture'
import { UsersPage } from '../../pages/users.page'

test.describe('用户管理', () => {
  test.beforeEach(async ({ authenticatedPage }) => {
    // 已自动登录
  })

  test('显示用户列表', async ({ page }) => {
    const usersPage = new UsersPage(page)
    await usersPage.goto()
    
    await expect(usersPage.userTable).toBeVisible()
  })
})
```

### 规范6：API Mock

```typescript
// tests/with-mock.spec.ts
import { test, expect } from '@playwright/test'

test.describe('使用 API Mock', () => {
  test('Mock API 响应', async ({ page }) => {
    // Mock API 响应
    await page.route('**/api/users', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 0,
          data: [
            { id: 1, username: 'user1', email: 'user1@example.com' },
            { id: 2, username: 'user2', email: 'user2@example.com' },
          ]
        })
      })
    })

    await page.goto('/users')
    
    // 验证 Mock 数据显示
    await expect(page.getByText('user1')).toBeVisible()
    await expect(page.getByText('user2')).toBeVisible()
  })

  test('Mock 网络错误', async ({ page }) => {
    await page.route('**/api/users', route => route.abort())
    
    await page.goto('/users')
    
    await expect(page.getByText('网络错误')).toBeVisible()
  })

  test('Mock 延迟响应', async ({ page }) => {
    await page.route('**/api/users', async route => {
      await new Promise(resolve => setTimeout(resolve, 2000))
      await route.fulfill({
        status: 200,
        body: JSON.stringify({ code: 0, data: [] })
      })
    })

    await page.goto('/users')
    
    // 验证 loading 状态
    await expect(page.getByText('加载中')).toBeVisible()
  })
})
```

### 规范7：视觉回归测试

```typescript
// tests/visual/snapshot.spec.ts
import { test, expect } from '@playwright/test'

test.describe('视觉回归测试', () => {
  test('登录页面截图对比', async ({ page }) => {
    await page.goto('/login')
    
    // 等待页面稳定
    await page.waitForLoadState('networkidle')
    
    // 截图对比
    await expect(page).toHaveScreenshot('login-page.png', {
      maxDiffPixels: 100,
    })
  })

  test('组件截图对比', async ({ page }) => {
    await page.goto('/components')
    
    const button = page.getByRole('button', { name: '主要按钮' })
    await expect(button).toHaveScreenshot('primary-button.png')
  })

  test('全页面截图', async ({ page }) => {
    await page.goto('/dashboard')
    
    await expect(page).toHaveScreenshot('dashboard-full.png', {
      fullPage: true,
    })
  })
})
```

### 规范8：常用命令

```bash
# 运行所有测试
npx playwright test

# 运行特定测试文件
npx playwright test tests/auth/login.spec.ts

# 运行带标签的测试
npx playwright test --grep @smoke

# 使用 UI 模式
npx playwright test --ui

# 调试模式
npx playwright test --debug

# 生成测试代码
npx playwright codegen http://localhost:5173

# 查看测试报告
npx playwright show-report

# 更新截图快照
npx playwright test --update-snapshots
```

## 禁止事项
- ❌ 测试依赖特定数据
- ❌ 使用不稳定的选择器
- ❌ 硬编码等待时间
- ❌ 测试之间有依赖
- ❌ 忽略测试隔离

## 检查清单
- [ ] 是否使用 Page Object 模式
- [ ] 是否使用稳定的选择器
- [ ] 是否处理了异步等待
- [ ] 是否有测试数据清理
- [ ] 是否覆盖了主要用户流程
