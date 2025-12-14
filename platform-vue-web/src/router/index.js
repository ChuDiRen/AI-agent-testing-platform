import {
    createRouter,
    createWebHashHistory
} from 'vue-router'

import NotFound from '~/views/404.vue'
import Forbidden from '~/views/403.vue'
import ServerError from '~/views/500.vue'
import Login from '~/views/login/login.vue'
import Home from '~/views/home/home.vue'
import Statistics from '~/views/statistics/statistics.vue'
import userList from '~/views/system/users/userList.vue'
import userForm from '~/views/system/users/userForm.vue'

// 系统管理相关导入
import roleList from '~/views/system/role/roleList.vue'
import roleForm from '~/views/system/role/roleForm.vue'
import menuList from '~/views/system/menu/menuList.vue'
import menuForm from '~/views/system/menu/menuForm.vue'
import deptList from '~/views/system/dept/deptList.vue'
import deptForm from '~/views/system/dept/deptForm.vue'

// API相关导入
import ApiProjectList from '~/views/apitest/project/ApiProjectList.vue'
import ApiProjectForm from '~/views/apitest/project/ApiProjectForm.vue'

import ApiKeyWordForm from '~/views/apitest/keyword/ApiKeyWordForm.vue'
import ApiKeyWordList from '~/views/apitest/keyword/ApiKeyWordList.vue'

import ApiMetaForm from '~/views/apitest/apimeta/ApiMetaForm.vue'
import ApiMetaList from '~/views/apitest/apimeta/ApiMetaList.vue'

// 接口信息管理相关导入
import ApiInfoList from '~/views/apitest/apiinfo/ApiInfoList.vue'
import ApiInfoForm from '~/views/apitest/apiinfo/ApiInfoForm.vue'
import ApiInfoEditor from '~/views/apitest/apiinfo/ApiInfoEditor.vue'

// 测试执行相关导入（apitest目录仅包含JS工具函数）
// import ApiTestList from '~/views/apitest/apitest/ApiTestList.vue'  // 已移除，使用ApiHistoryList代替

// 用例管理相关导入（已重命名）
import ApiInfoCaseList from '~/views/apitest/apiinfocase/ApiInfoCaseList.vue'
import ApiInfoCaseForm from '~/views/apitest/apiinfocase/ApiInfoCaseForm.vue'

// 测试计划相关导入
import TestPlanList from '~/views/apitest/testplan/TestPlanList.vue'
import TestPlanForm from '~/views/apitest/testplan/TestPlanForm.vue'

// 测试任务相关导入
import TestTaskList from '~/views/apitest/task/TestTaskList.vue'
import TestTaskForm from '~/views/apitest/task/TestTaskForm.vue'

// 测试历史相关导入（已重命名）
import ApiHistoryList from '~/views/apitest/history/ApiHistoryList.vue'
import ApiHistoryDetail from '~/views/apitest/history/ApiHistoryDetail.vue'

// 数据库配置相关导入
import ApiDbBaseList from '~/views/apitest/database/ApiDbBaseList.vue'
import ApiDbBaseForm from '~/views/apitest/database/ApiDbBaseForm.vue'

// 报告查看器
import ApiReportViewer from '~/views/apitest/report/ApiReportViewer.vue'

// 测试执行监控
import TestExecutionView from '~/views/apitest/execution/TestExecutionView.vue'

// AI测试助手模块相关导入
import AiModelList from '~/views/aiassistant/model/AiModelList.vue'
import AiModelForm from '~/views/aiassistant/model/AiModelForm.vue'
import PromptTemplateList from '~/views/aiassistant/prompt/PromptTemplateList.vue'
import PromptTemplateForm from '~/views/aiassistant/prompt/PromptTemplateForm.vue'
import TestCaseList from '~/views/aiassistant/testcase/TestCaseList.vue'
import TestCaseForm from '~/views/aiassistant/testcase/TestCaseForm.vue'
import AgentChatIntegrated from '~/views/aiassistant/agentchat/AgentChatIntegrated.vue'

// 消息管理模块相关导入
import RobotConfigList from '~/views/msgmanage/robot/RobotConfigList.vue'
import RobotConfigForm from '~/views/msgmanage/robot/RobotConfigForm.vue'
import RobotMsgConfigList from '~/views/msgmanage/template/RobotMsgConfigList.vue'
import RobotMsgConfigForm from '~/views/msgmanage/template/RobotMsgConfigForm.vue'

