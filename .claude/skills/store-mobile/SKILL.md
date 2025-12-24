# 移动端状态管理技能

## 触发条件
- 关键词：移动端状态、uni-app store、小程序状态、Pinia
- 场景：当用户需要管理移动端应用状态时

## 核心规范

### 规范1：使用 Pinia 进行状态管理

```javascript
// store/modules/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: uni.getStorageSync('userInfo') || null,
    isLogin: false
  }),
  
  getters: {
    // 是否已登录
    hasLogin: (state) => !!state.token && !!state.userInfo,
    
    // 用户名
    userName: (state) => state.userInfo?.nickname || state.userInfo?.username || '未登录'
  },
  
  actions: {
    // 设置 Token
    setToken(token) {
      this.token = token
      this.isLogin = !!token
      if (token) {
        uni.setStorageSync('token', token)
      } else {
        uni.removeStorageSync('token')
      }
    },
    
    // 设置用户信息
    setUserInfo(userInfo) {
      this.userInfo = userInfo
      if (userInfo) {
        uni.setStorageSync('userInfo', userInfo)
      } else {
        uni.removeStorageSync('userInfo')
      }
    },
    
    // 登录
    async login(loginData) {
      try {
        const res = await api.login(loginData)
        this.setToken(res.data.token)
        this.setUserInfo(res.data.userInfo)
        return res
      } catch (e) {
        throw e
      }
    },
    
    // 登出
    logout() {
      this.setToken('')
      this.setUserInfo(null)
      // 跳转登录页
      uni.reLaunch({ url: '/pages/login/index' })
    },
    
    // 获取用户信息
    async getUserInfo() {
      try {
        const res = await api.getUserInfo()
        this.setUserInfo(res.data)
        return res.data
      } catch (e) {
        throw e
      }
    }
  }
})
```

### 规范2：Store 入口配置

```javascript
// store/index.js
import { createPinia } from 'pinia'

const pinia = createPinia()

export default pinia

// 导出所有 store
export * from './modules/user'
export * from './modules/app'
export * from './modules/cart'
```

### 规范3：在 main.js 中注册

```javascript
// main.js
import { createSSRApp } from 'vue'
import App from './App.vue'
import pinia from './store'

export function createApp() {
  const app = createSSRApp(App)
  app.use(pinia)
  return { app }
}
```

### 规范4：在组件中使用

```vue
<template>
  <view class="user-info">
    <view v-if="userStore.hasLogin">
      <text>{{ userStore.userName }}</text>
      <wd-button @click="handleLogout">退出登录</wd-button>
    </view>
    <view v-else>
      <wd-button type="primary" @click="goLogin">去登录</wd-button>
    </view>
  </view>
</template>

<script setup>
import { useUserStore } from '@/store'

const userStore = useUserStore()

const handleLogout = () => {
  uni.showModal({
    title: '提示',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        userStore.logout()
      }
    }
  })
}

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/index' })
}
</script>
```

### 规范5：应用级状态管理

```javascript
// store/modules/app.js
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 系统信息
    systemInfo: null,
    // 网络状态
    networkType: 'unknown',
    // 是否显示 TabBar
    showTabBar: true,
    // 全局加载状态
    loading: false,
    // 主题
    theme: uni.getStorageSync('theme') || 'light'
  }),
  
  actions: {
    // 初始化系统信息
    initSystemInfo() {
      const systemInfo = uni.getSystemInfoSync()
      this.systemInfo = systemInfo
    },
    
    // 监听网络状态
    initNetworkListener() {
      uni.getNetworkType({
        success: (res) => {
          this.networkType = res.networkType
        }
      })
      
      uni.onNetworkStatusChange((res) => {
        this.networkType = res.networkType
        if (!res.isConnected) {
          uni.showToast({
            title: '网络已断开',
            icon: 'none'
          })
        }
      })
    },
    
    // 设置主题
    setTheme(theme) {
      this.theme = theme
      uni.setStorageSync('theme', theme)
    },
    
    // 设置加载状态
    setLoading(loading) {
      this.loading = loading
      if (loading) {
        uni.showLoading({ title: '加载中...' })
      } else {
        uni.hideLoading()
      }
    }
  }
})
```

### 规范6：购物车状态管理示例

```javascript
// store/modules/cart.js
import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: uni.getStorageSync('cartItems') || []
  }),
  
  getters: {
    // 购物车数量
    count: (state) => state.items.reduce((sum, item) => sum + item.quantity, 0),
    
    // 购物车总价
    totalPrice: (state) => state.items.reduce((sum, item) => sum + item.price * item.quantity, 0),
    
    // 选中的商品
    selectedItems: (state) => state.items.filter(item => item.selected),
    
    // 选中商品总价
    selectedTotalPrice: (state) => {
      return state.items
        .filter(item => item.selected)
        .reduce((sum, item) => sum + item.price * item.quantity, 0)
    }
  },
  
  actions: {
    // 添加商品
    addItem(product) {
      const existItem = this.items.find(item => item.id === product.id)
      if (existItem) {
        existItem.quantity++
      } else {
        this.items.push({
          ...product,
          quantity: 1,
          selected: true
        })
      }
      this.saveToStorage()
    },
    
    // 移除商品
    removeItem(productId) {
      const index = this.items.findIndex(item => item.id === productId)
      if (index > -1) {
        this.items.splice(index, 1)
        this.saveToStorage()
      }
    },
    
    // 更新数量
    updateQuantity(productId, quantity) {
      const item = this.items.find(item => item.id === productId)
      if (item) {
        item.quantity = quantity
        this.saveToStorage()
      }
    },
    
    // 切换选中状态
    toggleSelected(productId) {
      const item = this.items.find(item => item.id === productId)
      if (item) {
        item.selected = !item.selected
        this.saveToStorage()
      }
    },
    
    // 全选/取消全选
    toggleAllSelected(selected) {
      this.items.forEach(item => {
        item.selected = selected
      })
      this.saveToStorage()
    },
    
    // 清空购物车
    clearCart() {
      this.items = []
      this.saveToStorage()
    },
    
    // 保存到本地存储
    saveToStorage() {
      uni.setStorageSync('cartItems', this.items)
    }
  }
})
```

## 最佳实践

1. **按需持久化** - 只持久化必要的状态（token、userInfo、主题等）
2. **敏感数据加密** - Token 等敏感信息考虑加密存储
3. **清理过期数据** - 登出时清理所有用户相关缓存
4. **状态分模块** - 按业务领域拆分 store 模块
5. **避免过度使用** - 简单的页面状态不需要放入全局 store

## 禁止事项

1. ❌ 禁止在 store 中直接操作 DOM
2. ❌ 禁止在 store 中存储组件实例
3. ❌ 禁止存储过大的数据（如长列表）到本地存储
4. ❌ 禁止在 getters 中修改 state
