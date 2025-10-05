// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 路由守卫
 */
import type { Router } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'

// 白名单 - 不需要登录就能访问的路由
const whiteList = ['/login', '/register', '/forgot-password']

export function setupRouterGuards(router: Router) {
  // 前置守卫
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // 检查是否已登录
    if (authStore.isAuthenticated) {
      // 已登录
      if (to.path === '/login') {
        // 如果已登录且要去登录页，重定向到首页
        next('/dashboard')
      } else {
        // 如果用户信息不存在，尝试获取
        if (!authStore.userInfo) {
          try {
            await authStore.fetchUserInfo()
          } catch (error) {
            console.error('Failed to fetch user info:', error)
            // 获取用户信息失败，清除认证状态并跳转登录
            authStore.clearAuth()
            ElMessage.error('获取用户信息失败，请重新登录')
            next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
            return
          }
        }

        // 检查是否需要特定权限
        if (to.meta.permission && !authStore.hasPermission(to.meta.permission as string)) {
          ElMessage.error('您没有权限访问此页面')
          next(from.path || '/dashboard')  // 确保有默认路径
          return
        }

        // 检查是否需要特定角色
        if (to.meta.roles) {
          const roles = to.meta.roles as string[]
          const hasRole = roles.some(role => authStore.hasRole(role))
          if (!hasRole) {
            ElMessage.error('您没有权限访问此页面')
            next(from.path || '/dashboard')  // 确保有默认路径
            return
          }
        }

        next()
      }
    } else {
      // 未登录
      if (whiteList.includes(to.path)) {
        // 在白名单中，直接放行
        next()
      } else {
        // 不在白名单中，重定向到登录页
        ElMessage.warning('请先登录')
        next(`/login?redirect=${encodeURIComponent(to.fullPath)}`)
      }
    }
  })

  // 后置守卫
  router.afterEach((to) => {
    // 设置页面标题
    document.title = (to.meta.title as string) || '华测自动化测试平台'
  })
}

