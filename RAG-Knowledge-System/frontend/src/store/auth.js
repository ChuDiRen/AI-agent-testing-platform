import { defineStore } from 'pinia'
import { login as loginApi, logout as logoutApi, verifyToken } from '../api/auth'
import { getUserInfo } from '../api/user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    isAuthenticated: !!localStorage.getItem('token'),
    isAdmin: false
  }),

  getters: {
    userInfo: (state) => state.user,
    userName: (state) => state.user?.full_name || state.user?.username || '',
    userAvatar: (state) => state.user?.avatar || ''
  },

  actions: {
    loadToken() {
      const token = localStorage.getItem('token')
      if (token) {
        this.token = token
        this.isAuthenticated = true
        this.loadUserInfo()
      }
    },

    async login(username, password) {
      try {
        const response = await loginApi({ username, password })

        // 后端返回统一格式：{code: 0, message: "success", data: {...}}
        if (response.code === 0) {
          const { access_token, user } = response.data

          // 保存token
          this.token = access_token
          this.user = user
          this.isAdmin = user.role?.code === 'superadmin'
          this.isAuthenticated = true

          // 持久化
          localStorage.setItem('token', access_token)
          localStorage.setItem('user', JSON.stringify(user))

          return { success: true, data: user }
        } else {
          return { success: false, error: response.message || '登录失败' }
        }
      } catch (error) {
        console.error('登录失败:', error)
        return { success: false, error: error.message }
      }
    },

    async logout() {
      try {
        await logoutApi()

        // 清空状态
        this.token = ''
        this.user = null
        this.isAuthenticated = false
        this.isAdmin = false

        // 清空localStorage
        localStorage.removeItem('token')
        localStorage.removeItem('user')

        return { success: true }
      } catch (error) {
        console.error('登出失败:', error)
        return { success: false, error: error.message }
      }
    },

    async loadUserInfo() {
      try {
        const response = await getUserInfo()
        if (response.code === 0) {
          this.user = response.data
          this.isAdmin = response.data.role?.code === 'superadmin'
          localStorage.setItem('user', JSON.stringify(response.data))
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },

    async verifyToken() {
      if (!this.token) {
        return false
      }

      try {
        const response = await verifyToken()
        return response.code === 0 && response.data.valid
      } catch (error) {
        console.error('Token验证失败:', error)
        return false
      }
    },

    updateUser(userInfo) {
      this.user = { ...this.user, ...userInfo }
      localStorage.setItem('user', JSON.stringify(this.user))
    }
  }
})
