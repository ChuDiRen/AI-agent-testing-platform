import {
    createRouter,
    createWebHistory
} from 'vue-router'
import axios from '~/axios'

import NotFound from '~/views/404.vue'
import Forbidden from '~/views/403.vue'
import ServerError from '~/views/500.vue'
import Login from '~/views/login/login.vue'
import Home from '~/views/home/home.vue'
import Statistics from '~/views/statistics/statistics.vue'

// 动态导入所有 views 目录下的 .vue 文件
const modules = import.meta.glob('../views/**/*.vue')

// 获取 token
function getToken() {
    return localStorage.getItem('token')
}

// 基础路由（不需要动态加载的）
const routes = [
    {
        path: '/',
        redirect: '/home'
    }, {
        path: "/login",
        component: Login
    }, {
        path: "/home",
        name: 'home',
        component: Home,
        redirect: '/Statistics',
        children: [{
            path: "/Statistics",
            component: Statistics,
            meta: {
                title: "主页信息"
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

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 已添加的动态路由路径集合（防止重复添加）
const addedRoutes = new Set(['/Statistics'])

// 标记动态路由是否已加载
let dynamicRoutesLoaded = false

// 标记是否正在加载动态路由（防止重复请求）
let isLoadingRoutes = false

/**
 * 根据后端菜单数据动态添加路由
 * @param {Array} menus - 后端返回的菜单树
 */
export function addDynamicRoutes(menus) {
    if (!menus || !Array.isArray(menus)) return
    
    const flatMenus = flattenMenuTree(menus)
    
    flatMenus.forEach(menu => {
        // 只处理菜单类型(C)，跳过目录(M)和按钮(F)
        if (menu.menu_type !== 'C') return

        // 获取路由路径
        const routePath = getRoutePath(menu)
        if (!routePath) return
        
        // 防止重复添加
        if (addedRoutes.has(routePath)) return
        
        // 获取组件
        const component = getComponent(menu.component)
        if (!component) {
            return
        }

        // 添加路由
        router.addRoute('home', {
            path: routePath,
            component: component,
            meta: {
                title: menu.menu_name,
                permission: menu.perms
            }
        })

        addedRoutes.add(routePath)
    })
    
    // 标记动态路由已加载
    dynamicRoutesLoaded = true
}

/**
 * 检查动态路由是否已加载
 */
export function isDynamicRoutesLoaded() {
    return dynamicRoutesLoaded
}

/**
 * 将菜单树扁平化
 */
function flattenMenuTree(tree, result = []) {
    tree.forEach(node => {
        result.push(node)
        if (node.children && node.children.length > 0) {
            flattenMenuTree(node.children, result)
        }
    })
    return result
}

/**
 * 获取路由路径
 * 优先使用 path 字段（如果是 /XxxYyy 格式），否则使用 component
 */
function getRoutePath(menu) {
    // 如果 path 以 / + 大写字母开头，直接使用
    if (menu.path && /^\/[A-Z]/.test(menu.path)) {
        return menu.path
    }
    
    // 否则根据 component 生成路径
    if (menu.component) {
        // component 格式可能是 "userList" 或 "system/users/userList"
        // 提取最后的组件名作为路径
        const parts = menu.component.split('/')
        const componentName = parts[parts.length - 1]
        return `/${componentName}`
    }
    
    return null
}

/**
 * 根据 component 字符串获取组件
 * 支持多种格式：
 * - "userList" -> views/system/users/userList.vue 或其他匹配
 * - "system/users/userList" -> views/system/users/userList.vue
 */
function getComponent(componentStr) {
    if (!componentStr) return null
    
    // 尝试多种路径格式
    const possiblePaths = []
    
    // 如果包含 /，说明是完整路径
    if (componentStr.includes('/')) {
        possiblePaths.push(`../views/${componentStr}.vue`)
    } else {
        // 只有组件名，需要搜索匹配
        // 遍历所有模块找到匹配的
        for (const path in modules) {
            if (path.endsWith(`/${componentStr}.vue`)) {
                return modules[path]
            }
        }
        
        // 如果没找到，尝试常见的系统管理路径
        const systemPaths = [
            `../views/system/users/${componentStr}.vue`,
            `../views/system/role/${componentStr}.vue`, 
            `../views/system/menu/${componentStr}.vue`,
            `../views/system/dept/${componentStr}.vue`
        ]
        
        for (const tryPath of systemPaths) {
            if (modules[tryPath]) {
                return modules[tryPath]
            }
        }
    }
    
    // 尝试直接匹配
    for (const tryPath of possiblePaths) {
        if (modules[tryPath]) {
            return modules[tryPath]
        }
    }
    
    return null
}

// 权限检查函数
function checkPermission(permission) {
    try {
        const username = localStorage.getItem('username')
        
        // 超级管理员直接放行
        if (username === 'admin') {
            return true
        }
        
        const userPermissions = JSON.parse(localStorage.getItem('permissions') || '[]')
        return userPermissions.includes(permission)
    } catch (e) {
        console.error('权限检查失败:', e)
        return false
    }
}

/**
 * 从后端加载菜单并注册动态路由
 */
async function loadAndRegisterRoutes() {
    if (dynamicRoutesLoaded || isLoadingRoutes) return
    
    isLoadingRoutes = true
    try {
        const res = await axios.get('/menus/tree?_alias=menu-tree')
        if (res?.data?.code === 200) {
            const menuData = res.data.data || []
            addDynamicRoutes(menuData)
        }
    } catch (e) {
        console.error('加载动态路由失败:', e)
    } finally {
        isLoadingRoutes = false
    }
}

// 导航守卫
router.beforeEach(async (to, from, next) => {
    const token = getToken()

    if (to.path === '/login') {
        next()
    } else {
        if (token) {
            // 如果动态路由未加载，先加载
            if (!dynamicRoutesLoaded) {
                await loadAndRegisterRoutes()
                
                // 重新尝试匹配路由
                const matched = router.resolve(to.path)
                if (matched.name !== 'NotFound') {
                    next(to.path)
                    return
                }
            }
            
            // 检查权限
            if (to.meta.permission) {
                if (!checkPermission(to.meta.permission)) {
                    next('/403')
                    return
                }
            }
            
            // 设置页面标题
            if (to.meta.title) {
                document.title = `${to.meta.title} - 大熊AI代码生成器`
            }
            
            next()
        } else {
            next('/login')
        }
    }
})

// 全局后置守卫
router.afterEach(() => {
    window.scrollTo(0, 0)
})

export default router
