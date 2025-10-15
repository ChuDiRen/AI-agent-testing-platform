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
      // 知识库
      {
        path: 'knowledge',
        name: 'KnowledgeBase',
        component: () => import('@/views/knowledge/KnowledgeBase.vue'),
        meta: { title: '知识库', requiresAuth: true }
      },
      {
        path: 'knowledge/:id',
        name: 'KnowledgeDetail',
        component: () => import('@/views/knowledge/KnowledgeDetail.vue'),
        meta: { title: '知识库详情', requiresAuth: true, hidden: true }
      },
      // 测试用例
      {
        path: 'testcase/list',
        name: 'TestCaseList',
        component: () => import('@/views/testcase/TestCaseList.vue'),
        meta: { title: '测试用例', requiresAuth: true }
      },
      {
        path: 'testcase/create',
        name: 'TestCaseCreate',
        component: () => import('@/views/testcase/TestCaseEditor.vue'),
        meta: { title: '创建用例', requiresAuth: true, hidden: true }
      },
      {
        path: 'testcase/:id',
        name: 'TestCaseDetail',
        component: () => import('@/views/testcase/TestCaseDetail.vue'),
        meta: { title: '用例详情', requiresAuth: true, hidden: true }
      },
      // 测试报告
      {
        path: 'report/list',
        name: 'ReportList',
        component: () => import('@/views/report/ReportList.vue'),
        meta: { title: '测试报告', requiresAuth: true }
      },
      {
        path: 'report/generate',
        name: 'ReportGenerate',
        component: () => import('@/views/report/ReportGenerator.vue'),
        meta: { title: '生成报告', requiresAuth: true, hidden: true }
      },
      {
        path: 'report/:id',
        name: 'ReportDetail',
        component: () => import('@/views/report/ReportDetail.vue'),
        meta: { title: '报告详情', requiresAuth: true, hidden: true }
      },
      // 测试页面
      {
        path: 'test',
        name: 'TestPage',
        component: () => import('@/views/TestPage.vue'),
        meta: { title: '测试页面', requiresAuth: true }
      },
      // API 引擎（静态注册，避免刷新404）
      {
        path: '/plugin/api-engine',
        redirect: '/plugin/api-engine/suites',
        meta: { title: 'API引擎', requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/suites',
        name: 'ApiEngineSuiteList',
        component: () => import('@/plugins/api-engine/views/SuiteList.vue'),
        meta: { title: '测试套件', requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/suites/:id',
        name: 'ApiEngineSuiteDetail',
        component: () => import('@/plugins/api-engine/views/SuiteDetail.vue'),
        meta: { title: '套件详情', hidden: true, requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/cases',
        name: 'ApiEngineCaseList',
        component: () => import('@/plugins/api-engine/views/CaseList.vue'),
        meta: { title: '用例管理', requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/cases/create',
        name: 'ApiEngineCaseCreate',
        component: () => import('@/plugins/api-engine/views/CaseEditor.vue'),
        meta: { title: '创建用例', hidden: true, requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/cases/:id/edit',
        name: 'ApiEngineCaseEdit',
        component: () => import('@/plugins/api-engine/views/CaseEditor.vue'),
        meta: { title: '编辑用例', hidden: true, requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/executions',
        name: 'ApiEngineExecutionHistory',
        component: () => import('@/plugins/api-engine/views/ExecutionHistory.vue'),
        meta: { title: '执行历史', requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/batch-execution',
        name: 'ApiEngineBatchExecution',
        component: () => import('@/plugins/api-engine/views/BatchExecution.vue'),
        meta: { title: '批量执行', requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/executions/:id',
        name: 'ApiEngineExecutionDetail',
        component: () => import('@/plugins/api-engine/views/ExecutionConsole.vue'),
        meta: { title: '执行详情', hidden: true, requiresAuth: true }
      },
      {
        path: '/plugin/api-engine/keywords',
        name: 'ApiEngineKeywordManage',
        component: () => import('@/plugins/api-engine/views/KeywordManage.vue'),
        meta: { title: '关键字管理', requiresAuth: true }
      },

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
