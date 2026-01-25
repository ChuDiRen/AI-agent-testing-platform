/**
 * 组件映射配置
 * 静态映射所有页面组件，避免Vite动态导入问题
 */

// 静态导入所有组件
const componentModules = {
  // 工作台
  workbench: () => import('@/views/workbench/index.vue'),
  
  // API测试模块
  'apitest/project': () => import('@/views/apitest/project/index.vue'),
  'apitest/apiinfo': () => import('@/views/apitest/apiinfo/index.vue'),
  'apitest/apiinfocase': () => import('@/views/apitest/apiinfocase/index.vue'),
  'apitest/collection': () => import('@/views/apitest/collection/index.vue'),
  'apitest/keyword': () => import('@/views/apitest/keyword/index.vue'),
  'apitest/apiMate': () => import('@/views/apitest/apiMate/index.vue'),
  
  // 消息管理模块
  'msgmanage': () => import('@/views/msgmanage/index.vue'),
  'msgmanage/feishu': () => import('@/views/msgmanage/index.vue'),
  'msgmanage/dingding': () => import('@/views/msgmanage/index.vue'),
  'msgmanage/wechat': () => import('@/views/msgmanage/index.vue'),
  
  // 系统管理模块
  'system/users': () => import('@/views/system/users/index.vue'),
  'system/roles': () => import('@/views/system/roles/index.vue'),
  'system/menus': () => import('@/views/system/menus/index.vue'),
  'system/depts': () => import('@/views/system/depts/index.vue'),
  'system/apis': () => import('@/views/system/apis/index.vue'),
  'system/auditlogs': () => import('@/views/system/auditlogs/index.vue'),
  'system/settings': () => import('@/views/system/settings/index.vue'),
  
  // 个人中心
  'profile': () => import('@/views/profile/index.vue'),
}

/**
 * 根据组件路径获取组件加载器
 * @param {string} componentPath - 组件路径
 * @returns {Function} 组件加载函数
 */
export function getComponentLoader(componentPath) {
  const loader = componentModules[componentPath]
  
  if (loader) {
    return loader
  }
  
  // 如果没有找到，返回一个空组件
  return () => import('@/views/NotFound.vue')
}

/**
 * 检查组件是否存在
 * @param {string} componentPath - 组件路径
 * @returns {boolean} 是否存在
 */
export function hasComponent(componentPath) {
  return componentModules.hasOwnProperty(componentPath)
}

/**
 * 获取所有可用的组件路径
 * @returns {Array} 组件路径列表
 */
export function getAllComponentPaths() {
  return Object.keys(componentModules)
}

/**
 * 创建组件映射表（用于调试）
 */
export function createComponentMap() {
  const map = new Map()
  
  for (const [path, loader] of Object.entries(componentModules)) {
    map.set(path, loader)
  }
  
  return map
}

// 开发环境下打印组件映射信息
if (process.env.NODE_ENV === 'development') {
  // 开发环境组件映射信息
}

export default {
  componentModules,
  getComponentLoader,
  hasComponent,
  getAllComponentPaths,
  createComponentMap
}
