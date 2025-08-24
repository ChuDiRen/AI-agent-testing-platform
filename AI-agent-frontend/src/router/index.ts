import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store'
import { ElMessage } from 'element-plus'

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
    redirect: '/dashboard',
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: {
          title: '仪表板',
          icon: 'Monitor'
        }
      },
      {
        path: '/system',
        name: 'System',
        meta: {
          title: '系统管理',
          icon: 'Setting'
        },
        children: [
          {
            path: '/system/user',
            name: 'UserManagement',
            component: () => import('@/views/system/user/Index.vue'),
            meta: {
              title: '用户管理',
              permission: 'user:view'
            }
          },
          {
            path: '/system/role',
            name: 'RoleManagement',
            component: () => import('@/views/system/role/Index.vue'),
            meta: {
              title: '角色管理',
              permission: 'role:view'
            }
          },
          {
            path: '/system/menu',
            name: 'MenuManagement',
            component: () => import('@/views/system/menu/Index.vue'),
            meta: {
              title: '菜单管理',
              permission: 'menu:view'
            }
          },
          {
            path: '/system/department',
            name: 'DepartmentManagement',
            component: () => import('@/views/system/department/Index.vue'),
            meta: {
              title: '部门管理',
              permission: 'dept:view'
            }
          }
        ]
      },
      // {
      //   path: '/test',
      //   name: 'Test',
      //   meta: {
      //     title: '测试管理',
      //     icon: 'DataAnalysis'
      //   },
      //   children: [
      //     {
      //       path: '/test/cases',
      //       name: 'TestCases',
      //       component: () => import('@/views/test/cases/Index.vue'),
      //       meta: {
      //         title: '测试用例'
      //       }
      //     },
      //     {
      //       path: '/test/reports',
      //       name: 'TestReports',
      //       component: () => import('@/views/test/reports/Index.vue'),
      //       meta: {
      //         title: '测试报告'
      //       }
      //     }
      //   ]
      // },
      {
        path: '/agent',
        name: 'Agent',
        meta: {
          title: 'AI代理管理',
          icon: 'Cpu'
        },
        children: [
          {
            path: '/agent/list',
            name: 'AgentList',
            component: () => import('@/views/agent/list/Index.vue'),
            meta: {
              title: '代理列表'
            }
          },
          {
            path: '/agent/config',
            name: 'AgentConfig',
            component: () => import('@/views/agent/config/Index.vue'),
            meta: {
              title: '代理配置'
            }
          }
        ]
      },
      {
        path: '/logs',
        name: 'Logs',
        component: () => import('@/views/logs/Index.vue'),
        meta: {
          title: '日志管理',
          icon: 'Operation'
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
  history: createWebHashHistory(),
  routes,
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AI智能代理测试平台`
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    if (!userStore.isLoggedIn) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
    
    // 检查权限
    if (to.meta.permission && !userStore.hasPermission(to.meta.permission as string)) {
      ElMessage.error('权限不足')
      next('/403')
      return
    }
  }
  
  // 如果已登录，访问登录页面则跳转到首页
  if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
    return
  }
  
  next()
})

export default router
