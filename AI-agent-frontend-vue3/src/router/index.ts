// Copyright (c) 2025 左岚. All rights reserved.
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { setupRouterGuards } from './guards'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { title: '登录' }
  },
  // 主布局路由
  {
    path: '/',
    name: 'MainLayout', // 添加name以便插件路由可以作为子路由添加
    component: () => import('@/components/Layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板', requiresAuth: true }
      },
      // 系统管理
      {
        path: 'system',
        redirect: '/system/user',
        meta: { title: '系统管理', requiresAuth: true }
      },
      {
        path: 'system/user',
        name: 'SystemUser',
        component: () => import('@/views/system/UserManage.vue'),
        meta: { title: '用户管理', requiresAuth: true }
      },
      {
        path: 'system/role',
        name: 'SystemRole',
        component: () => import('@/views/system/RoleManage.vue'),
        meta: { title: '角色管理', requiresAuth: true }
      },
      {
        path: 'system/menu',
        name: 'SystemMenu',
        component: () => import('@/views/system/MenuManage.vue'),
        meta: { title: '菜单管理', requiresAuth: true }
      },
      {
        path: 'system/department',
        name: 'SystemDepartment',
        component: () => import('@/views/system/DepartmentManage.vue'),
        meta: { title: '部门管理', requiresAuth: true }
      },
      // 消息通知
      {
        path: 'message/list',
        name: 'MessageList',
        component: () => import('@/views/message/List.vue'),
        meta: { title: '消息列表', requiresAuth: true }
      },
      {
        path: 'message/setting',
        name: 'MessageSetting',
        component: () => import('@/views/message/Setting.vue'),
        meta: { title: '通知设置', requiresAuth: true }
      },
      // 用户个人中心
      {
        path: 'user/profile',
        name: 'UserProfile',
        component: () => import('@/views/user/Profile.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      },
      // 测试数据管理
      {
        path: 'data/testdata',
        name: 'TestData',
        component: () => import('@/views/testdata/TestDataManagement.vue'),
        meta: { title: '测试数据管理', requiresAuth: true }
      },
      // 系统数据管理
      {
        path: 'data/management',
        name: 'DataManagement',
        component: () => import('@/views/data/Management.vue'),
        meta: { title: '数据管理', requiresAuth: true }
      },
      // AI 功能
      {
        path: 'ai/chat',
        name: 'AIChat',
        component: () => import('@/views/ai/ChatEnhanced.vue'),
        meta: { title: 'AI 助手', requiresAuth: true }
      },
      // 测试页面
      {
        path: 'test',
        name: 'TestPage',
        component: () => import('@/views/TestPage.vue'),
        meta: { title: '测试页面', requiresAuth: true }
      }
    ]
  },
  // 404页面
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
