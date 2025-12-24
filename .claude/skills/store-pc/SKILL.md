# PC 端状态管理技能

## 触发条件
- 关键词：Vuex、状态管理、store、state、全局状态
- 场景：当用户需要管理 Vue 应用的全局状态时

## 核心规范

### 规范1：本项目 Vuex 结构

```
src/store/
└── index.js          # Vuex store 定义
```

### 规范2：现有 Store 结构

```javascript
// src/store/index.js
import { createStore } from 'vuex'

const store = createStore({
    state() {
        return {
            asideWidth: '250px',      // 侧边栏宽度
            theme: 'light',           // 主题模式
            userInfo: null,           // 用户信息
            roles: [],                // 用户角色
            permissions: [],          // 用户权限
            menuTree: []              // 用户菜单树
        }
    },
    mutations: {
        // 同步修改 state
        setUserInfo(state, userInfo) {
            state.userInfo = userInfo
        },
        setRoles(state, roles) {
            state.roles = roles
        },
        setPermissions(state, permissions) {
            state.permissions = permissions
        },
        setMenuTree(state, menuTree) {
            state.menuTree = menuTree
        },
        clearUserInfo(state) {
            state.userInfo = null
            state.roles = []
            state.permissions = []
            state.menuTree = []
        }
    },
    actions: {
        // 异步操作
        logout({ commit }) {
            commit('clearUserInfo')
            localStorage.removeItem('token')
        }
    },
    getters: {
        // 计算属性
        hasPermission: (state) => (perm) => {
            if (!perm) return true
            return state.permissions.includes(perm)
        },
        hasRole: (state) => (role) => {
            if (!role) return true
            return state.roles.some(r => r.role_name === role)
        }
    }
})

export default store
```

### 规范3：在组件中使用 Store

```vue
<script setup>
import { computed } from 'vue'
import { useStore } from 'vuex'

const store = useStore()

// 获取 state
const userInfo = computed(() => store.state.userInfo)
const theme = computed(() => store.state.theme)

// 调用 mutation
const setTheme = (newTheme) => {
    store.commit('setTheme', newTheme)
}

// 调用 action
const logout = () => {
    store.dispatch('logout')
}

// 使用 getter
const hasPermission = (perm) => store.getters.hasPermission(perm)
</script>
```

### 规范4：添加新模块状态

```javascript
// 在 state 中添加新状态
state() {
    return {
        // ... 现有状态
        
        // 新增模块状态示例
        currentProject: null,      // 当前选中的项目
        testRunning: false,        // 测试是否运行中
        wsConnected: false         // WebSocket 连接状态
    }
},

// 添加对应的 mutations
mutations: {
    // ... 现有 mutations
    
    setCurrentProject(state, project) {
        state.currentProject = project
    },
    setTestRunning(state, running) {
        state.testRunning = running
    },
    setWsConnected(state, connected) {
        state.wsConnected = connected
    }
}
```

### 规范5：权限控制集成

```vue
<template>
  <!-- 使用 v-permission 指令 -->
  <el-button v-permission="'user:add'" @click="handleAdd">新增</el-button>
  
  <!-- 或使用 v-if + getter -->
  <el-button v-if="hasPermission('user:edit')" @click="handleEdit">编辑</el-button>
</template>

<script setup>
import { useStore } from 'vuex'

const store = useStore()
const hasPermission = (perm) => store.getters.hasPermission(perm)
</script>
```

### 规范6：持久化存储

```javascript
// 需要持久化的状态使用 localStorage
mutations: {
    setTheme(state, theme) {
        state.theme = theme
        document.documentElement.setAttribute('data-theme', theme)
        localStorage.setItem('theme', theme)  // 持久化
    }
},

// 初始化时从 localStorage 恢复
state() {
    return {
        theme: localStorage.getItem('theme') || 'light'
    }
}
```

## 禁止事项
- ❌ 直接修改 state（必须通过 mutation）
- ❌ 在 mutation 中执行异步操作
- ❌ 不使用 computed 获取 state（导致响应式失效）
- ❌ 在组件中存储应该全局共享的状态

## 检查清单
- [ ] 是否通过 mutation 修改 state
- [ ] 异步操作是否放在 actions 中
- [ ] 是否使用 computed 获取 state
- [ ] 需要持久化的状态是否保存到 localStorage
