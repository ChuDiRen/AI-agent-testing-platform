import { defineStore } from 'pinia'
import { basicRoutes, vueModules } from '@/router/routes'
import Layout from '@/layout/index.vue'
import { getToken } from '@/utils'
import api from '@/api'

// 根据后端传来数据构建出前端路由
function buildRoutes(routes = []) {
  return routes.map((e) => {
    const route = {
      name: e.menu_name,
      path: e.path,
      component: shallowRef(Layout),
      isHidden: e.menu_type === '1', // 按钮类型隐藏
      redirect: e.redirect,
      meta: {
        title: e.menu_name,
        icon: e.icon,
        order: e.order_num,
        keepAlive: false,
      },
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单
      route.children = e.children.map((e_child) => ({
        name: e_child.menu_name,
        path: e_child.path,
        component: vueModules[`/src/views${e_child.component}/index.vue`],
        isHidden: e_child.menu_type === '1',
        meta: {
          title: e_child.menu_name,
          icon: e_child.icon,
          order: e_child.order_num,
          keepAlive: false,
        },
      }))
    } else if (e.component) {
      // 没有子菜单，创建一个默认的子路由
      route.children.push({
        name: `${e.menu_name}Default`,
        path: '',
        component: vueModules[`/src/views${e.component}/index.vue`],
        isHidden: true,
        meta: {
          title: e.menu_name,
          icon: e.icon,
          order: e.order_num,
          keepAlive: false,
        },
      })
    }

    return route
  })
}

export const usePermissionStore = defineStore('permission', {
  state() {
    return {
      accessRoutes: [],
      accessApis: [],
    }
  },
  
  getters: {
    routes() {
      return basicRoutes.concat(this.accessRoutes)
    },
    menus() {
      return this.routes.filter((route) => route.name && !route.isHidden)
    },
    apis() {
      return this.accessApis
    },
  },
  
  actions: {
    async generateRoutes() {
      try {
        // 从token中获取用户ID
        const token = getToken()
        if (!token) {
          return []
        }

        const payload = JSON.parse(atob(token.split('.')[1]))
        const userId = payload.user_id || payload.sub

        const res = await api.getUserMenu({ user_id: userId })
        if (res.code === 200 && res.data.menus) {
          this.accessRoutes = buildRoutes(res.data.menus)
        }
        return this.accessRoutes
      } catch (error) {
        console.error('获取用户菜单失败:', error)
        return []
      }
    },

    async getAccessApis() {
      try {
        // 从token中获取用户ID
        const token = getToken()
        if (!token) {
          return []
        }

        const payload = JSON.parse(atob(token.split('.')[1]))
        const userId = payload.user_id || payload.sub

        const res = await api.getUserMenu({ user_id: userId })
        if (res.code === 200 && res.data.permissions) {
          this.accessApis = res.data.permissions
        }
        return this.accessApis
      } catch (error) {
        console.error('获取用户权限失败:', error)
        return []
      }
    },
    
    resetPermission() {
      this.$reset()
    },
  },
})
