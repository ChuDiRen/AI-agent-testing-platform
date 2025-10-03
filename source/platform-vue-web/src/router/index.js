import {
    createRouter,
    createWebHashHistory
} from 'vue-router'
import { useCookies } from '@vueuse/integrations/useCookies';

import NotFound from '~/views/404.vue'
import Login from '~/views/login/login.vue'
import Home from '~/views/home/home.vue'
import Statistics from '~/views/statistics/statistics.vue'
import userList from '~/views/users/userList.vue'
import userForm from '~/views/users/userForm.vue'

// API相关导入
import ApiProjectList from '~/views/apitest/project/ApiProjectList.vue'
import ApiProjectForm from '~/views/apitest/project/ApiProjectForm.vue'

import ApiKeyWordForm from '~/views/apitest/keyword/ApiKeyWordForm.vue'
import ApiKeyWordList from '~/views/apitest/keyword/ApiKeyWordList.vue'


import ApiMateManageForm from '~/views/apitest/apiMate/ApiMateManageForm.vue'
import ApiMateManageList from '~/views/apitest/apiMate/ApiMateManageList.vue'

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
        },{
            path: "/ApiKeyWordForm",
            component: ApiKeyWordForm,
            meta: {
                title: "关键字编辑页面"
            }
        },{
            path: "/ApiKeyWordList",
            component: ApiKeyWordList,
            meta: {
                title: "关键字列表页面"
            }
        },{
            path: "/ApiMateManageForm",
            component: ApiMateManageForm,
            meta: {
                title: "素材维护管理编辑页面"
            }
        },{
            path: "/ApiMateManageList",
            component: ApiMateManageList,
            meta: {
                title: "素材维护管列表页面"
            }
        }
        ]
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
router.beforeEach((to,from,next)=>{
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