import { createStore } from 'vuex'
import { useCookies } from '@vueuse/integrations/useCookies'

const cookies = useCookies()

const store = createStore({
    state() {
        // 根据屏幕宽度设置初始侧边栏宽度，优先从 localStorage 恢复
        const getInitialAsideWidth = () => {
            const width = window.innerWidth
            const savedWidth = localStorage.getItem('asideWidth')
            
            console.log('🔧 初始化侧边栏宽度:', { width, savedWidth })
            
            // 移动端始终返回 0px
            if (width <= 768) {
                console.log('📱 移动端模式: 0px')
                return "0px"
            }
            
            // 清理无效的 0px 状态（非移动端不应该是 0px）
            if (savedWidth === "0px") {
                console.log('🧹 清理无效的 0px 状态')
                localStorage.removeItem('asideWidth')
            }
            
            // 非移动端：验证保存的宽度是否合理
            if (savedWidth === "64px") {
                console.log('📐 恢复折叠状态: 64px')
                return "64px"
            }
            
            if (savedWidth === "200px" || savedWidth === "250px") {
                // 根据屏幕尺寸调整展开宽度
                const expandedWidth = width <= 1366 ? "200px" : "250px"
                console.log('📐 恢复展开状态:', expandedWidth)
                return expandedWidth
            }
            
            // 没有有效的保存宽度，使用默认展开状态
            const defaultWidth = width <= 1366 ? "200px" : "250px"
            console.log('📐 使用默认展开状态:', defaultWidth)
            return defaultWidth
        }
        
        return {
            asideWidth: getInitialAsideWidth(),
            theme: localStorage.getItem('theme') || 'light', // 主题模式
            userInfo: null, // 用户信息
            roles: [], // 用户角色
            permissions: [], // 用户权限
            menuTree: [] // 用户菜单树
        }
    },
    mutations: {
        // 侧边栏宽度切换
        handleAsideWidth(state) {
            const width = window.innerWidth
            if (width <= 768) {
                // 移动端：显示/隐藏
                state.asideWidth = state.asideWidth === "0px" ? "250px" : "0px"
            } else if (width <= 1366) {
                // 笔记本：200px <-> 64px
                state.asideWidth = state.asideWidth === "200px" ? "64px" : "200px"
            } else {
                // 大屏：250px <-> 64px
                state.asideWidth = state.asideWidth === "250px" ? "64px" : "250px"
            }
            // 保存到 localStorage
            localStorage.setItem('asideWidth', state.asideWidth)
        },
        
        // 响应式调整侧边栏宽度（窗口大小变化时）
        adjustAsideWidth(state) {
            const width = window.innerWidth
            const isCollapsed = state.asideWidth === "64px" || state.asideWidth === "0px"
            
            // 移动端特殊处理
            if (width <= 768) {
                if (!isCollapsed) {
                    state.asideWidth = "0px"
                }
                return
            }
            
            // 非移动端：保持折叠状态，只调整展开时的宽度
            if (isCollapsed) {
                state.asideWidth = "64px"
            } else {
                // 根据屏幕尺寸调整展开宽度
                if (width <= 1366) {
                    state.asideWidth = "200px"
                } else {
                    state.asideWidth = "250px"
                }
            }
            // 保存到 localStorage
            localStorage.setItem('asideWidth', state.asideWidth)
        },

        // 设置主题
        setTheme(state, theme) {
            state.theme = theme
            document.documentElement.setAttribute('data-theme', theme)
            localStorage.setItem('theme', theme)
        },

        // 切换主题
        toggleTheme(state) {
            const newTheme = state.theme === 'light' ? 'dark' : 'light'
            this.commit('setTheme', newTheme)
        },

        // 设置用户信息
        setUserInfo(state, userInfo) {
            state.userInfo = userInfo
        },

        // 设置用户角色
        setRoles(state, roles) {
            state.roles = roles
        },

        // 设置用户权限
        setPermissions(state, permissions) {
            state.permissions = permissions
        },

        // 设置菜单树
        setMenuTree(state, menuTree) {
            state.menuTree = menuTree
        },

        // 清除用户信息
        clearUserInfo(state) {
            state.userInfo = null
            state.roles = []
            state.permissions = []
            state.menuTree = []
            cookies.remove('l-token')
        }
    },
    actions: {
        // 登出
        logout({ commit }) {
            commit('clearUserInfo')
        }
    },
    getters: {
        // 判断是否有某个权限
        hasPermission: (state) => (perm) => {
            if (!perm) return true
            return state.permissions.includes(perm)
        },

        // 判断是否有某个角色
        hasRole: (state) => (role) => {
            if (!role) return true
            return state.roles.some(r => r.role_name === role)
        }
    }
})

export default store