/**
 * 路由配置 - 参考vue-fastapi-admin实现
 */

const Layout = () => import('@/layout/index.vue')

// 基础路由（无需权限）
export const basicRoutes = [
  {
    path: '/',
    redirect: '/home',
    meta: { order: 0 },
  },
  {
    name: '首页',
    path: '/home',
    component: Layout,
    children: [
      {
        path: '',
        component: () => import('@/views/home/dashboard.vue'),
        name: '首页Default',
        meta: { title: '首页', icon: 'HomeFilled', affix: true },
      },
    ],
    meta: { order: 1 },
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
        meta: { title: '个人中心', icon: 'User' },
      },
    ],
    meta: { order: 99 },
  },
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/auth/login/login.vue'),
    isHidden: true,
    meta: { title: '登录' },
  },
  {
    name: '关于',
    path: '/about',
    component: () => import('@/views/pages/about.vue'),
    isHidden: true,
    meta: { title: '关于' },
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
export const vueModules = import.meta.glob('@/views/**/index.vue')

