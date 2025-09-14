// Copyright (c) 2025 左岚. All rights reserved.

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { MenuApi } from '@/api/modules/menu'
import type { UserMenuTreeNode } from '@/api/types'

// 基础路由 - 不需要权限的路由
export const basicRoutes: RouteRecordRaw[] = [
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
      // 静态的仪表板路由
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/Index.vue'),
        meta: {
          title: '仪表板',
          icon: 'Monitor'
        }
      },
      // 个人中心路由
      {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/profile/Index.vue'),
        meta: {
          title: '个人中心',
          icon: 'User',
          hidden: true // 不在菜单中显示
        }
      }
      // 其他路由将通过动态路由添加
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
  }
]

// 空路由 - 用于没有权限时的占位
export const EMPTY_ROUTE: RouteRecordRaw = {
  path: '/',
  name: 'Empty',
  component: () => import('@/views/error/403.vue'),
  meta: {
    title: '无权限'
  }
}

// 404路由 - 用于匹配所有未定义的路由
export const NOT_FOUND_ROUTE: RouteRecordRaw = {
  path: '/:pathMatch(.*)*',
  redirect: '/404'
}

// 动态导入组件的映射
const vueModules = import.meta.glob('/src/views/**/*.vue')

/**
 * 根据后端返回的菜单数据构建前端路由
 */
function buildRoutes(routes: UserMenuTreeNode[] = [], parentPath = ''): RouteRecordRaw[] {
  const result: RouteRecordRaw[] = []

  routes.forEach((route) => {
    // 处理子路由的相对路径
    let routePath = route.path
    if (parentPath && routePath.startsWith(parentPath + '/')) {
      // 将绝对路径转换为相对路径
      routePath = routePath.replace(parentPath + '/', '')
    }

    const routeRecord: RouteRecordRaw = {
      name: route.name,
      path: routePath,
      component: getComponent(route.component),
      redirect: route.redirect,
      meta: {
        title: route.meta.title,
        icon: route.meta.icon,
        order: route.meta.order,
        hidden: route.meta.hidden,
        keepAlive: route.meta.keepAlive,
        permission: route.meta.permission,
        requiresAuth: true
      },
      children: []
    }

    if (route.children && route.children.length > 0) {
      // 有子菜单，递归构建子路由，传递当前路由的原始路径作为父路径
      routeRecord.children = buildRoutes(route.children, route.path)
    }

    result.push(routeRecord)
  })

  return result
}

/**
 * 获取组件
 */
function getComponent(componentPath?: string) {
  if (!componentPath) {
    // 对于没有组件的菜单（如菜单分组），返回router-view容器
    return () => import('@/components/Common/RouterView.vue')
  }

  if (componentPath === 'Layout') {
    // 动态路由中的Layout一律渲染为router-view，避免重复Layout嵌套
    return () => import('@/components/Common/RouterView.vue')
  }

  // 构建完整的组件路径
  const fullPath = `/src/views/${componentPath}.vue`
  const component = vueModules[fullPath]

  if (component) {
    return component
  }

  // 如果找不到组件，返回404页面
  console.warn(`Component not found: ${fullPath}`)
  return () => import('@/views/error/404.vue')
}

export const usePermissionStore = defineStore('permission', () => {
  // 状态
  const accessRoutes = ref<RouteRecordRaw[]>([])
  const accessApis = ref<string[]>([])
  const permissions = ref<string[]>([])

  // 计算属性
  const routes = computed(() => {
    return [...basicRoutes, ...accessRoutes.value]
  })

  const menus = computed(() => {
    return accessRoutes.value.filter((route) => route.name && !route.meta?.hidden)
  })

  const apis = computed(() => {
    return accessApis.value
  })

  // 方法
  const generateRoutes = async (): Promise<RouteRecordRaw[]> => {
    try {
      // 调用接口获取用户路由
      const response = await MenuApi.getUserRoutes()

      if (response.success && response.data) {
        // 处理成前端路由格式
        const dynamicRoutes = buildRoutes(response.data.routes)
        permissions.value = response.data.permissions || []

        // 将动态路由作为Layout的子路由返回
        accessRoutes.value = dynamicRoutes

        return dynamicRoutes
      } else {
        throw new Error(response.message || '获取用户路由失败')
      }
    } catch (error) {
      console.error('Error generating routes:', error)
      accessRoutes.value = []
      permissions.value = []
      throw error
    }
  }

  const getAccessApis = async (): Promise<string[]> => {
    try {
      // 这里可以调用获取用户API权限的接口
      // const response = await MenuApi.getUserApis()
      // accessApis.value = response.data || []
      
      // 暂时返回空数组，后续可以扩展
      accessApis.value = []
      return accessApis.value
    } catch (error) {
      console.error('Error getting access APIs:', error)
      accessApis.value = []
      return []
    }
  }

  const resetPermission = () => {
    accessRoutes.value = []
    accessApis.value = []
    permissions.value = []
  }

  const hasPermission = (permission: string): boolean => {
    return permissions.value.includes(permission)
  }

  return {
    // 状态
    accessRoutes,
    accessApis,
    permissions,
    
    // 计算属性
    routes,
    menus,
    apis,
    
    // 方法
    generateRoutes,
    getAccessApis,
    resetPermission,
    hasPermission
  }
}, {
  persist: {
    key: 'permission-store',
    storage: sessionStorage,
    pick: ['permissions'] // 只持久化权限信息
  }
})