// 代码生成器相关导入
import GenTableList from '~/views/generator/table/GenTableList.vue'
import GeneratorCode from '~/views/generator/code/GeneratorCode.vue'
import GenHistory from '~/views/generator/history/GenHistory.vue'

// 插件管理相关导入
import PluginMarket from '~/views/plugin/PluginMarket.vue'

// 获取 token
function getToken() {
    return localStorage.getItem('token')
}

const routes = [
    {
        path: '/',
        redirect: '/login'
    }, {
        path: "/login",
        component: Login
    }, {
        path: "/home",
        component: Home,
        redirect: '/Statistics', // 默认重定向到系统总览页面
        //子路由概念，后续所有的子页面都要放在这里
        children: [{
            path: "/Statistics",
            component: Statistics,
            meta: {
                title: "主页信息"
            }
        }, {
            path: "/userList",
            component: userList,
            meta: {
                title: "用户管理",
                permission: "system:user:query"
            }
        }, {
            path: "/system/user",
            component: userList,
            meta: {
                title: "用户管理",
                permission: "system:user:list"
            }
        }, {
            path: "/userForm",
            component: userForm,
            meta: {
                title: "用户表单",
                permission: "system:user:add"
            }
        }, {
            path: "/roleList",
            component: roleList,
            meta: {
                title: "角色管理",
                permission: "system:role:query"
            }
        }, {
            path: "/system/role",
            component: roleList,
            meta: {
                title: "角色管理",
                permission: "system:role:list"
            }
        }, {
            path: "/roleForm",
            component: roleForm,
            meta: {
                title: "角色表单",
                permission: "system:role:add"
            }
        }, {
            path: "/menuList",
            component: menuList,
            meta: {
                title: "菜单管理",
                permission: "system:menu:query"
            }
        }, {
            path: "/system/menu",
            component: menuList,
            meta: {
                title: "菜单管理",
                permission: "system:menu:list"
            }
        }, {
            path: "/menuForm",
            component: menuForm,
            meta: {
                title: "菜单表单",
                permission: "system:menu:add"
            }
        }, {
            path: "/deptList",
            component: deptList,
            meta: {
                title: "部门管理",
                permission: "system:dept:query"
            }
        }, {
            path: "/system/dept",
            component: deptList,
            meta: {
                title: "部门管理",
                permission: "system:dept:list"
            }
        }, {
            path: "/deptForm",
            component: deptForm,
            meta: {
                title: "部门表单",
                permission: "system:dept:add"
            }
        }, {
            path: "/ApiProjectList",
            component: ApiProjectList,
            meta: {
                title: "项目列表",
                permission: "apitest:project:query"
            }
        }, {
            path: "/apitest/project",
            component: ApiProjectList,
            meta: {
                title: "项目管理",
                permission: "apitest:project:list"
            }
        }, {
            path: "/ApiProjectForm",
            component: ApiProjectForm,
            meta: {
                title: "项目操作",
                permission: "apitest:project:add"
            }
        }, {
            path: "/ApiKeyWordForm",
            component: ApiKeyWordForm,
            meta: {
                title: "关键字编辑页面",
                permission: "apitest:keyword:add"
            }
        }, {
            path: "/ApiKeyWordList",
            component: ApiKeyWordList,
            meta: {
                title: "关键字列表页面",
                permission: "apitest:keyword:query"
            }
        }, {
            path: "/apitest/keyword",
            component: ApiKeyWordList,
            meta: {
                title: "关键字管理",
                permission: "apitest:keyword:list"
            }
        }, {
            path: "/ApiMetaForm",
            component: ApiMetaForm,
            meta: {
                title: "素材编辑",
                permission: "apitest:meta:add"
            }
        }, {
            path: "/ApiMetaList",
            component: ApiMetaList,
            meta: {
                title: "素材列表",
                permission: "apitest:meta:query"
            }
        }, {
            path: "/apitest/meta",
            component: ApiMetaList,
            meta: {
                title: "素材管理",
                permission: "apitest:meta:list"
            }
        }, {
            path: "/ApiInfoList",
            component: ApiInfoList,
            meta: {
                title: "接口信息管理",
                permission: "apitest:api:query"
            }
        }, {
            path: "/apitest/apiinfo",
            component: ApiInfoList,
            meta: {
                title: "接口信息",
                permission: "apitest:apiinfo:list"
            }
        }, {
            path: "/ApiInfoForm",
            component: ApiInfoForm,
            meta: {
                title: "接口信息表单",
                permission: "apitest:api:add"
            }
        }, {
            path: "/ApiInfoEditor",
            component: ApiInfoEditor,
            meta: {
                title: "接口测试编辑器",
                permission: "apitest:api:execute"
            }
        }, {
            path: "/ApiHistoryList",
            component: ApiHistoryList,
            meta: {
                title: "测试历史记录",
                permission: "apitest:history:query"
            }
        }, {
            path: "/apitest/testhistory",
            component: ApiHistoryList,
            meta: {
                title: "测试历史",
                permission: "apitest:testhistory:list"
            }
        }, {
            path: "/ApiTestHistory",
            component: ApiHistoryList,
            meta: {
                title: "测试历史",
                permission: "apitest:testhistory:list"
            }
        }, {
            path: "/ApiHistoryDetail/:id",
            component: ApiHistoryDetail,
            meta: {
                title: "测试历史详情",
                permission: "apitest:history:query"
            }
        }, {
            path: "/ApiDbBaseList",
            component: ApiDbBaseList,
            meta: {
                title: "数据库配置",
                permission: "apitest:database:query"
            }
        }, {
            path: "/ApiDbBaseForm",
            component: ApiDbBaseForm,
            meta: {
                title: "数据库配置表单",
                permission: "apitest:database:add"
            }
        }, {
            path: "/ApiReportViewer",
            component: ApiReportViewer,
            meta: {
                title: "测试报告查看器"
                // 报告查看器无需权限,公开访问
            }
        }, {
            path: "/ApiInfoCaseList",
            component: ApiInfoCaseList,
            meta: {
                title: "用例管理",
                permission: "apitest:case:query"
            }
        }, {
            path: "/ApiInfoCaseForm",
            component: ApiInfoCaseForm,
            meta: {
                title: "用例表单",
                permission: "apitest:case:add"
            }
        }, {
            path: "/TestPlanList",
            component: TestPlanList,
            meta: {
                title: "测试计划",
                permission: "apitest:plan:query"
            }
        }, {
            path: "/TestPlanForm",
            component: TestPlanForm,
            meta: {
                title: "测试计划表单",
                permission: "apitest:plan:add"
            }
        }, {
            path: "/apitest/plan",
            component: TestPlanList,
            meta: {
                title: "测试计划",
                permission: "apitest:plan:list"
            }
        }, {
            path: "/TestTaskList",
            component: TestTaskList,
            meta: {
                title: "测试任务",
                permission: "apitest:task:query"
            }
        }, {
            path: "/TestTaskForm",
            component: TestTaskForm,
            meta: {
                title: "测试任务表单",
                permission: "apitest:task:add"
            }
        }, {
            path: "/apitest/task",
            component: TestTaskList,
            meta: {
                title: "测试任务",
                permission: "apitest:task:list"
            }
        }, {
            path: "/RobotConfigList",
            component: RobotConfigList,
            meta: {
                title: "机器人配置",
                permission: "msgmanage:robot:query"
            }
        }, {
            path: "/RobotConfigForm",
            component: RobotConfigForm,
            meta: {
                title: "机器人配置表单",
                permission: "msgmanage:robot:add"
            }
        }, {
            path: "/RobotMsgConfigList",
            component: RobotMsgConfigList,
            meta: {
                title: "消息模板管理",
                permission: "msgmanage:template:query"
            }
        }, {
            path: "/RobotMsgConfigForm",
            component: RobotMsgConfigForm,
            meta: {
                title: "消息模板表单",
                permission: "msgmanage:template:add"
            }
        }, {
            path: "/TestExecutionView",
            component: TestExecutionView,
            meta: {
                title: "测试执行监控",
                permission: "apitest:history:query"
            }
        }, {
            path: "/AiModelList",
            component: AiModelList,
            meta: {
                title: "AI模型管理",
                permission: "ai:model:list"
            }
        }, {
            path: "/AiModelForm",
            component: AiModelForm,
            meta: {
                title: "AI模型表单",
                permission: "ai:model:add"
            }
        }, {
            path: "/PromptTemplateList",
            component: PromptTemplateList,
            meta: {
                title: "提示词模板管理",
                permission: "ai:prompt:list"
            }
        }, {
            path: "/PromptTemplateForm",
            component: PromptTemplateForm,
            meta: {
                title: "提示词模板表单",
                permission: "ai:prompt:add"
            }
        }, {
            path: "/AgentChatIntegrated",
            component: AgentChatIntegrated,
            meta: {
                title: "智能体聊天",
                permission: "ai:agent:chat"
            }
        }, {
            path: "/AgentChatEnhanced",
            component: AgentChatIntegrated,
            meta: {
                title: "LangGraph测试用例生成",
                permission: "ai:agent:chat"
            }
        }, {
            path: "/ai/langgraph",
            component: AgentChatIntegrated,
            meta: {
                title: "LangGraph智能生成",
                permission: "ai:agent:chat"
            }
        }, {
            path: "/TestCaseList",
            component: TestCaseList,
            meta: {
                title: "测试用例管理",
                permission: "ai:testcase:list"
            }
        }, {
            path: "/TestCaseForm",
            component: TestCaseForm,
            meta: {
                title: "测试用例表单",
                permission: "ai:testcase:add"
            }
        }, {
            path: "/GenTableList",
            component: GenTableList,
            meta: {
                title: "表配置管理",
                permission: "generator:table:list"
            }
        }, {
            path: "/generator/table",
            component: GenTableList,
            meta: {
                title: "表配置",
                permission: "generator:table:list"
            }
        }, {
            path: "/GeneratorCode",
            component: GeneratorCode,
            meta: {
                title: "代码生成",
                permission: "generator:code:generate"
            }
        }, {
            path: "/generator/code",
            component: GeneratorCode,
            meta: {
                title: "代码生成",
                permission: "generator:code:list"
            }
        }, {
            path: "/GenHistory",
            component: GenHistory,
            meta: {
                title: "生成历史",
                permission: "generator:history:list"
            }
        }, {
            path: "/generator/history",
            component: GenHistory,
            meta: {
                title: "生成历史",
                permission: "generator:history:list"
            }
        }, {
            path: "/PluginMarket",
            component: PluginMarket,
            meta: {
                title: "插件市场",
                permission: "plugin:market:list"
            }
        }, {
            path: "/plugin/market",
            component: PluginMarket,
            meta: {
                title: "插件市场",
                permission: "plugin:market:list"
            }
        }, {
            path: "/plugin/PluginMarket",
            component: PluginMarket,
            meta: {
                title: "插件市场",
                permission: "plugin:market:list"
            }
        }]
    },
    // 403 无权限访问
    {
        path: '/403',
        name: 'Forbidden',
        component: Forbidden
    },
    // 500 服务器错误
    {
        path: '/500',
        name: 'ServerError',
        component: ServerError
    },
    // 最后匹配不到的 都返回 404 !!!
    {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: NotFound
    }
]

