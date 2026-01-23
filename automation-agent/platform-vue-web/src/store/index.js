// src/store/index.js
import { createStore } from 'vuex'
import loginApi from '~/views/login/loginApi'
import { resetDynamicRoutes } from '~/router'

// 定义状态类型（使用JSDoc注释）
/**
 * @typedef {Object} State
 * @property {string} asideWidth
 * @property {Object} userInfo
 * @property {Array} userMenus
 * @property {Array} userApis
 * @property {Array} userRoles
 */

// 创建 store 实例
const store = createStore({
  state: {
    asideWidth: '250px',
    userInfo: {},
    userMenus: [],
    userApis: [],
    userRoles: [],
    permissions: {
      menus: [],
      apis: [],
      roles: [],
      is_superuser: false
    }
  },
  
  getters: {
    userId: state => state.userInfo?.id,
    username: state => state.userInfo?.username,
    email: state => state.userInfo?.email,
    avatar: state => state.userInfo?.avatar,
    isSuperUser: state => state.userInfo?.is_superuser || state.permissions?.is_superuser,
    isActive: state => state.userInfo?.is_active,
    userRoles: state => state.permissions?.roles || [],
    hasMenuPermission: state => (menuPath) => {
      if (state.permissions?.is_superuser) return true
      return state.permissions?.menus?.includes(menuPath)
    },
    hasApiPermission: state => (apiPath, method = 'GET') => {
      if (state.permissions?.is_superuser) return true
      const permissionKey = `${apiPath}:${method}`
      return state.permissions?.apis?.includes(permissionKey) || state.permissions?.apis?.includes(apiPath)
    }
  },
  
  mutations: {
    handleAsideWidth(state) {
      state.asideWidth = state.asideWidth === '250px' ? '20px' : '250px'
    },
    
    setUserInfo(state, userInfo) {
      state.userInfo = userInfo
    },
    
    setUserMenus(state, menus) {
      state.userMenus = menus
    },
    
    setUserApis(state, apis) {
      state.userApis = apis
    },
    
    setPermissions(state, permissions) {
      state.permissions = permissions
    },
    
    clearUserData(state) {
      state.userInfo = {}
      state.userMenus = []
      state.userApis = []
      state.userRoles = []
      state.permissions = {
        menus: [],
        apis: [],
        roles: [],
        is_superuser: false
      }
    }
  },
  
  actions: {
    // 获取用户信息
    async getUserInfo({ commit }) {
      try {
        const res = await loginApi.getUserInfo()
        if (res.data.code === 200) {
          commit('setUserInfo', res.data.data)
          return res.data.data
        }
        return null
      } catch (error) {
        console.error('获取用户信息失败:', error)
        return null
      }
    },
    
    // 获取用户菜单
    async getUserMenu({ commit }) {
      try {
        const res = await loginApi.getUserMenu()
        if (res.data.code === 200) {
          commit('setUserMenus', res.data.data)
          return res.data.data
        }
        return []
      } catch (error) {
        console.error('获取用户菜单失败:', error)
        return []
      }
    },
    
    // 获取用户API权限
    async getUserApi({ commit }) {
      try {
        const res = await loginApi.getUserApi()
        if (res.data.code === 200) {
          commit('setUserApis', res.data.data)
          return res.data.data
        }
        return []
      } catch (error) {
        console.error('获取用户API权限失败:', error)
        return []
      }
    },
    
    // 获取用户权限
    async getUserPermissions({ commit }) {
      try {
        // 使用统一的 API 请求方式
        const res = await loginApi.getUserApi();
        if (res.data.code === 200) {
          commit('setPermissions', res.data.data);
          return res.data.data;
        }
        return null;
      } catch (error) {
        console.error('获取用户权限失败:', error);
        return null;
      }
    },
    
    // 登出
    logout({ commit }) {
      // 清除localStorage中的所有用户相关数据
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('username')
      localStorage.removeItem('loglevel') // 清除日志级别
      localStorage.removeItem('tabList') // 清除标签页缓存

      // 清除所有cookies
      document.cookie.split(";").forEach(function(c) {
        document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
      });

      // 清除store中的用户数据
      commit('clearUserData')

      // 重置动态路由
      resetDynamicRoutes()
    }
  },
  
  modules: {
    // modules
  }
})

export default store