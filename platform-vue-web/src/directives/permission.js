import { useUserStore } from '~/stores/index.js'

/**
 * 权限指令 - v-permission="'system:user:add'"
 * 用法：
 * - 单个权限：v-permission="'system:user:add'"
 * - 多个权限（满足其一即可）：v-permission="['system:user:add', 'system:user:edit']"
 * - 多个权限（必须全部满足）：v-permission="['system:user:add', 'system:user:edit']" mode="all"
 */
export const permission = {
    mounted(el, binding) {
        const { value, modifiers } = binding
        const userStore = useUserStore()
        const permissions = userStore.permissions || []
        
        // 支持模式：all（必须全部满足）或 any（满足其一，默认）
        const mode = modifiers.all ? 'all' : 'any'

        if (!value) {
            return
        }

        let hasPermission = false

        if (value instanceof Array && value.length > 0) {
            // 数组形式
            if (mode === 'all') {
                // 必须全部满足
                hasPermission = value.every(perm => permissions.includes(perm))
            } else {
                // 满足其一即可
                hasPermission = permissions.some(perm => value.includes(perm))
            }
        } else if (typeof value === 'string') {
            // 字符串形式
            hasPermission = permissions.includes(value)
        }

        if (!hasPermission) {
            // 移除元素
            if (el.parentNode) {
                el.parentNode.removeChild(el)
            }
            // 或者添加一个占位符，保持布局（可选）
            // el.style.display = 'none'
            // el.setAttribute('data-no-permission', 'true')
        }
    },
    
    // 支持动态更新权限
    updated(el, binding) {
        const { value, modifiers } = binding
        const userStore = useUserStore()
        const permissions = userStore.permissions || []
        const mode = modifiers.all ? 'all' : 'any'
        
        if (!value) return

        let hasPermission = false

        if (value instanceof Array && value.length > 0) {
            if (mode === 'all') {
                hasPermission = value.every(perm => permissions.includes(perm))
            } else {
                hasPermission = permissions.some(perm => value.includes(perm))
            }
        } else if (typeof value === 'string') {
            hasPermission = permissions.includes(value)
        }

        if (!hasPermission) {
            if (el.parentNode && el.style.display !== 'none') {
                el.style.display = 'none'
            }
        } else {
            if (el.style.display === 'none') {
                el.style.display = ''
            }
        }
    }
}

/**
 * 角色指令 - v-role="'admin'"
 * 用法：
 * - 单个角色：v-role="'admin'"
 * - 多个角色（满足其一即可）：v-role="['admin', 'editor']"
 * - 多个角色（必须全部满足）：v-role="['admin', 'editor']" mode="all"
 */
export const role = {
    mounted(el, binding) {
        const { value, modifiers } = binding
        const userStore = useUserStore()
        const roles = userStore.roles || []
        
        // 支持模式：all（必须全部满足）或 any（满足其一，默认）
        const mode = modifiers.all ? 'all' : 'any'

        if (!value) {
            return
        }

        let hasRole = false

        if (value instanceof Array && value.length > 0) {
            // 数组形式
            if (mode === 'all') {
                // 必须全部满足
                hasRole = value.every(roleName => roles.some(role => role.role_name === roleName))
            } else {
                // 满足其一即可
                hasRole = roles.some(role => value.includes(role.role_name))
            }
        } else if (typeof value === 'string') {
            // 字符串形式
            hasRole = roles.some(role => role.role_name === value)
        }

        if (!hasRole) {
            if (el.parentNode) {
                el.parentNode.removeChild(el)
            }
        }
    },
    
    // 支持动态更新角色
    updated(el, binding) {
        const { value, modifiers } = binding
        const userStore = useUserStore()
        const roles = userStore.roles || []
        const mode = modifiers.all ? 'all' : 'any'
        
        if (!value) return

        let hasRole = false

        if (value instanceof Array && value.length > 0) {
            if (mode === 'all') {
                hasRole = value.every(roleName => roles.some(role => role.role_name === roleName))
            } else {
                hasRole = roles.some(role => value.includes(role.role_name))
            }
        } else if (typeof value === 'string') {
            hasRole = roles.some(role => role.role_name === value)
        }

        if (!hasRole) {
            if (el.parentNode && el.style.display !== 'none') {
                el.style.display = 'none'
            }
        } else {
            if (el.style.display === 'none') {
                el.style.display = ''
            }
        }
    }
}

export default {
    permission,
    role
}


