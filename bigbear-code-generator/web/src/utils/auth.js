/**
 * 认证工具模块
 * 提供统一的认证、Token 管理和权限检查功能
 */

import { getToken, setToken as saveToken } from '~/axios'

/**
 * 从 localStorage 清除 Token
 */
export function clearToken() {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  localStorage.removeItem('permissions')
}

/**
 * 设置 Token
 */
export function setToken(token) {
  saveToken(token)
}

/**
 * 获取 Token
 */
export { getToken }

/**
 * 检查用户是否有指定权限
 * @param {string|Array} permission - 权限标识或权限数组
 * @param {Array} permissions - 用户权限列表
 * @returns {boolean}
 */
export function hasPermission(permission, permissions = []) {
  if (!permission) return true

  // 如果是数组，检查是否包含任一权限
  if (Array.isArray(permission)) {
    return permission.some(perm => permissions.includes(perm))
  }

  // 单个权限，检查是否包含
  return permissions.includes(permission)
}

/**
 * 检查用户是否有指定角色
 * @param {string|Array} role - 角色名称或角色数组
 * @param {Array} roles - 用户角色列表
 * @returns {boolean}
 */
export function hasRole(role, roles = []) {
  if (!role) return true

  // 如果是数组，检查是否包含任一角色
  if (Array.isArray(role)) {
    return role.some(roleName => roles.some(r => r.role_name === roleName))
  }

  // 单个角色，检查是否包含
  return roles.some(r => r.role_name === role)
}

/**
 * 检查是否是管理员
 * @param {Array} roles - 用户角色列表
 * @returns {boolean}
 */
export function isAdmin(roles = []) {
  const adminRoles = ['admin', '超级管理员', 'Administrator']
  return roles.some(r => adminRoles.includes(r.role_name))
}

/**
 * 从菜单树中提取所有权限标识
 * @param {Array} menuTree - 菜单树
 * @returns {Array}
 */
export function extractPermissionsFromMenus(menuTree) {
  if (!menuTree || !Array.isArray(menuTree)) return []

  const permissions = []

  function extract(menus) {
    menus.forEach(menu => {
      // 提取当前菜单的权限
      if (menu.perms) {
        // 如果 perms 是逗号分隔的字符串，拆分处理
        const permsList = menu.perms.split(',').filter(p => p.trim())
        permissions.push(...permsList)
      }

      // 递归处理子菜单
      if (menu.children && menu.children.length > 0) {
        extract(menu.children)
      }
    })
  }

  extract(menuTree)

  // 去重
  return [...new Set(permissions)]
}

/**
 * 验证用户登录状态
 * @returns {boolean}
 */
export function isAuthenticated() {
  const token = getToken()
  return !!token
}

/**
 * 用户登出
 * 清除所有认证信息
 */
export function logout() {
  clearToken()
  // 可以在这里清除其他用户相关数据
  sessionStorage.clear()
}
