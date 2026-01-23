import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null')
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userName: (state) => state.user?.full_name || state.user?.username || ''
  },

  actions: {
    async login(credentials) {
      try {
        const res = await login(credentials)
        const { access_token } = res.data
        this.setToken(access_token)
        
        // 获取用户信息
        const userRes = await getUserInfo()
        this.setUser(userRes.data)
        
        return true
      } catch (error) {
        console.error('Login failed:', error)
        return false
      }
    },

    setToken(token) {
      this.token = token
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
    },

    setUser(user) {
      this.user = user
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
    }
  }
})
