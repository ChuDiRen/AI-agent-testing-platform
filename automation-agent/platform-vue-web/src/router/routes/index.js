/**
 * 路由配置 - 参考vue-fastapi-admin实现
 */

const Layout = () => import('@/layout/index.vue')

// 基础路由（无需权限）
export const basicRoutes = [
  {
    path: '/',
    redirect: '/workbench', // 默认跳转到工作台
    meta: { order: 0 },
  },
  {
    name: '个人中心',
    path: '/profile',
    component: Layout,
    isHidden: true,
    children: [
      {
        path: '',
        component: () => import('@/views/profile/index.vue'),
        name: '个人中心Default',
        meta: {
          title: '个人中心',
          icon: 'User',
          affix: true,
        },
      },
    ],
    meta: { order: 99 },
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/auth/login/login.vue'),
    isHidden: true,
    meta: { title: '登录页' },
  },
  {
    name: '404',
    path: '/404',
    component: () => import('@/views/NotFound.vue'),
    isHidden: true,
  },
]

// 404路由（必须最后添加）
export const NOT_FOUND_ROUTE = {
  name: 'NotFound',
  path: '/:pathMatch(.*)*',
  component: () => import('@/views/NotFound.vue'),
  isHidden: true,
  meta: { title: '页面未找到' },
}

// 动态加载views下所有index.vue组件
// 注意：import.meta.glob 返回的键格式取决于 Vite 配置
// 通常是相对于项目根目录的绝对路径，如 /src/views/xxx/index.vue
export const vueModules = import.meta.glob('/src/views/**/index.vue')

