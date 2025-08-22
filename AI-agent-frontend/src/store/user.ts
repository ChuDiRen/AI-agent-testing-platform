import { defineStore } from 'pinia'
import { getToken, setToken, removeToken } from '@/utils/auth'
import { AuthApi } from '@/api/modules/auth'
import type { UserInfo, MenuTreeNode } from '@/api/types'
import { ElMessage } from 'element-plus'

// 用户状态接口
interface UserState {
  token: string | null
  userInfo: UserInfo | null
  permissions: string[]
  roles: string[]
  menus: MenuTreeNode[]
  loading: boolean
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: getToken(),
    userInfo: null,
    permissions: [],
    roles: [],
    menus: [],
    loading: false
  }),

  getters: {
    // 是否已登录
    isLoggedIn: (state) => !!state.token && !!state.userInfo,
    
    // 用户名
    username: (state) => state.userInfo?.username || '',
    
    // 用户头像
    avatar: (state) => state.userInfo?.avatar || '',
    
    // 用户邮箱
    email: (state) => state.userInfo?.email || '',
    
    // 用户部门
    deptName: (state) => state.userInfo?.dept_name || '',
    
    // 检查是否有特定权限
    hasPermission: (state) => (permission: string) => {
      return state.permissions.includes(permission)
    },
    
    // 检查是否有特定角色
    hasRole: (state) => (role: string) => {
      return state.roles.includes(role)
    },
    
    // 检查是否有任一权限
    hasAnyPermission: (state) => (permissions: string[]) => {
      return permissions.some(permission => state.permissions.includes(permission))
    },
    
    // 检查是否有任一角色
    hasAnyRole: (state) => (roles: string[]) => {
      return roles.some(role => state.roles.includes(role))
    }
  },

  actions: {
    // 设置token
    setToken(token: string) {
      this.token = token
      setToken(token)
    },

    // 设置用户信息
    setUserInfo(userInfo: UserInfo) {
      this.userInfo = userInfo
    },

    // 设置权限列表
    setPermissions(permissions: string[]) {
      this.permissions = permissions
    },

    // 设置角色列表
    setRoles(roles: string[]) {
      this.roles = roles
    },

    // 设置菜单列表
    setMenus(menus: MenuTreeNode[]) {
      this.menus = menus
    },

    // 用户登录
    async login(username: string, password: string) {
      try {
        this.loading = true
        const response = await AuthApi.login({ username, password })
        
        if (response.success && response.data) {
          const { access_token, user_info, permissions } = response.data
          
          // 保存token和用户信息
          this.setToken(access_token)
          this.setUserInfo(user_info)
          this.setPermissions(permissions)
          
          ElMessage.success('登录成功')
          return true
        } else {
          ElMessage.error(response.message || '登录失败')
          return false
        }
      } catch (error: any) {
        ElMessage.error(error.message || '登录失败')
        return false
      } finally {
        this.loading = false
      }
    },

    // 获取用户信息
    async getUserInfo() {
      try {
        if (!this.token) {
          throw new Error('No token found')
        }
        
        const response = await AuthApi.getCurrentUser()
        
        if (response.success && response.data) {
          this.setUserInfo(response.data)
          return true
        }
        
        return false
      } catch (error) {
        console.error('Failed to get user info:', error)
        return false
      }
    },

    // 获取用户权限
    async getUserPermissions() {
      try {
        if (!this.userInfo?.user_id) {
          return false
        }
        
        const response = await AuthApi.getUserPermissions(this.userInfo.user_id)
        
        if (response.success && response.data) {
          this.setPermissions(response.data)
          return true
        }
        
        return false
      } catch (error) {
        console.error('Failed to get user permissions:', error)
        return false
      }
    },

    // 获取用户菜单
    async getUserMenus() {
      try {
        if (!this.userInfo?.user_id) {
          return false
        }
        
        const response = await AuthApi.getUserMenus(this.userInfo.user_id)
        
        if (response.success && response.data) {
          this.setMenus(response.data)
          return true
        }
        
        return false
      } catch (error) {
        console.error('Failed to get user menus:', error)
        return false
      }
    },

    // 用户退出登录
    async logout() {
      try {
        // 调用后端退出API（可选）
        await AuthApi.logout()
      } catch (error) {
        console.error('Logout API call failed:', error)
      } finally {
        // 清除本地状态
        this.clearUserData()
        ElMessage.success('退出登录成功')
      }
    },

    // 清除用户数据
    clearUserData() {
      this.token = null
      this.userInfo = null
      this.permissions = []
      this.roles = []
      this.menus = []
      removeToken()
    },

    // 刷新token
    async refreshToken() {
      try {
        const response = await AuthApi.refreshToken()
        
        if (response.success && response.data) {
          this.setToken(response.data.access_token)
          return true
        }
        
        return false
      } catch (error) {
        console.error('Failed to refresh token:', error)
        // token刷新失败，清除用户数据
        this.clearUserData()
        return false
      }
    }
  },

  // 数据持久化配置
  persist: {
    key: 'user_store',
    storage: localStorage,
    paths: ['token', 'userInfo', 'permissions', 'roles']
  }
})

// 保持向后兼容
export const userStore = useUserStore
