/**
 * 前端权限验证工具
 */

import { useUserStore } from '@/store'

// 权限常量
export const PERMISSIONS = {
  // 用户管理
  USER_VIEW: 'user:view',
  USER_CREATE: 'user:create',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
  
  // 角色管理
  ROLE_VIEW: 'role:view',
  ROLE_CREATE: 'role:create',
  ROLE_UPDATE: 'role:update',
  ROLE_DELETE: 'role:delete',
  
  // AI代理管理
  AGENT_VIEW: 'agent:view',
  AGENT_CREATE: 'agent:create',
  AGENT_UPDATE: 'agent:update',
  AGENT_DELETE: 'agent:delete',
  
  // 测试用例管理
  TEST_CASE_VIEW: 'test_case:view',
  TEST_CASE_CREATE: 'test_case:create',
  TEST_CASE_UPDATE: 'test_case:update',
  TEST_CASE_DELETE: 'test_case:delete',
  TEST_CASE_RUN: 'test_case:run',
  
  // 系统管理
  SYSTEM_VIEW: 'system:view',
  SYSTEM_MANAGE: 'system:manage',
  
  // 日志管理
  LOG_VIEW: 'log:view',
  LOG_DELETE: 'log:delete'
} as const

// 角色常量
export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  USER: 'user',
  GUEST: 'guest'
} as const

// 权限验证类
export class PermissionValidator {
  private getUserStore() {
    return useUserStore() // 延迟获取store，确保Pinia已初始化
  }

  /**
   * 检查是否有指定权限
   */
  hasPermission(permission: string): boolean {
    const userStore = this.getUserStore()
    if (!userStore.isLoggedIn) {
      return false
    }

    // 超级管理员拥有所有权限
    if (userStore.hasRole(ROLES.SUPER_ADMIN)) {
      return true
    }

    return userStore.hasPermission(permission)
  }

  /**
   * 检查是否有任意一个权限
   */
  hasAnyPermission(permissions: string[]): boolean {
    return permissions.some(permission => this.hasPermission(permission))
  }

  /**
   * 检查是否有所有权限
   */
  hasAllPermissions(permissions: string[]): boolean {
    return permissions.every(permission => this.hasPermission(permission))
  }

  /**
   * 检查是否有指定角色
   */
  hasRole(role: string): boolean {
    const userStore = this.getUserStore()
    if (!userStore.isLoggedIn) {
      return false
    }

    return userStore.hasRole(role)
  }

  /**
   * 检查是否有任意一个角色
   */
  hasAnyRole(roles: string[]): boolean {
    return roles.some(role => this.hasRole(role))
  }

  /**
   * 检查是否为管理员
   */
  isAdmin(): boolean {
    return this.hasAnyRole([ROLES.ADMIN, ROLES.SUPER_ADMIN])
  }

  /**
   * 检查是否为超级管理员
   */
  isSuperAdmin(): boolean {
    return this.hasRole(ROLES.SUPER_ADMIN)
  }

  /**
   * 检查是否可以访问指定路由
   */
  canAccessRoute(routePath: string): boolean {
    // 这里可以实现基于路由的权限控制
    // 例如：某些路由需要特定权限
    
    const routePermissions: Record<string, string[]> = {
      '/system/user': [PERMISSIONS.USER_VIEW],
      '/system/role': [PERMISSIONS.ROLE_VIEW],
      '/agent': [PERMISSIONS.AGENT_VIEW],
      '/test/cases': [PERMISSIONS.TEST_CASE_VIEW],
      '/system/logs': [PERMISSIONS.LOG_VIEW]
    }

    const requiredPermissions = routePermissions[routePath]
    if (!requiredPermissions) {
      return true // 没有特殊权限要求的路由，默认允许访问
    }

    return this.hasAnyPermission(requiredPermissions)
  }

