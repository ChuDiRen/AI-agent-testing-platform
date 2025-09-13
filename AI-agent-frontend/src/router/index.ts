import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 临时的简单路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/Layout/MainLayout.vue'),
    meta: {
      requiresAuth: true
    },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: {
          title: '仪表板',
          icon: 'Monitor'
        }
      }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '权限不足'
    }
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 动态路由是否已添加的标记
let routesAdded = false

// 重置路由的函数
export const resetRoutes = () => {
  console.log('Resetting routes...')

  // 移除所有动态添加的路由
  const allRoutes = router.getRoutes()
  allRoutes.forEach(route => {
    // 移除非基础路由（除了基础的登录、Layout、错误页面等）
    if (route.name && !['Login', 'Layout', 'Dashboard', 'Forbidden', 'NotFound'].includes(route.name as string)) {
      router.removeRoute(route.name)
    }
  })

  routesAdded = false
  console.log('Routes reset successfully')
}

// 添加动态路由的函数
export const addDynamicRoutes = async () => {
  if (routesAdded) {
    console.log('Dynamic routes already added')
    return
  }

  try {
    console.log('Adding dynamic routes...')

    // 动态导入permission store，避免循环依赖
    const { usePermissionStore } = await import('@/store/modules/permission')
    const permissionStore = usePermissionStore()

    // 生成动态路由
    const dynamicRoutes = await permissionStore.generateRoutes()

    // 将动态路由添加到Layout路由的children中
    dynamicRoutes.forEach(route => {
      router.addRoute('Layout', route)
    })

    // 添加404路由（必须在最后）
    router.addRoute({
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    })

    routesAdded = true
    console.log('Dynamic routes added successfully:', dynamicRoutes.length)

  } catch (error) {
    console.error('Failed to add dynamic routes:', error)

    // 如果获取动态路由失败，添加空路由占位
    router.addRoute('Layout', {
      path: '/empty',
      name: 'Empty',
      component: () => import('@/views/error/403.vue'),
      meta: {
        title: '无权限'
      }
    })

    // 仍然添加404路由
    router.addRoute({
      path: '/:pathMatch(.*)*',
      redirect: '/404'
    })

    throw error
  }
}

// 简化的路由守卫：基本认证
router.beforeEach(async (to, from, next) => {
  console.log('Route guard:', to.path, 'requiresAuth:', to.meta?.requiresAuth)

  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - AI智能代理测试平台`
  }

  // 如果访问登录页面
  if (to.path === '/login') {
    // 动态导入相关模块
    const { useUserStore } = await import('@/store')
    const { getToken, isNullOrWhitespace } = await import('@/utils/auth')
    const userStore = useUserStore()
    const token = getToken()

    // 检查实际的token状态，确保store和cookie状态一致
    if (token && !isNullOrWhitespace(token) && userStore.isLoggedIn) {
      next('/')
      return
    } else {
      // 如果没有有效token但store显示已登录，清除store状态
      if (userStore.isLoggedIn && (!token || isNullOrWhitespace(token))) {
        console.log('Token mismatch, clearing user store')
        userStore.clearUserData()
      }
      next()
      return
    }
  }

  // 如果访问错误页面，直接放行
  if (to.path === '/403' || to.path === '/404') {
    next()
    return
  }

  // 检查是否需要认证
  if (to.meta?.requiresAuth !== false) {
    // 动态导入相关模块，避免循环依赖
    const { getToken, isNullOrWhitespace } = await import('@/utils/auth')
    const { useUserStore } = await import('@/store')

    const token = getToken()
    const userStore = useUserStore()

    if (!token || isNullOrWhitespace(token)) {
      console.log('No token, redirecting to login')
      next('/login')
      return
    }

    // 如果有token但用户store中没有登录状态，需要初始化用户信息
    if (token && !userStore.isLoggedIn) {
      userStore.setToken(token)
    }

    // 如果用户已登录但动态路由未添加，则添加动态路由
    if (userStore.isLoggedIn && !routesAdded) {
      try {
        await addDynamicRoutes()
        console.log('Dynamic routes loaded successfully')
      } catch (error) {
        console.error('Failed to load dynamic routes:', error)
        // 动态路由加载失败时，仍然允许访问基础路由
      }
    }

    // 检查权限
    if (to.meta?.permission) {
      const { usePermissionStore } = await import('@/store/modules/permission')
      const permissionStore = usePermissionStore()

      const hasPermission = permissionStore.hasPermission(to.meta.permission as string)

      // 超级管理员跳过权限校验
      const isAdmin = userStore.hasRole('admin') || userStore.hasRole('super_admin')

      if (!isAdmin && !hasPermission) {
        console.log('Permission denied for route:', to.path, 'required:', to.meta.permission)
        next('/403')
        return
      }
    }

    console.log('Token found, allowing access')
  }

  // 默认放行
  next()
})

export default router
