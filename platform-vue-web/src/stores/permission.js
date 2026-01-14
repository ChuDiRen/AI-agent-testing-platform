import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '~/router/index.js'
import { generateRoutesFromMenus, extractPermissionsFromMenus } from '~/utils/dynamicRoute.js'

/**
 * 动态路由状态管理
 * 管理动态生成的路由和权限
 */
export const usePermissionStore = defineStore('permission', {
  state: () => ({
    dynamicRoutes: [], // 动态路由列表
    isRoutesGenerated: false, // 是否已生成动态路由
    routeGenerationTime: null, // 路由生成时间戳
  }),

  getters: {
    // 所有路由（静态 + 动态）
    allRoutes: (state) => {
      const staticRoutes = router.options.routes.find(r => r.path === '/home')?.children || []
      return [...staticRoutes, ...state.dynamicRoutes]
    },
    
    // 路由是否正在生成
    isGenerating: (state) => {
      if (!state.routeGenerationTime) return false
      return Date.now() - state.routeGenerationTime < 5000 // 5秒内视为正在生成
    }
  },

  actions: {
    /**
     * 根据菜单树生成动态路由
     * 优化：添加性能监控和防抖
     */
    async generateRoutes(menuTree) {
      // 性能监控：开始时间
      const startTime = performance.now()
      this.routeGenerationTime = startTime

      // 从菜单中提取权限
      const permissions = extractPermissionsFromMenus(menuTree)

      // 生成动态路由
      const dynamicRoutes = generateRoutesFromMenus(menuTree)

      // 批量添加路由（优化性能）
      const routePromises = dynamicRoutes.map(route => {
        return new Promise((resolve, reject) => {
          try {
            // 使用 setTimeout 让出主线程，避免阻塞 UI
            setTimeout(() => {
              router.addRoute('home', route)
              resolve({ success: true, route })
            }, 0)
          } catch (error) {
            console.warn('添加路由失败:', error)
            reject({ success: false, route, error })
          }
        })
      })

      // 等待所有路由添加完成
      await Promise.allSettled(routePromises)

      this.dynamicRoutes = dynamicRoutes
      this.isRoutesGenerated = true

      // 性能监控：结束时间
      const endTime = performance.now()
      const duration = endTime - startTime
      console.log(`路由生成完成: ${dynamicRoutes.length} 条路由, 耗时: ${duration.toFixed(2)}ms`)

      return dynamicRoutes
    },

    /**
     * 清空动态路由
     * 优化：批量移除路由
     */
    clearRoutes() {
      const startTime = performance.now()

      // 移除所有动态添加的路由
      this.dynamicRoutes.forEach(route => {
        if (route.name) {
          try {
            router.removeRoute(route.name)
          } catch (error) {
            console.warn('移除路由失败:', error)
          }
        }
      })

      this.dynamicRoutes = []
      this.isRoutesGenerated = false
      this.routeGenerationTime = null

      const duration = performance.now() - startTime
      console.log(`路由清空完成, 耗时: ${duration.toFixed(2)}ms`)
    },

    /**
     * 刷新动态路由
     * 用于菜单权限变化时重新生成路由
     */
    async refreshRoutes(menuTree) {
      console.log('刷新动态路由...')
      
      // 先清空现有路由
      this.clearRoutes()
      
      // 等待一个事件循环，确保路由完全移除
      await new Promise(resolve => setTimeout(resolve, 0))
      
      // 重新生成路由
      return await this.generateRoutes(menuTree)
    }
  }
})

