# 状态管理技能

## 触发条件
- 关键词：状态管理、Store、Pinia、Vuex、Redux、状态
- 场景：当用户需要设计或实现前端状态管理时

## 核心规范

### 规范1：Pinia Store 结构

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import { userApi } from '@/api/user'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const loading = ref(false)
  
  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => user.value?.username ?? '')
  const permissions = computed(() => user.value?.permissions ?? [])
  
  // Actions
  async function login(username: string, password: string) {
    loading.value = true
    try {
      const response = await userApi.login({ username, password })
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('token', token.value)
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    } finally {
      loading.value = false
    }
  }
  
  async function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }
  
  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const response = await userApi.getUserInfo()
      user.value = response.data
    } catch (error) {
      logout()
    }
  }
  
  function hasPermission(permission: string): boolean {
    return permissions.value.includes(permission)
  }
  
  // 初始化
  function init() {
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      token.value = savedToken
      fetchUserInfo()
    }
  }
  
  return {
    // State
    user,
    token,
    loading,
    // Getters
    isLoggedIn,
    username,
    permissions,
    // Actions
    login,
    logout,
    fetchUserInfo,
    hasPermission,
    init,
  }
})
```

### 规范2：Store 目录结构

```
stores/
├── index.ts              # Store 统一导出
├── user.ts               # 用户状态
├── app.ts                # 应用全局状态
├── permission.ts         # 权限状态
└── modules/              # 业务模块状态
    ├── project.ts
    ├── testCase.ts
    └── report.ts
```

```typescript
// stores/index.ts
export { useUserStore } from './user'
export { useAppStore } from './app'
export { usePermissionStore } from './permission'
export { useProjectStore } from './modules/project'
export { useTestCaseStore } from './modules/testCase'
```

### 规范3：应用全局状态

```typescript
// stores/app.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 侧边栏折叠状态
  const sidebarCollapsed = ref(false)
  
  // 主题
  const theme = ref<'light' | 'dark'>('light')
  
  // 语言
  const locale = ref('zh-CN')
  
  // 全局 Loading
  const globalLoading = ref(false)
  
  // Actions
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }
  
  function setTheme(newTheme: 'light' | 'dark') {
    theme.value = newTheme
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('theme', newTheme)
  }
  
  function setLocale(newLocale: string) {
    locale.value = newLocale
    localStorage.setItem('locale', newLocale)
  }
  
  function init() {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark'
    if (savedTheme) setTheme(savedTheme)
    
    const savedLocale = localStorage.getItem('locale')
    if (savedLocale) locale.value = savedLocale
  }
  
  return {
    sidebarCollapsed,
    theme,
    locale,
    globalLoading,
    toggleSidebar,
    setTheme,
    setLocale,
    init,
  }
})
```

### 规范4：业务模块状态

```typescript
// stores/modules/testCase.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TestCase, TestCaseQuery } from '@/types'
import { testCaseApi } from '@/api/testCase'

export const useTestCaseStore = defineStore('testCase', () => {
  // State
  const list = ref<TestCase[]>([])
  const total = ref(0)
  const current = ref<TestCase | null>(null)
  const loading = ref(false)
  const query = ref<TestCaseQuery>({
    page: 1,
    pageSize: 20,
    keyword: '',
    status: undefined,
  })
  
  // Getters
  const isEmpty = computed(() => list.value.length === 0)
  const pageCount = computed(() => Math.ceil(total.value / query.value.pageSize))
  
  // Actions
  async function fetchList() {
    loading.value = true
    try {
      const response = await testCaseApi.getList(query.value)
      list.value = response.data.items
      total.value = response.data.total
    } finally {
      loading.value = false
    }
  }
  
  async function fetchById(id: number) {
    loading.value = true
    try {
      const response = await testCaseApi.getById(id)
      current.value = response.data
      return response.data
    } finally {
      loading.value = false
    }
  }
  
  async function create(data: Partial<TestCase>) {
    const response = await testCaseApi.create(data)
    await fetchList() // 刷新列表
    return response.data
  }
  
  async function update(id: number, data: Partial<TestCase>) {
    const response = await testCaseApi.update(id, data)
    // 更新列表中的数据
    const index = list.value.findIndex(item => item.id === id)
    if (index !== -1) {
      list.value[index] = response.data
    }
    if (current.value?.id === id) {
      current.value = response.data
    }
    return response.data
  }
  
  async function remove(id: number) {
    await testCaseApi.delete(id)
    list.value = list.value.filter(item => item.id !== id)
    total.value -= 1
  }
  
  function setQuery(newQuery: Partial<TestCaseQuery>) {
    query.value = { ...query.value, ...newQuery }
  }
  
  function resetQuery() {
    query.value = {
      page: 1,
      pageSize: 20,
      keyword: '',
      status: undefined,
    }
  }
  
  return {
    list,
    total,
    current,
    loading,
    query,
    isEmpty,
    pageCount,
    fetchList,
    fetchById,
    create,
    update,
    remove,
    setQuery,
    resetQuery,
  }
})
```

### 规范5：Store 持久化

```typescript
// stores/plugins/persist.ts
import type { PiniaPluginContext } from 'pinia'

