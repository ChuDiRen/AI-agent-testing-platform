/**
 * 动态路由生成工具
 * 将后端菜单数据转换为 Vue Router 路由配置
 */

import { staticRoutes } from '~/config/staticMenus'

/**
 * 将后端菜单转换为前端菜单格式
 */
export function transformMenuData(menuList) {
  if (!menuList || !Array.isArray(menuList)) return []

  return menuList.map(menu => {
    const transformed = {
      name: menu.menu_name,
      icon: menu.icon || 'Document',
      frontpath: menu.path || '',
      menu_type: menu.menu_type,
      perms: menu.perms,
      child: []
    }

    // 如果有子菜单，递归转换
    if (menu.children && menu.children.length > 0) {
      transformed.child = transformMenuData(menu.children)
    }

    return transformed
  })
}

/**
 * 从后端菜单生成前端路由
 * 将菜单树转换为路由数组
 */
export function generateRoutesFromMenus(menuTree) {
  const routes = []

  // 递归遍历菜单树
  function traverse(menus) {
    menus.forEach(menu => {
      // 只处理类型为 C（菜单）的项，跳过目录（M）和按钮（F）
      if (menu.menu_type === 'C' && menu.path) {
        // 查找静态路由配置中的组件
        const staticRoute = staticRoutes.find(route => route.path === menu.path)

        if (staticRoute) {
          // 使用静态路由配置
          routes.push({
            ...staticRoute,
            meta: {
              ...staticRoute.meta,
              title: menu.menu_name,
              permission: menu.perms || null
            }
          })
        }
      }

      // 递归处理子菜单
      if (menu.children && menu.children.length > 0) {
        traverse(menu.children)
      }
    })
  }

  traverse(menuTree)
  return routes
}

/**
 * 过滤用户有权限的路由
 * 根据用户权限过滤路由
 */
export function filterRoutesByPermission(routes, permissions) {
  if (!permissions || !Array.isArray(permissions)) return []

  return routes.filter(route => {
    // 如果路由没有配置权限要求，则通过
    if (!route.meta || !route.meta.permission) return true

    // 检查用户是否有该权限
    return permissions.includes(route.meta.permission)
  })
}

/**
 * 从菜单树中提取所有权限标识
 */
export function extractPermissionsFromMenus(menuTree, permissions = []) {
  if (!menuTree || !Array.isArray(menuTree)) return permissions

  menuTree.forEach(menu => {
    // 提取当前菜单的权限
    if (menu.perms) {
      // 如果 perms 是逗号分隔的字符串，拆分处理
      const permsList = menu.perms.split(',').filter(p => p.trim())
      permissions.push(...permsList)
    }

    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      extractPermissionsFromMenus(menu.children, permissions)
    }
  })

  // 去重
  return [...new Set(permissions)]
}

/**
 * 扁平化菜单树（用于生成标签页）
 */
export function flattenMenus(menuTree, flatList = []) {
  if (!menuTree || !Array.isArray(menuTree)) return flatList

  menuTree.forEach(menu => {
    // 如果是菜单类型且有路径，添加到扁平列表
    if (menu.menu_type === 'C' && menu.frontpath) {
      flatList.push({
        title: menu.name,
        path: menu.frontpath,
        icon: menu.icon
      })
    }

    // 递归处理子菜单
    if (menu.child && menu.child.length > 0) {
      flattenMenus(menu.child, flatList)
    }
  })

  return flatList
}
