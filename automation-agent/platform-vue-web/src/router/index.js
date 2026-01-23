// 导入路由创建函数
import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Login from '~/views/login/login.vue'
import NotFound from '../views/NotFound.vue'  // 导入404组件
import About from '../views/pages/about.vue'  // 导入关于页面
import Home from '../views/home/home.vue' // 导入首页
import Statistics from '../views/statistics/statistics.vue'

// 导入动态路由工具
import { menusToRoutes, addRoutes } from '~/utils/router'

// 导入store
import store from '~/store'

// 标记是否已加载动态路由
let hasDynamicRoutes = false

// 路由规则数组
const routes = [
  {
    path: '/',          // 访问路径
    redirect: '/login'  // 自动重定向到'/login'路径
  }, {
    path: '/login',
    component: Login,
    meta: {
      title: '登录'
    }
  }, {
    path: '/about',
    component: About,
    meta: {
      title: '关于'
    }
  }, {
    path: '/home',
    component: Home,
    redirect: '/Statistics',
    meta: {
      title: '首页'
    },
    // 预留一些基础路由，其他路由将通过动态加载添加
    children: [
      {
        path: "/Statistics",
        component: Statistics,
        meta: {
          title: "数据统计",
          keepalive: true
        }
      },
      {
        path: "/profile",
        component: () => import('~/views/profile/profile.vue'),
        meta: {
          title: "个人中心",
          keepalive: true
        }
      },
      {
        path: "/settings",
        component: () => import('~/views/settings/settings.vue'),
        meta: {
          title: "系统设置",
          keepalive: false
        }
      }
    ]
  }, {
    // 通配符路由，匹配所有未定义的路径
    // 404页面必须放在最后
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: '页面未找到'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),  // 使用HTML5 history模式（无#号URL）
  routes                        // 路由规则
})

/**
 * 加载动态路由
 * @returns {Promise<boolean>} 是否加载成功
 */
async function loadDynamicRoutes() {
  try {
    // 如果已经加载过，直接返回
    if (hasDynamicRoutes) {
      return true
    }

    // 从store获取用户菜单
    const userMenus = store.state.userMenus || []

    // 如果没有菜单数据，先获取
    if (userMenus.length === 0) {
      await store.dispatch('getUserMenu')
    }

    // 再次检查菜单数据
    const menus = store.state.userMenus || []
    if (menus.length === 0) {
      console.warn('用户菜单数据为空，无法加载动态路由')
      return false
    }

    // 将菜单转换为路由
    const dynamicRoutes = menusToRoutes(menus)

    // 将动态路由添加到router中
    addRoutes(router, dynamicRoutes)

    // 标记已加载
    hasDynamicRoutes = true

    console.log(`成功加载 ${dynamicRoutes.length} 条动态路由`)
    return true

  } catch (error) {
    console.error('加载动态路由失败:', error)
    return false
  }
}

/**
 * 重置动态路由（登出时调用）
 */
export function resetDynamicRoutes() {
  hasDynamicRoutes = false
  // 注意：Vue Router 4不支持直接移除路由
  // 最好的做法是重新加载页面
}

// 全局前置守卫 - 验证用户登录状态和加载动态路由
router.beforeEach(async (to, from, next) => {
  // 获取 token
  const token = localStorage.getItem('token')

  // 定义需要登录才能访问的路径
  const publicPaths = ['/login', '/about']
  const isPublicPath = publicPaths.includes(to.path)

  if (isPublicPath) {
    // 公开路径，直接放行
    if (to.path === '/login' && token) {
      // 如果已登录且访问登录页，重定向到首页
      next('/home')
    } else {
      next()
    }
  } else {
    // 需要登录的路径
    if (!token) {
      // 未登录，重定向到登录页，并保存目标路径
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
      return
    }

    // 已登录，检查是否需要加载动态路由
    if (!hasDynamicRoutes) {
      try {
        const loaded = await loadDynamicRoutes()
        if (loaded) {
          // 重新导航到目标路由（因为可能刚刚添加了路由）
          next({ ...to, replace: true })
        } else {
          // 加载失败，重定向到默认首页
          next('/home')
        }
      } catch (error) {
        console.error('加载动态路由失败:', error)
        // 加载失败，仍然放行（使用默认路由）
        next('/home')
      }
    } else {
      // 已加载过动态路由，直接放行
      next()
    }
  }
})

// 导出路由实例（resetDynamicRoutes 已在上面导出）
export default router