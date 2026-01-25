/**
 * 动态路由构建工具
 * 将后端返回的菜单数据转换为Vue Router路由配置
 * 参考vue-fastapi-admin的实现
 */

/**
 * 组件映射表
 * 将菜单的component字段映射到实际的组件
 */
const componentMap = {
  // 首页
  'home/home': () => import('~/views/home/home.vue'),
  
  // API测试 - 项目管理
  'apitest/project/ApiProjectList': () => import('~/views/apitest/project/ApiProjectList.vue'),
  'apitest/project/ApiProjectForm': () => import('~/views/apitest/project/ApiProjectForm.vue'),
  
  // API测试 - 关键字管理
  'apitest/keyword/ApiKeyWordList': () => import('~/views/apitest/keyword/ApiKeyWordList.vue'),
  'apitest/keyword/ApiKeyWordForm': () => import('~/views/apitest/keyword/ApiKeyWordForm.vue'),
  
  // API测试 - 素材维护
  'apitest/apiMate/ApiMateManageList': () => import('~/views/apitest/apiMate/ApiMateManageList.vue'),
  'apitest/apiMate/ApiMateManageForm': () => import('~/views/apitest/apiMate/ApiMateManageForm.vue'),
  
  // API测试 - 接口信息
  'apitest/apiinfo/ApiInfoList': () => import('~/views/apitest/apiinfo/ApiInfoList.vue'),
  'apitest/apiinfo/ApiInfoForm': () => import('~/views/apitest/apiinfo/ApiInfoForm.vue'),
  
  // API测试 - 用例信息
  'apitest/apiinfocase/ApiInfoCaseList': () => import('~/views/apitest/apiinfocase/ApiInfoCaseList.vue'),
  'apitest/apiinfocase/ApiInfoCaseForm': () => import('~/views/apitest/apiinfocase/ApiInfoCaseForm.vue'),
  
  // API测试 - 测试计划
  'apitest/collection/ApiCollectionInfoList': () => import('~/views/apitest/collection/ApiCollectionInfoList.vue'),
  'apitest/collection/ApiCollectionInfoForm': () => import('~/views/apitest/collection/ApiCollectionInfoForm.vue'),
  'apitest/collection/ApiPlanChartForm': () => import('~/views/apitest/collection/ApiPlanChartForm.vue'),
  
  // 消息管理
  'apitest/msgmanage/WeChartMsgManageList': () => import('~/views/apitest/msgmanage/WeChartMsgManageList.vue'),
  'apitest/msgmanage/WeChartMsgManageForm': () => import('~/views/apitest/msgmanage/WeChartMsgManageForm.vue'),
  'apitest/msgmanage/DingDingMsgManageList': () => import('~/views/apitest/msgmanage/DingDingMsgManageList.vue'),
  'apitest/msgmanage/DingDingMsgManageForm': () => import('~/views/apitest/msgmanage/DingDingMsgManageForm.vue'),
  'apitest/msgmanage/FeiShuMsgManageList': () => import('~/views/apitest/msgmanage/FeiShuMsgManageList.vue'),
  'apitest/msgmanage/FeishuMsgManageForm': () => import('~/views/apitest/msgmanage/FeishuMsgManageForm.vue'),
  
  // 系统管理 - 用户管理
  'users/userList': () => import('~/views/system/users/userList.vue'),
  'users/userForm': () => import('~/views/system/users/userForm.vue'),
  
  // 系统管理 - 角色管理
  'roles/roleList': () => import('~/views/system/roles/roleList.vue'),
  'roles/roleForm': () => import('~/views/system/roles/roleForm.vue'),
  'roles/roleMenu': () => import('~/views/system/roles/roleMenu.vue'),
  'roles/roleApi': () => import('~/views/system/roles/roleApi.vue'),
  'roles/rolePermission': () => import('~/views/system/roles/rolePermission.vue'),
  
  // 系统管理 - 菜单管理
  'menus/menuList': () => import('~/views/system/menus/menuList.vue'),
  'menus/menuForm': () => import('~/views/system/menus/menuForm.vue'),
  
  // 系统管理 - 部门管理
  'depts/deptList': () => import('~/views/system/depts/deptList.vue'),
  'depts/deptForm': () => import('~/views/system/depts/deptForm.vue'),
  'depts/index': () => import('~/views/system/depts/index.vue'),
  
  // 系统管理 - API管理
  'apis/apiList': () => import('~/views/system/apis/apiList.vue'),
  'apis/apiForm': () => import('~/views/system/apis/apiForm.vue'),
  
  // 系统管理 - 审计日志
  'auditlogs/auditLogList': () => import('~/views/system/auditlogs/auditLogList.vue'),
  
  // 其他页面
  'profile/profile': () => import('~/views/system/profile/profile.vue'),
  'settings/settings': () => import('~/views/system/settings/settings.vue'),
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
    return componentMap['notFound'] || (() => import('~/views/NotFound.vue'))
  }

  const component = componentMap[componentName]
  if (component) {
    return component
  }

  return componentMap['notFound'] || (() => import('~/views/NotFound.vue'))
}

/**
 * 将菜单项转换为路由配置
 * 参考vue-fastapi-admin的buildRoutes函数
 * @param {Object} menu - 菜单项对象
 * @returns {Object} 路由配置对象
 */
export function menuToRoute(menu) {
  const route = {
    name: menu.name || menu.id,
    path: menu.path,
    isHidden: menu.is_hidden || false,
    redirect: menu.redirect,
    meta: {
      title: menu.name,
      icon: menu.icon,
      order: menu.order,
      keepAlive: menu.keepalive !== false, // 默认启用缓存
    },
    children: []
  }

  // 处理子菜单
  if (menu.children && menu.children.length > 0) {
    // 有子菜单
    route.children = menu.children.map(child => ({
      name: child.name,
      path: child.path,
      component: loadComponent(child.component),
      isHidden: child.is_hidden || false,
      meta: {
        title: child.name,
        icon: child.icon,
        order: child.order,
        keepAlive: child.keepalive !== false,
      },
    }))
  } else {
    // 没有子菜单，创建一个默认的子路由
    route.children.push({
      name: `${menu.name}Default`,
      path: '',
      component: loadComponent(menu.component),
      isHidden: true,
      meta: {
        title: menu.name,
        icon: menu.icon,
        order: menu.order,
        keepAlive: menu.keepalive !== false,
      },
    })
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
    return []
  }

  // 过滤掉隐藏的菜单
  const visibleMenus = menus.filter(menu => !menu.is_hidden)

  return visibleMenus.map(menu => menuToRoute(menu))
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

  // 将新路由直接添加到根路由
  routes.forEach(route => {
    if (!router.hasRoute(route.name)) {
      router.addRoute(route)
    }
  })
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
