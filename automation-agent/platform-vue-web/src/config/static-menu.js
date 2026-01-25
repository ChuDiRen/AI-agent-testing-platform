/**
 * 静态菜单配置
 * 基于现有功能模块生成的菜单结构
 */

// 导入组件映射
import { getComponentLoader } from './component-map'

// 静态菜单数据
export const staticMenus = [
  {
    name: '工作台',
    path: '/workbench',
    icon: 'Monitor',
    order: 1,
    component: 'workbench',
    keepalive: true,
    children: []
  },
  {
    name: 'API测试',
    path: '/apitest',
    icon: 'Connection',
    order: 2,
    children: [
      {
        name: '项目管理',
        path: 'project',
        icon: 'Folder',
        order: 1,
        component: 'apitest/project'
      },
      {
        name: 'API信息',
        path: 'apiinfo',
        icon: 'Document',
        order: 2,
        component: 'apitest/apiinfo'
      },
      {
        name: '用例管理',
        path: 'apiinfocase',
        icon: 'Operation',
        order: 3,
        component: 'apitest/apiinfocase'
      },
      {
        name: '用例集合',
        path: 'collection',
        icon: 'Collection',
        order: 4,
        component: 'apitest/collection'
      },
      {
        name: '关键字管理',
        path: 'keyword',
        icon: 'Key',
        order: 5,
        component: 'apitest/keyword'
      },
      {
        name: '素材管理',
        path: 'apiMate',
        icon: 'Picture',
        order: 6,
        component: 'apitest/apiMate'
      }
    ]
  },
  {
    name: '消息管理',
    path: '/msgmanage',
    icon: 'Message',
    order: 3,
    component: 'msgmanage',
    children: [
      {
        name: '飞书消息',
        path: 'feishu',
        icon: 'ChatDotRound',
        order: 1,
        component: 'msgmanage/feishu'
      },
      {
        name: '钉钉消息',
        path: 'dingding',
        icon: 'ChatDotSquare',
        order: 2,
        component: 'msgmanage/dingding'
      },
      {
        name: '微信消息',
        path: 'wechat',
        icon: 'ChatLineRound',
        order: 3,
        component: 'msgmanage/wechat'
      }
    ]
  },
  {
    name: '系统管理',
    path: '/system',
    icon: 'Setting',
    order: 4,
    children: [
      {
        name: '用户管理',
        path: 'users',
        icon: 'UserFilled',
        order: 1,
        component: 'system/users'
      },
      {
        name: '角色管理',
        path: 'roles',
        icon: 'Avatar',
        order: 2,
        component: 'system/roles'
      },
      {
        name: '菜单管理',
        path: 'menus',
        icon: 'Menu',
        order: 3,
        component: 'system/menus'
      },
      {
        name: '部门管理',
        path: 'depts',
        icon: 'OfficeBuilding',
        order: 4,
        component: 'system/depts'
      },
      {
        name: 'API权限',
        path: 'apis',
        icon: 'Key',
        order: 5,
        component: 'system/apis'
      },
      {
        name: '审计日志',
        path: 'auditlogs',
        icon: 'Document',
        order: 6,
        component: 'system/auditlogs'
      },
      {
        name: '系统设置',
        path: 'settings',
        icon: 'Tools',
        order: 7,
        component: 'system/settings',
        is_hidden: true
      }
    ]
  },
  {
    name: '个人中心',
    path: '/profile',
    icon: 'User',
    order: 99,
    is_hidden: true,
    component: 'profile',
    children: []
  }
]

/**
 * 构建路由的辅助函数
 * @param {Array} menus - 菜单数据
 * @returns {Array} 路由配置
 */
export function buildStaticRoutes(menus = staticMenus) {
  return menus.map(menu => {
    const route = {
      name: menu.name,
      path: menu.path,
      component: () => import('@/layout/index.vue'),
      isHidden: menu.is_hidden || false,
      meta: {
        title: menu.name,
        icon: menu.icon,
        order: menu.order,
        keepAlive: menu.keepalive || false,
      },
      children: []
    }
    
    // 处理子菜单
    if (menu.children && menu.children.length > 0) {
      route.children = menu.children.map(child => {
        // 使用组件映射获取组件加载器
        const componentLoader = getComponentLoader(child.component)
        
        return {
          name: `${menu.name}${child.name}`,
          path: child.path, // 子路由使用相对路径
          component: componentLoader,
          meta: {
            title: child.name,
            icon: child.icon,
            order: child.order,
            keepAlive: child.keepalive || false,
          },
          isHidden: child.is_hidden || false
        }
      })
    } else if (menu.component) {
      // 没有子菜单但有组件，创建默认子路由
      const componentLoader = getComponentLoader(menu.component)
      
      route.children.push({
        name: `${menu.name}Default`,
        path: '',
        component: componentLoader,
        isHidden: true, // 设置为隐藏，不在菜单中显示但可访问
        meta: {
          title: menu.name,
          icon: menu.icon,
          order: menu.order,
          keepAlive: menu.keepalive || false,
        },
      })
    }
    
    return route
  })
}

/**
 * 获取扁平化的菜单列表（用于权限验证等）
 * @param {Array} menus - 菜单数据
 * @returns {Array} 扁平化的菜单列表
 */
export function getFlatMenus(menus = staticMenus) {
  const flatMenus = []
  
  function traverse(items) {
    items.forEach(item => {
      flatMenus.push({
        name: item.name,
        path: item.path,
        icon: item.icon,
        order: item.order,
        component: item.component
      })
      
      if (item.children && item.children.length > 0) {
        traverse(item.children)
      }
    })
  }
  
  traverse(menus)
  return flatMenus
}

/**
 * 根据路径查找菜单
 * @param {string} path - 路径
 * @param {Array} menus - 菜单数据
 * @returns {Object|null} 菜单项
 */
export function findMenuByPath(path, menus = staticMenus) {
  for (const menu of menus) {
    // 检查父菜单路径
    if (menu.path === path) {
      return menu
    }
    
    // 检查子菜单路径（需要拼接父路径）
    if (menu.children && menu.children.length > 0) {
      for (const child of menu.children) {
        const childFullPath = `${menu.path}/${child.path}`.replace('//', '/')
        if (childFullPath === path) {
          return child
        }
      }
      
      // 递归检查更深层的子菜单
      const found = findMenuByPath(path, menu.children)
      if (found) return found
    }
  }
  
  return null
}

// 默认导出
export default {
  staticMenus,
  buildStaticRoutes,
  getFlatMenus,
  findMenuByPath
}
