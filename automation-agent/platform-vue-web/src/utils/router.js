/**
 * 动态路由构建工具
 * 将后端返回的菜单数据转换为Vue Router路由配置
 */

/**
 * 组件映射表
 * 将菜单的component字段映射到实际的组件
 */
const componentMap = {
  // 系统管理
  'userList': () => import('~/views/users/userList.vue'),
  'userForm': () => import('~/views/users/userForm.vue'),
  'roleList': () => import('~/views/roles/roleList.vue'),
  'roleForm': () => import('~/views/roles/roleForm.vue'),
  'roleMenu': () => import('~/views/roles/roleMenu.vue'),
  'roleApi': () => import('~/views/roles/roleApi.vue'),
  'rolePermission': () => import('~/views/roles/rolePermission.vue'),
  'menuList': () => import('~/views/menus/menuList.vue'),
  'menuForm': () => import('~/views/menus/menuForm.vue'),
  'deptList': () => import('~/views/depts/deptList.vue'),
  'deptForm': () => import('~/views/depts/deptForm.vue'),
  'apiList': () => import('~/views/apis/apiList.vue'),
  'apiForm': () => import('~/views/apis/apiForm.vue'),
  'auditLogList': () => import('~/views/auditlogs/auditLogList.vue'),

  // API测试
  'apiProjectList': () => import('~/views/apitest/project/ApiProjectList.vue'),
  'apiProjectForm': () => import('~/views/apitest/project/ApiProjectForm.vue'),
  'apiKeyWordList': () => import('~/views/apitest/keyword/ApiKeyWordList.vue'),
  'apiKeyWordForm': () => import('~/views/apitest/keyword/ApiKeyWordForm.vue'),
  'apiMateManageList': () => import('~/views/apitest/apiMate/ApiMateManageList.vue'),
  'apiMateManageForm': () => import('~/views/apitest/apiMate/ApiMateManageForm.vue'),
  'apiInfoList': () => import('~/views/apitest/apiinfo/ApiInfoList.vue'),
  'apiInfoForm': () => import('~/views/apitest/apiinfo/ApiInfoForm.vue'),
  'apiInfoCaseList': () => import('~/views/apitest/apiinfocase/ApiInfoCaseList.vue'),
  'apiInfoCaseForm': () => import('~/views/apitest/apiinfocase/ApiInfoCaseForm.vue'),
  'apiCollectionInfoList': () => import('~/views/apitest/collection/ApiCollectionInfoList.vue'),
  'apiCollectionInfoForm': () => import('~/views/apitest/collection/ApiCollectionInfoForm.vue'),
  'apiPlanChartForm': () => import('~/views/apitest/collection/ApiPlanChartForm.vue'),

  // 消息管理
  'weChartMsgManageList': () => import('~/views/msgmanage/WeChartMsgManageList.vue'),
  'weChartMsgManageForm': () => import('~/views/msgmanage/WeChartMsgManageForm.vue'),
  'dingDingMsgManageList': () => import('~/views/msgmanage/DingDingMsgManageList.vue'),
  'dingDingMsgManageForm': () => import('~/views/msgmanage/DingDingMsgManageForm.vue'),
  'feiShuMsgManageList': () => import('~/views/msgmanage/FeiShuMsgManageList.vue'),
  'feiShuMsgManageForm': () => import('~/views/msgmanage/FeiShuMsgManageForm.vue'),

  // 其他页面
  'statistics': () => import('~/views/statistics/statistics.vue'),
  'profile': () => import('~/views/profile/profile.vue'),
  'settings': () => import('~/views/settings/settings.vue'),
  'about': () => import('~/views/pages/about.vue'),
  'notFound': () => import('~/views/NotFound.vue'),
}

/**
 * 根据组件名称加载组件
 * @param {string} componentName - 组件名称
 * @returns {Function} 异步加载组件的函数
 */
export function loadComponent(componentName) {
  if (!componentName) {
    console.warn(`组件名称为空: ${componentName}`)
    return componentMap['notFound'] || (() => import('~/views/NotFound.vue'))
  }

  const component = componentMap[componentName]
  if (component) {
    return component
  }

  console.warn(`未找到组件: ${componentName}`)
  return componentMap['notFound'] || (() => import('~/views/NotFound.vue'))
}

/**
 * 将菜单项转换为路由配置
 * @param {Object} menu - 菜单项对象
 * @returns {Object} 路由配置对象
 */
export function menuToRoute(menu) {
  const route = {
    path: menu.path,
    name: menu.name || menu.id,
    meta: {
      title: menu.name,
      icon: menu.icon,
      isHidden: menu.is_hidden || false,
      keepalive: menu.keepalive !== false, // 默认启用缓存
      redirect: menu.redirect
    }
  }

  // 处理组件
  if (menu.component) {
    route.component = loadComponent(menu.component)
  }

  // 处理重定向
  if (menu.redirect) {
    route.redirect = menu.redirect
  }

  // 处理子路由
  if (menu.children && menu.children.length > 0) {
    route.children = menu.children
      .filter(child => child.menu_type === 'menu') // 只处理菜单类型
      .map(child => menuToRoute(child))
  }

  return route
}

/**
 * 将菜单树转换为路由树
 * @param {Array} menus - 菜单树数组
 * @returns {Array} 路由树数组
 */
export function menusToRoutes(menus) {
  if (!menus || !Array.isArray(menus)) {
    console.warn('菜单数据格式错误', menus)
    return []
  }

  // 过滤掉隐藏的菜单和目录（只保留可见的菜单）
  const visibleMenus = menus.filter(menu => !menu.is_hidden)

  return visibleMenus
    .filter(menu => menu.menu_type === 'menu') // 只处理菜单类型
    .map(menu => menuToRoute(menu))
}

/**
 * 将路由添加到Vue Router
 * @param {Object} router - Vue Router实例
 * @param {Array} routes - 路由配置数组
 */
export function addRoutes(router, routes) {
  if (!router || !routes || routes.length === 0) {
    return
  }

  // 将新路由添加到现有的home路由下
  const homeRoute = router.getRoutes().find(route => route.path === '/home')
  if (homeRoute) {
    routes.forEach(route => {
      router.addRoute('home', route)
    })
  } else {
    // 如果找不到home路由，直接添加到根路由
    routes.forEach(route => {
      router.addRoute(route)
    })
  }
}

/**
 * 递归查找菜单中的所有路径
 * @param {Array} menus - 菜单数组
 * @returns {Array} 路径数组
 */
export function getMenuPaths(menus) {
  const paths = []

  function traverse(menus) {
    menus.forEach(menu => {
      if (menu.path) {
        paths.push(menu.path)
      }
      if (menu.children) {
        traverse(menu.children)
      }
    })
  }

  traverse(menus)
  return paths
}

/**
 * 检查用户是否有某个菜单权限
 * @param {string} menuPath - 菜单路径
 * @param {Array} userMenus - 用户菜单树
 * @returns {boolean} 是否有权限
 */
export function hasMenuPermission(menuPath, userMenus) {
  const paths = getMenuPaths(userMenus)
  return paths.includes(menuPath)
}

export default {
  loadComponent,
  menuToRoute,
  menusToRoutes,
  addRoutes,
  getMenuPaths,
  hasMenuPermission
}