  /**
   * 检查是否可以执行指定操作
   */
  canPerformAction(action: string, resource?: any): boolean {
    switch (action) {
      case 'create':
        return this.hasAnyPermission([
          PERMISSIONS.USER_CREATE,
          PERMISSIONS.ROLE_CREATE,
          PERMISSIONS.AGENT_CREATE,
          PERMISSIONS.TEST_CASE_CREATE
        ])
      
      case 'update':
        // 如果是更新自己的资源，允许
        const userStore = this.getUserStore()
        if (resource && resource.userId === userStore.userInfo?.id) {
          return true
        }
        return this.hasAnyPermission([
          PERMISSIONS.USER_UPDATE,
          PERMISSIONS.ROLE_UPDATE,
          PERMISSIONS.AGENT_UPDATE,
          PERMISSIONS.TEST_CASE_UPDATE
        ])
      
      case 'delete':
        return this.hasAnyPermission([
          PERMISSIONS.USER_DELETE,
          PERMISSIONS.ROLE_DELETE,
          PERMISSIONS.AGENT_DELETE,
          PERMISSIONS.TEST_CASE_DELETE
        ])
      
      case 'view_system':
        return this.hasPermission(PERMISSIONS.SYSTEM_VIEW)
      
      default:
        return true
    }
  }
}

// 延迟创建权限验证实例的函数
let _permissionValidator: PermissionValidator | null = null

function getPermissionValidator(): PermissionValidator {
  if (!_permissionValidator) {
    _permissionValidator = new PermissionValidator()
  }
  return _permissionValidator
}

// 便捷函数
export const hasPermission = (permission: string): boolean => {
  return getPermissionValidator().hasPermission(permission)
}

export const hasAnyPermission = (permissions: string[]): boolean => {
  return getPermissionValidator().hasAnyPermission(permissions)
}

export const hasAllPermissions = (permissions: string[]): boolean => {
  return getPermissionValidator().hasAllPermissions(permissions)
}

export const hasRole = (role: string): boolean => {
  return getPermissionValidator().hasRole(role)
}

export const hasAnyRole = (roles: string[]): boolean => {
  return getPermissionValidator().hasAnyRole(roles)
}

export const isAdmin = (): boolean => {
  return getPermissionValidator().isAdmin()
}

export const isSuperAdmin = (): boolean => {
  return getPermissionValidator().isSuperAdmin()
}

export const canAccessRoute = (routePath: string): boolean => {
  return getPermissionValidator().canAccessRoute(routePath)
}

export const canPerformAction = (action: string, resource?: any): boolean => {
  return getPermissionValidator().canPerformAction(action, resource)
}

// 导出权限验证器实例（用于组件内使用）
export const permissionValidator = {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  hasRole,
  hasAnyRole,
  isAdmin,
  isSuperAdmin,
  canAccessRoute,
  canPerformAction
}

// 权限检查混入
export const permissionMixin = {
  methods: {
    $hasPermission: hasPermission,
    $hasAnyPermission: hasAnyPermission,
    $hasAllPermissions: hasAllPermissions,
    $hasRole: hasRole,
    $hasAnyRole: hasAnyRole,
    $isAdmin: isAdmin,
    $isSuperAdmin: isSuperAdmin,
    $canAccessRoute: canAccessRoute,
    $canPerformAction: canPerformAction
  }
}

// Vue 组合式API
export const usePermission = () => {
  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    isAdmin,
    isSuperAdmin,
    canAccessRoute,
    canPerformAction,
    PERMISSIONS,
    ROLES
  }
}

// 路由守卫权限检查
export const checkRoutePermission = (to: any): boolean => {
  const meta = to.meta || {}

  // 检查是否需要登录
  if (meta.requiresAuth !== false) {
    try {
      const userStore = useUserStore()
      if (!userStore.isLoggedIn) {
        return false
      }
    } catch (error) {
      // 如果Pinia还没初始化，返回false
      console.warn('Pinia not initialized in route guard, denying access')
      return false
    }
  }

  // 检查权限
  if (meta.permission) {
    if (typeof meta.permission === 'string') {
      return hasPermission(meta.permission)
    }
    if (Array.isArray(meta.permission)) {
      return hasAnyPermission(meta.permission)
    }
  }

  // 检查角色
  if (meta.roles) {
    if (typeof meta.roles === 'string') {
      return hasRole(meta.roles)
    }
    if (Array.isArray(meta.roles)) {
      return hasAnyRole(meta.roles)
    }
  }

  return true
}

export default {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  hasRole,
  hasAnyRole,
  isAdmin,
  isSuperAdmin,
  canAccessRoute,
  canPerformAction,
  PERMISSIONS,
  ROLES,
  usePermission,
  checkRoutePermission
}