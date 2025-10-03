// Copyright (c) 2025 左岚. All rights reserved.
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { setupRouterGuards } from './guards'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表板', requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { title: '登录' }
  },
  // 系统管理
  {
    path: '/system',
    redirect: '/system/user',
    meta: { title: '系统管理', requiresAuth: true }
  },
  {
    path: '/system/user',
    name: 'SystemUser',
    component: () => import('@/views/system/UserManage.vue'),
    meta: { title: '用户管理', requiresAuth: true }
  },
  {
    path: '/system/role',
    name: 'SystemRole',
    component: () => import('@/views/system/RoleManage.vue'),
    meta: { title: '角色管理', requiresAuth: true }
  },
  {
    path: '/system/permission',
    name: 'SystemPermission',
    component: () => import('@/views/system/PermissionManage.vue'),
    meta: { title: '权限管理', requiresAuth: true }
  },
  // API自动化
  {
    path: '/api/testcase',
    name: 'ApiTestCase',
    component: () => import('@/views/api/TestCase.vue'),
    meta: { title: 'API测试用例', requiresAuth: true }
  },
  {
    path: '/api/execute',
    name: 'ApiExecute',
    component: () => import('@/views/api/Execute.vue'),
    meta: { title: 'API测试执行', requiresAuth: true }
  },
  {
    path: '/api/report',
    name: 'ApiReport',
    component: () => import('@/views/api/Report.vue'),
    meta: { title: 'API测试报告', requiresAuth: true }
  },
  // WEB自动化
  {
    path: '/web/testcase',
    name: 'WebTestCase',
    component: () => import('@/views/web/TestCase.vue'),
    meta: { title: 'WEB测试用例', requiresAuth: true }
  },
  {
    path: '/web/execute',
    name: 'WebExecute',
    component: () => import('@/views/web/Execute.vue'),
    meta: { title: 'WEB测试执行', requiresAuth: true }
  },
  {
    path: '/web/report',
    name: 'WebReport',
    component: () => import('@/views/web/Report.vue'),
    meta: { title: 'WEB测试报告', requiresAuth: true }
  },
  // APP自动化
  {
    path: '/app/testcase',
    name: 'AppTestCase',
    component: () => import('@/views/app/TestCase.vue'),
    meta: { title: 'APP测试用例', requiresAuth: true }
  },
  {
    path: '/app/execute',
    name: 'AppExecute',
    component: () => import('@/views/app/Execute.vue'),
    meta: { title: 'APP测试执行', requiresAuth: true }
  },
  {
    path: '/app/report',
    name: 'AppReport',
    component: () => import('@/views/app/Report.vue'),
    meta: { title: 'APP测试报告', requiresAuth: true }
  },
  // 消息通知
  {
    path: '/message/list',
    name: 'MessageList',
    component: () => import('@/views/message/List.vue'),
    meta: { title: '消息列表', requiresAuth: true }
  },
  {
    path: '/message/setting',
    name: 'MessageSetting',
    component: () => import('@/views/message/Setting.vue'),
    meta: { title: '通知设置', requiresAuth: true }
  },

  // 用户个人中心
  {
    path: '/user/profile',
    name: 'UserProfile',
    component: () => import('@/views/user/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  
  // 测试数据管理
  {
    path: '/data/testdata',
    name: 'TestData',
    component: () => import('@/views/data/TestData.vue'),
    meta: { title: '测试数据管理', requiresAuth: true }
  },
  
  // AI 功能
  {
    path: '/ai/chat',
    name: 'AIChat',
    component: () => import('@/views/ai/Chat.vue'),
    meta: { title: 'AI 助手', requiresAuth: true }
  },
  
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 设置路由守卫
setupRouterGuards(router)

export default router
