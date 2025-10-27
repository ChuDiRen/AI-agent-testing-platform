import {
    createRouter,
    createWebHashHistory
} from 'vue-router'
import { useCookies } from '@vueuse/integrations/useCookies';

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

import ApiMateForm from '~/views/apitest/apimate/ApiMateForm.vue'
import ApiMateList from '~/views/apitest/apimate/ApiMateList.vue'

// 接口信息管理相关导入
import ApiInfoList from '~/views/apitest/apiinfo/ApiInfoList.vue'
import ApiInfoForm from '~/views/apitest/apiinfo/ApiInfoForm.vue'
import ApiInfoEditor from '~/views/apitest/apiinfo/ApiInfoEditor.vue'

// 接口分组管理相关导入
import ApiGroupList from '~/views/apitest/apigroup/ApiGroupList.vue'
import ApiGroupForm from '~/views/apitest/apigroup/ApiGroupForm.vue'

// 测试历史相关导入
import ApiTestList from '~/views/apitest/apitest/ApiTestList.vue'

// AI测试助手模块相关导入
import AiChatInterface from '~/views/aiassistant/chat/AiChatInterface.vue'
import AiModelList from '~/views/aiassistant/model/AiModelList.vue'
import PromptTemplateList from '~/views/aiassistant/prompt/PromptTemplateList.vue'
import TestCaseList from '~/views/aiassistant/testcase/TestCaseList.vue'
import LangGraphChat from '~/views/aiassistant/langgraph/LangGraphChat.vue'

const cookies = useCookies()
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
                title: "用户管理"
            }
        }, {
            path: "/userForm",
            component: userForm,
            meta: {
                title: "用户表单"
            }
        }, {
            path: "/roleList",
            component: roleList,
            meta: {
                title: "角色管理"
            }
        }, {
            path: "/roleForm",
            component: roleForm,
            meta: {
                title: "角色表单"
            }
        }, {
            path: "/menuList",
            component: menuList,
            meta: {
                title: "菜单管理"
            }
        }, {
            path: "/menuForm",
            component: menuForm,
            meta: {
                title: "菜单表单"
            }
        }, {
            path: "/deptList",
            component: deptList,
            meta: {
                title: "部门管理"
            }
        }, {
            path: "/deptForm",
            component: deptForm,
            meta: {
                title: "部门表单"
            }
        }, {
            path: "/ApiProjectList",
            component: ApiProjectList,
            meta: {
                title: "项目列表"
            }
        }, {
            path: "/ApiProjectForm",
            component: ApiProjectForm,
            meta: {
                title: "项目操作"
            }
        }, {
            path: "/ApiKeyWordForm",
            component: ApiKeyWordForm,
            meta: {
                title: "关键字编辑页面"
            }
        }, {
            path: "/ApiKeyWordList",
            component: ApiKeyWordList,
            meta: {
                title: "关键字列表页面"
            }
        }, {
            path: "/ApiMateManageForm",
            component: ApiMateForm,
            meta: {
                title: "素材维护管理编辑页面"
            }
        }, {
            path: "/ApiMateManageList",
            component: ApiMateList,
            meta: {
                title: "素材维护管列表页面"
            }
        }, {
            path: "/ApiInfoList",
            component: ApiInfoList,
            meta: {
                title: "接口信息管理"
            }
        }, {
            path: "/ApiInfoForm",
            component: ApiInfoForm,
            meta: {
                title: "接口信息表单"
            }
        }, {
            path: "/ApiInfoEditor",
            component: ApiInfoEditor,
            meta: {
                title: "接口测试编辑器"
            }
        }, {
            path: "/ApiGroupList",
            component: ApiGroupList,
            meta: {
                title: "接口分组管理"
            }
        }, {
            path: "/ApiGroupForm",
            component: ApiGroupForm,
            meta: {
                title: "接口分组表单"
            }
        }, {
            path: "/ApiTestHistory",
            component: ApiTestList,
            meta: {
                title: "测试历史记录"
            }
        }, {
            path: "/ai-chat",
            component: AiChatInterface,
            meta: {
                title: "AI测试助手"
            }
        }, {
            path: "/test-cases",
            component: TestCaseList,
            meta: {
                title: "测试用例管理"
            }
        }, {
            path: "/ai-models",
            component: AiModelList,
            meta: {
                title: "AI模型管理"
            }
        }, {
            path: "/ai-prompts",
            component: PromptTemplateList,
            meta: {
                title: "提示词模板管理"
            }
        }, {
            path: "/langgraph-chat",
            component: LangGraphChat,
            meta: {
                title: "LangGraph 智能对话"
            }
        }
        ]
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
    }]

/** */
const router = createRouter({
    history: createWebHashHistory(),
    routes
})

//导航判断逻辑
router.beforeEach((to, from, next) => {
    const token = cookies.get("l-token");
    if (to.path === '/login') {
        // 如果要前往登录页面，无需检查 token，直接跳转
        next();
    } else {
        // 如果不是前往登录页面，检查 token 是否存在
        if (token) {
            // 如果 token 存在，允许继续导航
            next();
        } else {
            // 如果 token 不存在，重定向到登录页面
            next('/login');
        }
    }
})

export default router