export function persistPlugin({ store }: PiniaPluginContext) {
  // 需要持久化的 store
  const persistStores = ['user', 'app']
  
  if (!persistStores.includes(store.$id)) return
  
  // 从 localStorage 恢复状态
  const savedState = localStorage.getItem(`pinia-${store.$id}`)
  if (savedState) {
    store.$patch(JSON.parse(savedState))
  }
  
  // 监听状态变化并保存
  store.$subscribe((mutation, state) => {
    localStorage.setItem(`pinia-${store.$id}`, JSON.stringify(state))
  })
}

// main.ts
import { createPinia } from 'pinia'
import { persistPlugin } from './stores/plugins/persist'

const pinia = createPinia()
pinia.use(persistPlugin)
```

### 规范6：组件中使用 Store

```vue
<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useUserStore, useTestCaseStore } from '@/stores'

// 获取 store 实例
const userStore = useUserStore()
const testCaseStore = useTestCaseStore()

// 使用 storeToRefs 保持响应性
const { user, isLoggedIn } = storeToRefs(userStore)
const { list, loading, query } = storeToRefs(testCaseStore)

// 直接解构 actions（不需要 storeToRefs）
const { login, logout } = userStore
const { fetchList, setQuery } = testCaseStore

// 初始化加载数据
onMounted(() => {
  fetchList()
})

// 搜索
function handleSearch(keyword: string) {
  setQuery({ keyword, page: 1 })
  fetchList()
}
</script>
```

### 规范7：Store 测试

```typescript
// stores/__tests__/user.test.ts
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../user'
import { vi, describe, it, expect, beforeEach } from 'vitest'

vi.mock('@/api/user', () => ({
  userApi: {
    login: vi.fn(),
    getUserInfo: vi.fn(),
  }
}))

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('should login successfully', async () => {
    const store = useUserStore()
    
    vi.mocked(userApi.login).mockResolvedValue({
      data: {
        token: 'test-token',
        user: { id: 1, username: 'admin' }
      }
    })
    
    const result = await store.login('admin', 'password')
    
    expect(result).toBe(true)
    expect(store.token).toBe('test-token')
    expect(store.isLoggedIn).toBe(true)
  })
  
  it('should logout correctly', () => {
    const store = useUserStore()
    store.token = 'test-token'
    store.user = { id: 1, username: 'admin' }
    
    store.logout()
    
    expect(store.token).toBe('')
    expect(store.user).toBeNull()
    expect(store.isLoggedIn).toBe(false)
  })
})
```

## 禁止事项
- ❌ 在组件中直接修改 store state
- ❌ 在 store 中存储大量临时数据
- ❌ 不使用 storeToRefs 解构响应式数据
- ❌ 在 store 中处理 UI 逻辑
- ❌ 循环依赖 store

## 检查清单
- [ ] Store 是否按功能模块划分
- [ ] State 是否只包含必要数据
- [ ] Actions 是否处理了错误
- [ ] 是否配置了持久化
- [ ] 是否编写了单元测试
