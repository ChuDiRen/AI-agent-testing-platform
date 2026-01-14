import { defineStore } from 'pinia'

/**
 * 用户状态管理
 * 包括：用户信息、角色、权限等
 */
export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: null, // 用户信息
    roles: [], // 用户角色
    permissions: JSON.parse(localStorage.getItem('permissions') || '[]') // 用户权限（从 localStorage 恢复）
  }),

  getters: {
    // 判断是否有某个权限
    hasPermission: (state) => (perm) => {
      if (!perm) return true
      // 支持数组形式的权限检查（满足任一即可）
      if (Array.isArray(perm)) {
        return perm.some(p => state.permissions.includes(p))
      }
      return state.permissions.includes(perm)
    },

    // 判断是否有某个角色
    hasRole: (state) => (role) => {
      if (!role) return true
      // 支持数组形式的角色检查（满足任一即可）
      if (Array.isArray(role)) {
        return role.some(roleName => state.roles.some(r => r.role_name === roleName))
      }
      return state.roles.some(r => r.role_name === role)
    },

    // 是否是管理员
    isAdmin: (state) => {
      const adminRoles = ['admin', '超级管理员', 'Administrator']
      return state.roles.some(r => adminRoles.includes(r.role_name))
    },

    // 用户显示名称
    displayName: (state) => {
      return state.userInfo?.real_name || state.userInfo?.username || '未知用户'
    },

    // 用户头像
    avatar: (state) => {
      return state.userInfo?.avatar || ''
    }
  },

  actions: {
    /**
     * 设置用户信息
     */
    setUserInfo(userInfo) {
      this.userInfo = userInfo
    },

    /**
     * 设置用户角色
     */
    setRoles(roles) {
      this.roles = roles || []
    },

    /**
     * 设置用户权限
     */
    setPermissions(permissions) {
      this.permissions = permissions || []
      localStorage.setItem('permissions', JSON.stringify(permissions))
    },

    /**
     * 更新用户权限
     */
    updatePermissions(permissions) {
      this.setPermissions(permissions)
    },

    /**
     * 清除用户信息（登出）
     */
    clearUserInfo() {
      this.userInfo = null
      this.roles = []
      this.permissions = []
    },

    /**
     * 登出
     */
    logout() {
      this.clearUserInfo()
    }
  }
})

