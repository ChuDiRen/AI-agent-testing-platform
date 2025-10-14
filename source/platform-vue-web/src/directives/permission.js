import store from '../store'

// 权限指令 - v-permission="'system:user:add'"
export const permission = {
    mounted(el, binding) {
        const { value } = binding
        const permissions = store.state.permissions || []

        if (value && value instanceof Array && value.length > 0) {
            const hasPermission = permissions.some(perm => value.includes(perm))
            if (!hasPermission) {
                el.parentNode && el.parentNode.removeChild(el)
            }
        } else if (value && typeof value === 'string') {
            const hasPermission = permissions.includes(value)
            if (!hasPermission) {
                el.parentNode && el.parentNode.removeChild(el)
            }
        }
    }
}

// 角色指令 - v-role="'admin'"
export const role = {
    mounted(el, binding) {
        const { value } = binding
        const roles = store.state.roles || []

        if (value && value instanceof Array && value.length > 0) {
            const hasRole = roles.some(role => value.includes(role.role_name))
            if (!hasRole) {
                el.parentNode && el.parentNode.removeChild(el)
            }
        } else if (value && typeof value === 'string') {
            const hasRole = roles.some(role => role.role_name === value)
            if (!hasRole) {
                el.parentNode && el.parentNode.removeChild(el)
            }
        }
    }
}

export default {
    permission,
    role
}

