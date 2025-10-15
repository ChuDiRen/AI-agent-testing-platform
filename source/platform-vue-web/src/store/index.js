import { createStore } from 'vuex'
import { useCookies } from '@vueuse/integrations/useCookies'

const cookies = useCookies()

const store = createStore({
    state() {
        return {
            asideWidth: "250px",
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
            state.asideWidth = state.asideWidth == "250px" ? "64px" : "250px"
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