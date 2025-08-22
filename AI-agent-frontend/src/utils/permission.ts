/**
 * 权限工具函数
 */
import { useUserStore } from '@/store'

/**
 * 检查是否有指定权限
 * @param permission 权限标识或权限数组
 * @param mode 检查模式：'some' 任一匹配 | 'every' 全部匹配
 * @returns 是否有权限
 */
export function hasPermission(permission: string | string[], mode: 'some' | 'every' = 'some'): boolean {
  const userStore = useUserStore()
  
  // 如果未登录，无权限
  if (!userStore.isLoggedIn) {
    return false
  }

  // 超级管理员拥有所有权限
  if (userStore.hasRole('admin') || userStore.hasRole('super_admin')) {
    return true
  }

  const permissions = Array.isArray(permission) ? permission : [permission]
  
  if (mode === 'every') {
    return permissions.every(perm => userStore.hasPermission(perm))
  } else {
    return permissions.some(perm => userStore.hasPermission(perm))
  }
}

/**
 * 检查是否有指定角色
 * @param role 角色标识或角色数组
 * @param mode 检查模式：'some' 任一匹配 | 'every' 全部匹配
 * @returns 是否有角色
 */
export function hasRole(role: string | string[], mode: 'some' | 'every' = 'some'): boolean {
  const userStore = useUserStore()
  
  // 如果未登录，无权限
  if (!userStore.isLoggedIn) {
    return false
  }

  const roles = Array.isArray(role) ? role : [role]
  
  if (mode === 'every') {
    return roles.every(r => userStore.hasRole(r))
  } else {
    return roles.some(r => userStore.hasRole(r))
  }
}

/**
 * 检查是否有任一权限
 * @param permissions 权限数组
 * @returns 是否有权限
 */
export function hasAnyPermission(permissions: string[]): boolean {
  return hasPermission(permissions, 'some')
}

/**
 * 检查是否有所有权限
 * @param permissions 权限数组
 * @returns 是否有权限
 */
export function hasAllPermissions(permissions: string[]): boolean {
  return hasPermission(permissions, 'every')
}

/**
 * 检查是否有任一角色
 * @param roles 角色数组
 * @returns 是否有角色
 */
export function hasAnyRole(roles: string[]): boolean {
  return hasRole(roles, 'some')
}

/**
 * 检查是否有所有角色
 * @param roles 角色数组
 * @returns 是否有角色
 */
export function hasAllRoles(roles: string[]): boolean {
  return hasRole(roles, 'every')
}

/**
 * 检查是否是超级管理员
 * @returns 是否是超级管理员
 */
export function isSuperAdmin(): boolean {
  const userStore = useUserStore()
  return userStore.hasRole('admin') || userStore.hasRole('super_admin')
}

/**
 * 权限过滤器 - 过滤有权限的项目
 * @param items 项目数组
 * @param getPermission 获取权限的函数
 * @returns 有权限的项目数组
 */
export function filterByPermission<T>(
  items: T[],
  getPermission: (item: T) => string | string[] | undefined
): T[] {
  return items.filter(item => {
    const permission = getPermission(item)
    if (!permission) return true // 如果没有指定权限，则显示
    return hasPermission(permission)
  })
}

/**
 * 角色过滤器 - 过滤有角色的项目
 * @param items 项目数组
 * @param getRole 获取角色的函数
 * @returns 有角色的项目数组
 */
export function filterByRole<T>(
  items: T[],
  getRole: (item: T) => string | string[] | undefined
): T[] {
  return items.filter(item => {
    const role = getRole(item)
    if (!role) return true // 如果没有指定角色，则显示
    return hasRole(role)
  })
}

/**
 * 菜单权限过滤器
 * @param menus 菜单数组
 * @returns 有权限的菜单数组
 */
export function filterMenusByPermission(menus: any[]): any[] {
  return menus.filter(menu => {
    // 检查菜单权限
    if (menu.perms && !hasPermission(menu.perms)) {
      return false
    }
    
    // 递归检查子菜单
    if (menu.children && menu.children.length > 0) {
      menu.children = filterMenusByPermission(menu.children)
      // 如果所有子菜单都没有权限，则隐藏父菜单
      return menu.children.length > 0
    }
    
    return true
  })
}

/**
 * 按钮权限过滤器
 * @param buttons 按钮配置数组
 * @returns 有权限的按钮数组
 */
export function filterButtonsByPermission(buttons: Array<{ permission?: string | string[]; [key: string]: any }>): any[] {
  return buttons.filter(button => {
    if (!button.permission) return true
    return hasPermission(button.permission)
  })
}