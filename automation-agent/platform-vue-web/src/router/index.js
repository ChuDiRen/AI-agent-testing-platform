/**
 * 路由配置 - 参考vue-fastapi-admin重构
 */
import { createRouter, createWebHistory } from 'vue-router'
import { setupRouterGuard } from './guard'
import { basicRoutes, NOT_FOUND_ROUTE } from './routes'
import { useUserStore, usePermissionStore } from '@/store/modules'
import { getMenuModeParam } from '@/config/menu-config'

// 创建路由实例
export const router = createRouter({
  history: createWebHistory(),
  routes: basicRoutes,
  scrollBehavior: () => ({ left: 0, top: 0 }),
})

/**
 * 初始化路由
 */
export async function setupRouter(app) {
  await addDynamicRoutes()
  setupRouterGuard(router)
  app.use(router)
}

/**
 * 重置路由（登出时调用）
 */
export async function resetRouter() {
  const basicRouteNames = getRouteNames(basicRoutes)
  router.getRoutes().forEach((route) => {
    const name = route.name
    if (!basicRouteNames.includes(name)) {
      router.removeRoute(name)
    }
  })
}

/**
 * 添加动态路由
 */
export async function addDynamicRoutes() {
  const token = localStorage.getItem('token')

  // 没有token直接返回
  if (!token) {
    return
  }

  // 有token的情况
  const userStore = useUserStore()
  const permissionStore = usePermissionStore()

  // 获取用户信息
  if (!userStore.userId) {
    await userStore.getUserInfo()
  }

  try {
    // 生成动态路由 - 根据配置决定使用静态还是动态菜单
    const useStatic = getMenuModeParam()
    const accessRoutes = await permissionStore.generateRoutes(useStatic)
    await permissionStore.getAccessApis()

    // 添加路由
    accessRoutes.forEach((route) => {
      if (!router.hasRoute(route.name)) {
        router.addRoute(route)
      }
    })

    // 添加404路由（必须最后添加）
    if (!router.hasRoute(NOT_FOUND_ROUTE.name)) {
      router.addRoute(NOT_FOUND_ROUTE)
    }
  } catch (error) {
    await userStore.logout()
  }
}

/**
 * 获取路由名称列表
 */
export function getRouteNames(routes) {
  return routes.map((route) => getRouteName(route)).flat(1)
}

function getRouteName(route) {
  const names = [route.name]
  if (route.children?.length) {
    names.push(...route.children.map((item) => getRouteName(item)).flat(1))
  }
  return names
}

// 导出默认路由实例
export default router