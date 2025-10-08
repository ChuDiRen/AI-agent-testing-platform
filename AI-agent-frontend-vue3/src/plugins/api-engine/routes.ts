/**
 * API引擎插件 - 路由配置
 */
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
    {
        path: '/plugin/api-engine',
        redirect: '/plugin/api-engine/suites',
        meta: { requiresAuth: true }
    },
    {
        path: '/plugin/api-engine/suites',
        name: 'ApiEngineSuiteList',
        component: () => import('./views/SuiteList.vue'),
        meta: {
            title: '测试套件',
            icon: 'FolderOutlined',
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/suites/:id',
        name: 'ApiEngineSuiteDetail',
        component: () => import('./views/SuiteDetail.vue'),
        meta: {
            title: '套件详情',
            hidden: true,
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/cases',
        name: 'ApiEngineCaseList',
        component: () => import('./views/CaseList.vue'),
        meta: {
            title: '用例管理',
            icon: 'FileTextOutlined',
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/cases/create',
        name: 'ApiEngineCaseCreate',
        component: () => import('./views/CaseEditor.vue'),
        meta: {
            title: '创建用例',
            hidden: true,
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/cases/:id/edit',
        name: 'ApiEngineCaseEdit',
        component: () => import('./views/CaseEditor.vue'),
        meta: {
            title: '编辑用例',
            hidden: true,
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/executions',
        name: 'ApiEngineExecutionHistory',
        component: () => import('./views/ExecutionHistory.vue'),
        meta: {
            title: '执行历史',
            icon: 'HistoryOutlined',
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/executions/:id',
        name: 'ApiEngineExecutionDetail',
        component: () => import('./views/ExecutionConsole.vue'),
        meta: {
            title: '执行详情',
            hidden: true,
            requiresAuth: true
        }
    },
    {
        path: '/plugin/api-engine/keywords',
        name: 'ApiEngineKeywordManage',
        component: () => import('./views/KeywordManage.vue'),
        meta: {
            title: '关键字管理',
            icon: 'CodeOutlined',
            requiresAuth: true
        }
    }
]

export default routes
