// 导入路由创建函数
import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Login from '~/views/login/login.vue'
import NotFound from '../views/NotFound.vue'  // 导入404组件
import About from '../views/pages/about.vue'  // 导入关于页面
import Home from '../views/home/home.vue' // 导入首页



// 导入统计页面
import Statistics from '../views/statistics/statistics.vue'

// 导入对应的路由
import userList from '~/views/users/userList.vue'
import userForm from '~/views/users/userForm.vue'

// RBAC 权限管理导入
import roleList from '~/views/roles/roleList.vue'
import roleForm from '~/views/roles/roleForm.vue'
import roleMenu from '~/views/roles/roleMenu.vue'
import roleApi from '~/views/roles/roleApi.vue'
import rolePermission from '~/views/roles/rolePermission.vue'

import menuList from '~/views/menus/menuList.vue'
import menuForm from '~/views/menus/menuForm.vue'

import deptList from '~/views/depts/deptList.vue'
import deptForm from '~/views/depts/deptForm.vue'

import apiList from '~/views/apis/apiList.vue'
import apiForm from '~/views/apis/apiForm.vue'

import auditLogList from '~/views/auditlogs/auditLogList.vue'

// API相关导入
import ApiProjectList from '~/views/apitest/project/ApiProjectList.vue'
import ApiProjectForm from '~/views/apitest/project/ApiProjectForm.vue'

import ApiKeyWordForm from '~/views/apitest/keyword/ApiKeyWordForm.vue'
import ApiKeyWordList from '~/views/apitest/keyword/ApiKeyWordList.vue'

import ApiMateManageForm from '~/views/apitest/apiMate/ApiMateManageForm.vue'
import ApiMateManageList from '~/views/apitest/apiMate/ApiMateManageList.vue'

import ApiInfoList from '~/views/apitest/apiinfo/ApiInfoList.vue'
import ApiInfoForm from '~/views/apitest/apiinfo/ApiInfoForm.vue'

import ApiInfoCaseList from '~/views/apitest/apiinfocase/ApiInfoCaseList.vue'
import ApiInfoCaseForm from '~/views/apitest/apiinfocase/ApiInfoCaseForm.vue'

import ApiCollectionInfoList from '~/views/apitest/collection/ApiCollectionInfoList.vue'
import ApiCollectionInfoForm from '~/views/apitest/collection/ApiCollectionInfoForm.vue'

import WeChartMsgManageList from '../views/msgmanage/WeChartMsgManageList.vue'
import WeChartMsgManageForm from '../views/msgmanage/WeChartMsgManageForm.vue'

import DingDingMsgManageList from '~/views/msgmanage/DingDingMsgManageList.vue';
import DingDingMsgManageForm from '~/views/msgmanage/DingDingMsgManageForm.vue';

import FeiShuMsgManageList from '~/views/msgmanage/FeiShuMsgManageList.vue';
import FeiShuMsgManageForm from '~/views/msgmanage/FeiShuMsgManageForm.vue';


// 报表页面
import ApiPlanChartForm from '../views/apitest/collection/ApiPlanChartForm.vue'

// 路由规则数组
const routes = [
  {
    path: '/',          // 访问路径
    redirect: '/login'  // 自动重定向到'/login'路径
  }, {
    path: '/login',         
    component: Login     
  }, {
    path: '/about',       
    component: About  
  }, {
    path: '/home',      
    component: Home,
    redirect: '/Statistics',  // 默认重定向到统计页面
    //子路由概念，后续所有的子页面都要放在这里
    children: [{
            path: "/Statistics",
            component: Statistics,
            meta: {
                title: "数据统计"
            }
        },{
            path: "/profile",
            component: () => import('~/views/profile/profile.vue'),
            meta: {
                title: "个人中心"
            }
        },{
            path: "/settings",
            component: () => import('~/views/settings/settings.vue'),
            meta: {
                title: "系统设置"
            }
        },{
            path: "/userList",
            component: userList,
            meta: {
                title: "用户管理"
            }
        }, {
            path: "/userForm",
            component: userForm,
            meta: {
                title: "用户编辑页"
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
                title: "项目编辑页"
            }
        },{
            path: "/ApiKeyWordForm",
            component: ApiKeyWordForm,
            meta: {
                title: "关键字编辑页"
            }
        },{
            path: "/ApiKeyWordList",
            component: ApiKeyWordList,
            meta: {
                title: "关键字列表页"
            }
        },{
            path: "/ApiMateManageForm",
            component: ApiMateManageForm,
            meta: {
                title: "素材维护管理编辑页"
            }
        },{
            path: "/ApiMateManageList",
            component: ApiMateManageList,
            meta: {
                title: "素材维护管列表页"
            }
        },{
            path: "/ApiInfoList",
            component: ApiInfoList,
            meta: {
                title: "接口信息列表页"
          }
        }, {
            path: "/ApiInfoForm",
            component: ApiInfoForm,
            meta: {
                title: "接口信息编辑页"
            }
        },{
            path: "/ApiInfoCaseList",
            component: ApiInfoCaseList,
            meta: {
                title: "用例信息列表页"
            }
        },{
            path: "/ApiInfoCaseForm",
            component: ApiInfoCaseForm,
            meta: {
                title: "用例信息编辑页"
            }
        },{
            path: "/ApiCollectionInfoList",
            component: ApiCollectionInfoList,
            meta: {
                title: "测试计划列表页"
            }
        },{
            path: "/ApiCollectionInfoForm",
            component: ApiCollectionInfoForm,
            meta: {
                title: "测试计划编辑页"
            }
        },{
            "path":"/WeChartMsgManageList",
            component: WeChartMsgManageList,
            meta: {
                title: "微信消息管理"
            }
        },{
            "path":"/WeChartMsgManageForm",
            component: WeChartMsgManageForm,
            meta: {
                title: "微信消息管理编辑"
            }
        },{
            "path":"/DingDingMsgManageList",
            component: DingDingMsgManageList,
            meta: {
                title: "钉钉消息管理"
            }
        },{
            "path":"/DingDingMsgManageForm",
            component: DingDingMsgManageForm,
            meta: {
                title: "钉钉消息管理编辑"
            }
        },{
            "path":"/FeiShuMsgManageList",
            component: FeiShuMsgManageList,
            meta: {
                title: "飞书消息管理"
            }
        },{
            "path":"/FeiShuMsgManageForm",
            component: FeiShuMsgManageForm,
            meta: {
                title: "飞书消息管理编辑"
            }
        },{
            "path":"/ApiPlanChartForm",
            component: ApiPlanChartForm,
            meta: {
                title: "测试计划报表页面"
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
                title: "角色编辑页"
            }
        }, {
            path: "/roleMenu",
            component: roleMenu,
            meta: {
                title: "角色菜单配置"
            }
        }, {
            path: "/roleApi",
            component: roleApi,
            meta: {
                title: "角色API配置"
            }
        }, {
            path: "/rolePermission",
            component: rolePermission,
            meta: {
                title: "角色权限配置"
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
                title: "菜单编辑页"
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
                title: "部门编辑页"
            }
        }, {
            path: "/apiList",
            component: apiList,
            meta: {
                title: "API管理"
            }
        }, {
            path: "/apiForm",
            component: apiForm,
            meta: {
                title: "API编辑页"
            }
        }, {
            path: "/auditLogList",
            component: auditLogList,
            meta: {
                title: "审计日志"
            }
        }]
  }, {
    // 通配符路由，匹配所有未定义的路径
    // 404页面必须放在最后
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),  // 使用HTML5 history模式（无#号URL）
  routes                        // 路由规则
})

// 导出路由实例
export default router