import { defineStore } from 'pinia'
import { resetRouter } from '@/router'
import { useTagsStore, usePermissionStore } from '@/store'
import { getToken, removeToken, toLogin } from '@/utils'
import api from '@/api'

export const useUserStore = defineStore('user', {
  state() {
    return {
      userInfo: {},
    }
  },
  
  getters: {
    userId() {
      return this.userInfo?.id
    },
    name() {
      return this.userInfo?.username
    },
    email() {
      return this.userInfo?.email
    },
    avatar() {
      return this.userInfo?.avatar
    },
    role() {
      return this.userInfo?.roles || []
    },
    isSuperUser() {
      return this.userInfo?.is_superuser
    },
    isActive() {
      return this.userInfo?.is_active
    },
  },
  
  actions: {
    async getUserInfo() {
      try {
        // 从token中获取用户ID
        const token = getToken()
        if (!token) {
          this.logout()
          return
        }

        // 解析token获取用户ID (简单解析，生产环境应该更安全)
        const payload = JSON.parse(atob(token.split('.')[1]))
        const userId = payload.user_id || payload.sub

        const res = await api.getUserInfo({ user_id: userId })
        if (res.code !== 200) {
          this.logout()
          return
        }

        const userData = res.data
        this.userInfo = {
          id: userData.id,  // 修正字段名
          username: userData.username,
          email: userData.email || '',
          avatar: userData.avatar || 'https://avatars.githubusercontent.com/u/54677442?v=4',
          roles: userData.roles || [],
          is_superuser: userData.is_superuser || false,  // 修正字段名
          is_active: userData.is_active || true,  // 修正字段名
          last_login: userData.last_login || null
        }
        return this.userInfo
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.logout()
        return error
      }
    },
    
    async logout() {
      const { resetTags } = useTagsStore()
      const { resetPermission } = usePermissionStore()
      removeToken()
      resetTags()
      resetPermission()
      resetRouter()
      this.$reset()
      toLogin()
    },
    
    setUserInfo(userInfo = {}) {
      this.userInfo = { ...this.userInfo, ...userInfo }
    },
  },
})