/** */
const router = createRouter({
    history: createWebHashHistory(),
    routes
})

// 已删除的路由列表
const deletedRoutes = ['/ai-chat', '/langgraph-chat']

// 权限检查函数
function checkPermission(permission) {
    try {
        // 从localStorage获取用户名
        const username = localStorage.getItem('username')

        // 超级管理员直接放行（admin用户拥有所有权限）
        if (username === 'admin') {
            console.log('超级管理员，跳过权限检查')
            return true
        }

        // 从localStorage获取用户权限列表
        const userPermissions = JSON.parse(localStorage.getItem('permissions') || '[]')

        // 检查是否有该权限
        const hasPermission = userPermissions.includes(permission)
        if (!hasPermission) {
            console.warn(`权限检查失败: 需要 ${permission}, 当前权限:`, userPermissions)
        }

        return hasPermission
    } catch (e) {
        console.error('权限检查失败:', e)
        return false
    }
}

//导航判断逻辑
router.beforeEach((to, from, next) => {
    const token = getToken();

    // 如果访问已删除的路由，重定向到首页
    if (deletedRoutes.includes(to.path)) {
        next('/Statistics')
        return
    }

    if (to.path === '/login') {
        // 如果要前往登录页面，无需检查 token，直接跳转
        next();
    } else {
        // 如果不是前往登录页面，检查 token 是否存在
        if (token) {
            // 检查权限
            if (to.meta.permission) {
                if (!checkPermission(to.meta.permission)) {
                    console.warn(`权限不足: 需要 ${to.meta.permission}`)
                    next('/403')
                    return
                }
            }

            // 设置页面标题
            if (to.meta.title) {
                document.title = `${to.meta.title} - AI Agent Testing Platform`
            }

            // 如果 token 存在且有权限，允许继续导航
            next();
        } else {
            // 如果 token 不存在，重定向到登录页面
            next('/login');
        }
    }
})

// 全局后置守卫
router.afterEach((to, from) => {
    // 页面滚动到顶部
    window.scrollTo(0, 0)
})

export default router