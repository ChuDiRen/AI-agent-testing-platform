import { defineStore } from 'pinia'
import { shallowRef } from 'vue'
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
      route.children = e.children.map((e_child) => {
        // 只处理菜单类型的子项，跳过按钮类型
        if (e_child.menu_type === '1') {
          return null // 按钮类型不创建路由
        }

        return {
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
        }
      }).filter(Boolean) // 过滤掉null值
    } else if (e.component) {
      // 没有子菜单，创建一个默认的子路由（但标记为直接菜单）
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
      // 标记为直接菜单，用于前端判断是否显示下拉箭头
      route.meta.isDirect = true
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
        // 调用新的getUserMenu接口（不需要传user_id）
        const res = await api.getUserMenu()
        if (res.code === 200 && res.data) {
          // 后端直接返回菜单树数组
          const menus = Array.isArray(res.data) ? res.data : []
          this.accessRoutes = buildRoutes(menus)
        }
        return this.accessRoutes
      } catch (error) {
        console.error('获取用户菜单失败:', error)
        return []
      }
    },

    async getAccessApis() {
      try {
        // 调用新的getUserApi接口（不需要传user_id）
        const res = await api.getUserApi()
        if (res.code === 200 && res.data) {
          // 后端直接返回API权限数组
          this.accessApis = Array.isArray(res.data) ? res.data : []
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
