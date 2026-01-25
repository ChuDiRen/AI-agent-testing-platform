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

    // 没有token的情况
    if (!token) {
      if (isWhiteList) {
        next()
      } else {
        next({ path: '/login', query: { redirect: to.fullPath } })
      }
      return
    }

    // 有token的情况
    if (to.path === '/login') {
      next('/')
      return
    }

    // 检查用户信息和路由
    const userStore = useUserStore()
    const permissionStore = usePermissionStore()

    // 如果没有用户信息，获取用户信息
    if (!userStore.userId) {
      try {
        const userInfo = await userStore.getUserInfo()
        if (!userInfo) {
          userStore.logout()
          next({ path: '/login', query: { redirect: to.fullPath } })
          return
        }
      } catch (error) {
        userStore.logout()
        next({ path: '/login', query: { redirect: to.fullPath } })
        return
      }
    }

    // 如果没有动态路由，生成路由（只生成一次）
    if (permissionStore.accessRoutes.length === 0) {
      try {
        const accessRoutes = await permissionStore.generateRoutes()
        await permissionStore.getAccessApis()
        // 动态添加路由
        accessRoutes.forEach((route, index) => {
          router.addRoute(route)
        })
        // 重新导航到目标路由
        next({ ...to, replace: true })
      } catch (error) {
        await userStore.logout()
        next('/login')
      }
    } else {
      // 检查workbench路由是否存在
      const workbenchRoute = router.getRoutes().find(r => r.path === '/workbench')
      if (!workbenchRoute && to.path === '/workbench') {
        try {
          // 重新生成并添加路由
          const accessRoutes = await permissionStore.generateRoutes(true) // 强制使用静态菜单
          accessRoutes.forEach((route) => {
            router.addRoute(route)
          })
        } catch (error) {
          // 重新添加路由失败处理
        }
      }
      next()
    }
  })

  // 后置守卫 - 设置页面标题
  router.afterEach((to) => {
    document.title = to.meta?.title ? `${to.meta.title} - API测试平台` : 'API测试平台'
  })
}

