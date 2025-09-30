import Layout from '@/layout/index.vue'

// 动态导入所有视图组件
export const vueModules = import.meta.glob('/src/views/**/index.vue')

// 基础路由
export const basicRoutes = [
  {
    name: 'Login',
    path: '/login',
    component: () => import('@/views/login/index.vue'),
    isHidden: true,
    meta: {
      title: '登录',
    },
  },
  {
    name: 'Layout',
    path: '/',
    component: Layout,
    redirect: '/workbench',
    isHidden: true, // 隐藏Layout路由，不在菜单中显示
    meta: {
      title: '首页',
    },
    children: [
      {
        name: 'Workbench',
        path: '/workbench',
        component: () => import('@/views/workbench/index.vue'),
        isHidden: true, // 隐藏基础工作台路由，使用动态路由
        meta: {
          title: '工作台',
          icon: 'mdi:view-dashboard',
        },
      },
    ],
  },
]

// 空路由
export const EMPTY_ROUTE = {
  name: 'Empty',
  path: '/:pathMatch(.*)*',
  component: () => import('@/views/error-page/404.vue'),
}

// 404路由
export const NOT_FOUND_ROUTE = {
  name: 'NotFound',
  path: '/:pathMatch(.*)*',
  component: () => import('@/views/error-page/404.vue'),
  isHidden: true,
  meta: {
    title: '页面不存在',
  },
}
