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
      requiresAuth: false,
    },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/Layout/MainLayout.vue'),
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'LayoutRedirect',
        redirect: '/dashboard',
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: {
          title: '仪表板',
          icon: 'Monitor',
        },
      },
      // 个人中心路由
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/profile/Index.vue'),
        meta: {
          title: '个人中心',
          icon: 'User',
          hidden: true, // 不在菜单中显示
        },
      },
      // AI代理管理路由
      {
        path: '/agent',
        name: 'AgentManagement',
        meta: {
          title: 'AI代理管理',
          icon: 'Robot',
        },
        children: [
          {
            path: '',
            name: 'AgentList',
            component: () => import('@/views/agent/list/index.vue'),
            meta: {
              title: '代理列表',
              icon: 'List',
            },
          },
          {
            path: 'config/:id',
            name: 'AgentConfig',
            component: () => import('@/views/agent/config/index.vue'),
            meta: {
              title: '代理配置',
              hidden: true,
            },
          },
          {
            path: 'create',
            name: 'AgentCreate',
            component: () => import('@/views/agent/config/index.vue'),
            meta: {
              title: '创建代理',
              hidden: true,
            },
          },
        ],
      },
      // 测试用例管理路由
      {
        path: '/test',
        name: 'TestManagement',
        meta: {
          title: '测试管理',
          icon: 'TestTube',
        },
        children: [
          {
            path: 'generate',
            name: 'TestGenerate',
            component: () => import('@/views/test/generate/index.vue'),
            meta: {
              title: 'AI生成测试用例',
              icon: 'MagicStick',
            },
          },
          {
            path: 'cases',
            name: 'TestCases',
            component: () => import('@/views/test/cases/Index.vue'),
            meta: {
              title: '测试用例列表',
              icon: 'Document',
            },
          },
          {
            path: 'reports',
            name: 'TestReports',
            component: () => import('@/views/test/reports/list/index.vue'),
            meta: {
              title: '测试报告',
              icon: 'Document',
            },
          },
        ],
      },
      // AI模型配置路由
      {
        path: '/model',
        name: 'ModelManagement',
        meta: {
          title: 'AI模型配置',
          icon: 'Setting',
        },
        children: [
          {
            path: 'config',
            name: 'ModelConfig',
            component: () => import('@/views/model/config/index.vue'),
            meta: {
              title: '模型配置',
              icon: 'Setting',
            },
          },
        ],
      },
      // AI智能对话路由
      {
        path: '/chat',
        name: 'AIChat',
        component: () => import('@/views/chat/index.vue'),
        meta: {
          title: 'AI智能对话',
          icon: 'ChatDotRound',
        },
      },
    ],
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '权限不足',
    },
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在',
    },
  },
  // 注意：全局404路由将在动态路由加载后添加
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
  allRoutes.forEach((route) => {
    // 移除非基础路由（除了基础的登录、Layout、错误页面等）
    if (
      route.name &&
      ![
        'Login',
        'Layout',
        'LayoutRedirect',
        'Dashboard',
        'Profile',
        'Forbidden',
        'NotFound',
        'AgentManagement',
        'AgentList',
        'AgentConfig',
        'TestManagement',
        'TestGenerate',
        'TestCases',
        'TestReports',
        'ModelManagement',
        'ModelConfig',
      ].includes(route.name as string)
    ) {
      router.removeRoute(route.name)
    }
  })

  // 移除动态添加的404路由
  const dynamicNotFoundRoute = router
    .getRoutes()
    .find((route) => route.path === '/:pathMatch(.*)*' && !route.name)
  if (dynamicNotFoundRoute && dynamicNotFoundRoute.name) {
    router.removeRoute(dynamicNotFoundRoute.name)
  }

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
    console.log('Adding routes to Layout parent...')
    dynamicRoutes.forEach((route, index) => {
      console.log(`Adding route ${index + 1}:`, route.name, route.path)
      router.addRoute('Layout', route)
    })
    console.log('All dynamic routes added to router')

    // 检查是否已存在404路由，避免重复添加
    const existingNotFoundRoute = router
      .getRoutes()
      .find((route) => route.path === '/:pathMatch(.*)*')

    if (!existingNotFoundRoute) {
      // 添加404路由（必须在最后）
      router.addRoute({
        path: '/:pathMatch(.*)*',
        redirect: '/404',
      })
    }

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
        title: '无权限',
      },
    })

    // 检查是否已存在404路由，避免重复添加
    const existingNotFoundRoute = router
      .getRoutes()
      .find((route) => route.path === '/:pathMatch(.*)*')

    if (!existingNotFoundRoute) {
      // 仍然添加404路由
      router.addRoute({
        path: '/:pathMatch(.*)*',
        redirect: '/404',
      })
    }

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
      console.log('Token found but user not logged in, setting token')
      userStore.setToken(token)
    }

    // 只要有有效token就加载动态路由（修复页面刷新时动态路由丢失的问题）
    if (token && !routesAdded) {
      try {
        console.log('Loading dynamic routes for token:', token.substring(0, 20) + '...')
        await addDynamicRoutes()
        console.log('Dynamic routes loaded successfully')

        // 动态路由加载完成后，如果当前访问的路径不是基础路由，需要重新导航
        // 等待一个tick确保路由已经完全注册
        await new Promise(resolve => setTimeout(resolve, 0))
        
        if (
          to.path !== '/login' &&
          to.path !== '/403' &&
          to.path !== '/404' &&
          to.path !== '/dashboard' &&
          to.path !== '/' &&
          to.path !== '/profile'
        ) {
          console.log('Redirecting to current path after dynamic routes loaded:', to.path)
          next({ path: to.path, query: to.query, hash: to.hash, replace: true })
          return
        }
      } catch (error) {
        console.error('Failed to load dynamic routes:', error)
        // 如果动态路由加载失败，检查是否是token过期
        if (error && typeof error === 'object' && 'response' in error) {
          const errorResponse = error as any
          if (errorResponse.response?.status === 401) {
            console.log('Token expired, clearing user data and redirecting to login')
            userStore.clearUserData()
            next('/login')
            return
          }
        }
        // 其他错误重定向到404页面
        next('/404')
        return
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
