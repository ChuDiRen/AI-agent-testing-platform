/**
 * 权限管理工具
 * 实现前端权限控制
 */

// 权限缓存
let userPermissions = null
let permissionsCache = new Map()

/**
 * 获取用户权限
 */
export async function getUserPermissions() {
  if (userPermissions) {
    return userPermissions
  }
  
  try {
    // 从localStorage获取用户信息
    const username = localStorage.getItem('username')
    if (!username) {
      return { menus: new Set(), apis: new Set(), roles: [] }
    }
    
    // 调用API获取权限
    const response = await fetch('/permission/user', {
      method: 'GET',
      headers: {
        'token': localStorage.getItem('token') || '',
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.code === 200) {
        userPermissions = {
          menus: new Set(data.data.menus || []),
          apis: new Set(data.data.apis || []),
          roles: data.data.roles || []
        }
        return userPermissions
      }
    }
  } catch (error) {
    // 获取用户权限失败处理
  }
  
  return { menus: new Set(), apis: new Set(), roles: [] }
}

/**
 * 检查菜单权限
 */
export async function hasMenuPermission(menuPath) {
  const permissions = await getUserPermissions()
  return permissions.menus.has(menuPath)
}

/**
 * 检查API权限
 */
export async function hasApiPermission(apiPath, method = 'GET') {
  const permissions = await getUserPermissions()
  const permissionKey = `${apiPath}:${method}`
  return permissions.apis.has(permissionKey) || permissions.apis.has(apiPath)
}

/**
 * 检查是否为超级管理员
 */
export async function isSuperAdmin() {
  const permissions = await getUserPermissions()
  return permissions.roles.includes('超级管理员')
}

/**
 * 清除权限缓存
 */
export function clearPermissionCache() {
  userPermissions = null
  permissionsCache.clear()
}

/**
 * 权限指令 - Vue自定义指令
 */
export const permissionDirective = {
  async mounted(el, binding) {
    const { value } = binding
    
    if (!value) {
      return
    }
    
    let hasPermission = false
    
    if (typeof value === 'string') {
      // 检查菜单权限
      hasPermission = await hasMenuPermission(value)
    } else if (typeof value === 'object') {
      const { path, method } = value
      // 检查API权限
      hasPermission = await hasApiPermission(path, method)
    }
    
    if (!hasPermission) {
      // 隐藏元素
      el.style.display = 'none'
      // 或者移除元素
      // el.parentNode && el.parentNode.removeChild(el)
    }
  }
}

/**
 * 路由权限守卫
 */
export async function checkRoutePermission(to) {
  const path = to.path
  const permissions = await getUserPermissions()
  
  // 超级管理员可以访问所有页面
  if (permissions.roles.includes('超级管理员')) {
    return true
  }
  
  // 检查页面权限
  if (!permissions.menus.has(path)) {
    return false
  }
  
  return true
}

/**
 * 过滤菜单项
 */
export async function filterMenuItems(menus) {
  const permissions = await getUserPermissions()
  
  if (permissions.roles.includes('超级管理员')) {
    return menus
  }
  
  return menus.filter(menu => {
    return permissions.menus.has(menu.path) || permissions.menus.has(menu.url)
  })
}

/**
 * 权限检查Mixin
 */
export const permissionMixin = {
  data() {
    return {
      userPermissions: null
    }
  },
  
  async created() {
    this.userPermissions = await getUserPermissions()
  },
  
  methods: {
    async hasPermission(path, method = 'GET') {
      if (this.userPermissions.roles.includes('超级管理员')) {
        return true
      }
      
      if (path.startsWith('/')) {
        return this.userPermissions.menus.has(path)
      } else {
        const permissionKey = `${path}:${method}`
        return this.userPermissions.apis.has(permissionKey) || this.userPermissions.apis.has(path)
      }
    },
    
    isSuperAdmin() {
      return this.userPermissions.roles.includes('超级管理员')
    }
  }
}
