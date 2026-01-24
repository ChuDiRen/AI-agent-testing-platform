/**
 * 权限store模块 - 参考vue-fastapi-admin实现
 * 管理动态路由和菜单权限
 */
import { defineStore } from 'pinia'
import { basicRoutes, vueModules } from '@/router/routes'
import Layout from '@/layout/index.vue'
import { shallowRef } from 'vue'
import loginApi from '@/api/loginApi'

/**
 * 根据后端传来数据构建前端路由 - 完全参考vue-fastapi-admin
 */
function buildRoutes(routes = []) {
  return routes.map((e) => {
    const route = {
      name: e.name,
      path: e.path,
      component: shallowRef(Layout),
      isHidden: e.is_hidden,
      redirect: e.redirect,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
      },
      children: [],
    }

    if (e.children && e.children.length > 0) {
      // 有子菜单
      route.children = e.children.map((e_child) => ({
        name: e_child.name,
        path: e_child.path,
        component: vueModules[`/src/views${e_child.component}/index.vue`],
        isHidden: e_child.is_hidden,
        meta: {
          title: e_child.name,
          icon: e_child.icon,
          order: e_child.order,
          keepAlive: e_child.keepalive,
        },
      }))
    } else {
      // 没有子菜单，创建一个默认的子路由
      route.children.push({
        name: `${e.name}Default`,
        path: '',
        component: vueModules[`/src/views${e.component}/index.vue`],
        isHidden: true,
        meta: {
          title: e.name,
          icon: e.icon,
          order: e.order,
          keepAlive: e.keepalive,
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
      const res = await loginApi.getUserMenu() // 调用接口获取后端传来的菜单路由
      const menuData = res.data?.data || res.data?.lst || []
      this.accessRoutes = buildRoutes(menuData) // 处理成前端路由格式
      return this.accessRoutes
    },
    async getAccessApis() {
      const res = await loginApi.getUserApi()
      this.accessApis = res.data?.data || res.data?.lst || []
      return this.accessApis
    },
    resetPermission() {
      this.$reset()
    },
  },
})

