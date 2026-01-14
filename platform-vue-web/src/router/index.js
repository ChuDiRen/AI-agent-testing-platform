import {
    createRouter,
    createWebHistory
} from 'vue-router'

import NotFound from '~/views/404.vue'
import Forbidden from '~/views/403.vue'
import ServerError from '~/views/500.vue'
import Login from '~/views/login/login.vue'
import Home from '~/views/home/home.vue'
import { staticRoutes } from '~/config/staticMenus'
import { useUserStore, useMenuStore, usePermissionStore } from '~/stores/index.js'

// 获取 token
function getToken() {
    return localStorage.getItem('token')
}

// 基础路由配置（使用静态路由）
const routes = [
    {
        path: '/',
        redirect: '/home'
    },
    {
        path: "/login",
        component: Login
    },
    {
        path: "/home",
        name: 'home',
        component: Home,
        redirect: '/Statistics',
        children: staticRoutes  // 初始使用静态路由配置
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

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 导航守卫
router.beforeEach(async (to, from, next) => {
    const token = getToken()

    // 如果是登录页，直接放行
    if (to.path === '/login') {
        next()
        return
    }

    // 如果没有 token，重定向到登录页
    if (!token) {
        next('/login')
        return
    }

    // 有 token，检查是否需要重新生成动态路由
    const menuStore = useMenuStore()
    const permissionStore = usePermissionStore()

    // 如果菜单已加载但动态路由未生成，则生成动态路由
    if (menuStore.menus.length > 0 && !permissionStore.isRoutesGenerated) {
        permissionStore.generateRoutes(menuStore.menus)
        console.log('刷新页面：重新生成动态路由')
    }

    // 设置页面标题
    if (to.meta.title) {
        document.title = `${to.meta.title} - 大熊AI代码生成器`
    }

    // 权限检查：如果有定义 requiredPermission，检查用户是否有权限
    const requiredPermission = to.meta.permission
    if (requiredPermission) {
        // 从 Pinia store 获取权限检查函数
        const userStore = useUserStore()
        const hasPermission = userStore.hasPermission(requiredPermission)
        if (!hasPermission) {
            // 没有权限，重定向到 403 页面
            next('/403')
            return
        }
    }

    next()
})

// 全局后置守卫
router.afterEach(() => {
    window.scrollTo(0, 0)
})

export default router
