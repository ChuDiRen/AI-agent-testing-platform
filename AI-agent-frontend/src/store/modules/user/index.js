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
        // 调用新的getUserInfo接口（不需要传user_id）
        const res = await api.getUserInfo()
        if (res.code !== 200) {
          this.logout()
          return
        }

        const userData = res.data
        this.userInfo = {
          id: userData.user_id,  // 后端返回user_id
          username: userData.username,
          nickname: userData.nickname || userData.username,
          email: userData.email || '',
          mobile: userData.mobile || '',
          avatar: userData.avatar || 'https://avatars.githubusercontent.com/u/54677442?v=4',
          dept_id: userData.dept_id,
          dept_name: userData.dept_name || '',
          roles: userData.roles || [],  // 后端返回roles数组
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
