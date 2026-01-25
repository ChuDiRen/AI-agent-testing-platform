/**
 * 权限store模块 - 参考vue-fastapi-admin实现
 * 管理动态路由和菜单权限
 */
import { defineStore } from 'pinia'
import { shallowRef } from 'vue'
import { basicRoutes, vueModules } from '@/router/routes'
import Layout from '@/layout/index.vue'
import loginApi from '@/api/loginApi'
import { staticMenus, buildStaticRoutes } from '@/config/static-menu'

// 根据后端传来数据构建前端路由
function buildRoutes(routes = []) {
  
  // 确保routes是数组
  if (!Array.isArray(routes)) {
    return []
  }
  
  return routes.map((e) => {
    const route = {
      name: e.name,
      path: e.path,
      component: Layout,
      isHidden: e.is_hidden,
      meta: {
        title: e.name,
        icon: e.icon,
        order: e.order,
        keepAlive: e.keepalive,
      },
      children: []
    }
    
    // 处理子菜单
    if (e.children && e.children.length > 0) {
      route.children = e.children.map((e_child) => {
        let componentPath = e_child.component
        
        // 统一处理组件路径格式
        if (!componentPath) {
          return null
        }
        
        // 构建完整的组件路径
        let fullComponentPath
        if (componentPath.startsWith('/')) {
          fullComponentPath = `/src/views${componentPath}/index.vue`
        } else {
          fullComponentPath = `/src/views/${componentPath}/index.vue`
        }
        
        let componentLoader = vueModules[fullComponentPath]
        
        if (!componentLoader) {
          // 尝试其他可能的路径格式
          const alternativePaths = [
            `/src/views/${e_child.component}/index.vue`,
            `/src/views/${componentPath}.vue`,
            `/src/views/${e_child.component}.vue`
          ]
          
          for (const altPath of alternativePaths) {
            componentLoader = vueModules[altPath]
            if (componentLoader) {
              fullComponentPath = altPath
              break
            }
          }
          
          if (!componentLoader) {
            return null
          }
        }
        
        return {
          name: `${e.name}${e_child.name}`,
          path: `/${e_child.component}`,
          component: componentLoader,
          meta: {
            title: e_child.name,
            icon: e_child.icon,
            order: e_child.order,
          },
          isHidden: e_child.is_hidden
        }
      }).filter(Boolean) // 过滤掉null值
    } else {
      // 没有子菜单，创建一个默认的子路由
      let componentPath = e.component
      let fullComponentPath
      
      if (componentPath) {
        if (componentPath.startsWith('/')) {
          fullComponentPath = `/src/views${componentPath}/index.vue`
        } else {
          fullComponentPath = `/src/views/${componentPath}/index.vue`
        }
      } else {
        return null
      }
      
      let componentLoader = vueModules[fullComponentPath]
      
      if (!componentLoader) {
        // 尝试其他可能的路径格式
        const alternativePaths = [
          `/src/views/${e.component}/index.vue`,
          `/src/views/${componentPath}.vue`,
          `/src/views/${e.component}.vue`
        ]
        
        for (const altPath of alternativePaths) {
          componentLoader = vueModules[altPath]
          if (componentLoader) {
            fullComponentPath = altPath
            break
          }
        }
        
        if (!componentLoader) {
          return null
        }
      }
      
      route.children.push({
        name: `${e.name}Default`,
        path: '',
        component: componentLoader,
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
  }).filter(Boolean) // 过滤掉null值
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
    async generateRoutes(useStatic = false) {
      if (useStatic) {
        // 使用静态菜单
        this.accessRoutes = buildStaticRoutes(staticMenus)
        return this.accessRoutes
      }
      
      // 原有的动态菜单逻辑
      try {
        const res = await loginApi.getUserMenu() // 调用接口获取后端传来的菜单路由
        
        // 确保获取到正确的数据格式 - 后端返回格式: {code: 200, data: [...]}
        let menuData = res.data?.data || [] // 注意是res.data.data
        if (!Array.isArray(menuData)) {
          menuData = []
        }
        
        this.accessRoutes = buildRoutes(menuData) // 处理成前端路由格式
        return this.accessRoutes
      } catch (error) {
        // 动态路由失败时，回退到静态菜单
        this.accessRoutes = buildStaticRoutes(staticMenus)
        return this.accessRoutes
      }
    },
    async getAccessApis() {
      const res = await loginApi.getUserApi()
      this.accessApis = res.data
      return this.accessApis
    },
    resetPermission() {
      this.$reset()
    },
  },
})

