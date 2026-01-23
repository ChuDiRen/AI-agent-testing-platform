import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/auth/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPassword.vue'),
    meta: { title: '忘记密码' }
  },
  {
    path: '/login',
    redirect: '/auth/login'
  },
  {
    path: '/register',
    redirect: '/auth/register'
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '工作台' }
  },
  {
    path: '/agents/create',
    name: 'AgentCreate',
    component: () => import('@/views/agents/AgentForm.vue'),
    meta: { title: '创建代理' }
  },
  {
    path: '/agents',
    name: 'AgentList',
    component: () => import('@/views/agents/AgentList.vue'),
    meta: { title: '智能代理' }
  },
  {
    path: '/workflows',
    name: 'WorkflowList',
    component: () => import('@/views/workflows/WorkflowList.vue'),
    meta: { title: '工作流' }
  },
  {
    path: '/workflows/create',
    name: 'WorkflowCreate',
    component: () => import('@/views/workflows/WorkflowCreate.vue'),
    meta: { title: '创建工作流' }
  },
  {
    path: '/workflows/:id/editor',
    name: 'WorkflowEditor',
    component: () => import('@/views/workflows/WorkflowEditor.vue'),
    meta: { title: '工作流编辑器' }
  },
  {
    path: '/tools',
    name: 'ToolList',
    component: () => import('@/views/tools/ToolList.vue'),
    meta: { title: '工具管理' }
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: () => import('@/views/monitoring/Monitoring.vue'),
    meta: { title: '执行监控' }
  },
  {
    path: '/billing',
    name: 'Billing',
    component: () => import('@/views/billing/Billing.vue'),
    meta: { title: '计费统计' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查身份验证
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 检查是否是公共路由（登录、注册、忘记密码）
  const publicRoutes = ['/auth/login', '/auth/register', '/auth/forgot-password']
  const isPublicRoute = publicRoutes.includes(to.path)
  
  // 如果用户未登录且访问的不是公共路由，重定向到登录页
  if (!authStore.isAuthenticated && !isPublicRoute) {
    next('/auth/login')
  } 
  // 如果用户已登录且访问登录页，重定向到工作台
  else if (authStore.isAuthenticated && isPublicRoute) {
    next('/')
  }
  // 否则正常导航
  else {
    next()
  }
})

export default router
