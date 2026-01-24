/**
 * 用户store模块 - 参考vue-fastapi-admin实现
 * 管理用户信息和登录状态
 */
import { defineStore } from 'pinia'
import loginApi from '@/api/loginApi'

export const useUserStore = defineStore('user', {
  state() {
    return {
      userInfo: {},
      token: localStorage.getItem('token') || '',
    }
  },
  getters: {
    userId: (state) => state.userInfo?.id,
    username: (state) => state.userInfo?.username,
    alias: (state) => state.userInfo?.alias,
    email: (state) => state.userInfo?.email,
    avatar: (state) => state.userInfo?.avatar,
    isSuperUser: (state) => state.userInfo?.is_superuser,
    isActive: (state) => state.userInfo?.is_active,
    roles: (state) => state.userInfo?.roles || [],
  },
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },
    async getUserInfo() {
      try {
        const res = await loginApi.getUserInfo()
        if (res.data?.code === 200) {
          this.userInfo = res.data.data || res.data.obj || {}
          return this.userInfo
        }
        return null
      } catch (error) {
        console.error('获取用户信息失败:', error)
        return null
      }
    },
    async logout() {
      // 清除localStorage中的所有用户相关数据
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('username')
      localStorage.removeItem('tabList')

      // 清除所有cookies
      document.cookie.split(';').forEach((c) => {
        document.cookie = c.replace(/^ +/, '').replace(/=.*/, '=;expires=' + new Date().toUTCString() + ';path=/')
      })

      // 重置store
      this.$reset()
    },
  },
})

