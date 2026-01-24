/**
 * 路由守卫 - 参考vue-fastapi-admin实现
 */
import { useUserStore } from '@/store/modules/user'
import { usePermissionStore } from '@/store/modules/permission'

const WHITE_LIST = ['/login', '/about', '/403', '/404', '/500'] // 白名单路由

export function setupRouterGuard(router) {
  router.beforeEach(async (to, from, next) => {
    const token = localStorage.getItem('token')
    const isWhiteList = WHITE_LIST.includes(to.path)

    // 白名单路由直接放行
    if (isWhiteList) {
      if (to.path === '/login' && token) {
        next('/home')
      } else {
        next()
      }
      return
    }

    // 未登录跳转登录页
    if (!token) {
      next({ path: '/login', query: { redirect: to.fullPath } })
      return
    }

    // 已登录，检查用户信息和路由
    const userStore = useUserStore()
    const permissionStore = usePermissionStore()

    // 如果没有用户信息，获取用户信息
    if (!userStore.userId) {
      await userStore.getUserInfo()
    }

    // 如果没有动态路由，生成路由
    if (permissionStore.accessRoutes.length === 0) {
      try {
        const accessRoutes = await permissionStore.generateRoutes()
        await permissionStore.getAccessApis()
        // 动态添加路由
        accessRoutes.forEach((route) => {
          if (!router.hasRoute(route.name)) {
            router.addRoute(route)
          }
        })
        // 重新导航
        next({ ...to, replace: true })
      } catch (error) {
        console.error('加载动态路由失败:', error)
        await userStore.logout()
        next('/login')
      }
    } else {
      next()
    }
  })

  // 后置守卫 - 设置页面标题
  router.afterEach((to) => {
    document.title = to.meta?.title ? `${to.meta.title} - API测试平台` : 'API测试平台'
  })
}

