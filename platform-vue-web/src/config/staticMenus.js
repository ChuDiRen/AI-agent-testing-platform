/**
 * 静态菜单配置
 * 菜单结构说明:
 * - name: 菜单名称
 * - icon: Element Plus 图标组件名
 * - frontpath: 前端路由路径
 * - child: 子菜单数组
 */

export const staticMenus = [
  {
    name: '主页',
    icon: 'HomeFilled',
    frontpath: '/Statistics',
    child: []
  },
  {
    name: '系统管理',
    icon: 'Setting',
    frontpath: '',
    child: [
      {
        name: '用户管理',
        icon: 'User',
        frontpath: '/userList'
      },
      {
        name: '角色管理',
        icon: 'Avatar',
        frontpath: '/roleList'
      },
      {
        name: '菜单管理',
        icon: 'Menu',
        frontpath: '/menuList'
      },
      {
        name: '部门管理',
        icon: 'OfficeBuilding',
        frontpath: '/deptList'
      }
    ]
  },
  {
    name: '代码生成',
    icon: 'Cpu',
    frontpath: '',
    child: [
      {
        name: '代码生成器',
        icon: 'EditPen',
        frontpath: '/GeneratorCode'
      },
      {
        name: '表配置管理',
        icon: 'Grid',
        frontpath: '/GenTableList'
      },
      {
        name: '生成历史',
        icon: 'Clock',
        frontpath: '/GenHistory'
      }
    ]
  }
]

/**
 * 静态路由配置
 * 用于在 router 中注册
 * 包含所有页面路由（列表页 + 表单页）
 */
export const staticRoutes = [
  // ========== 主页 ==========
  {
    path: '/Statistics',
    component: () => import('~/views/statistics/statistics.vue'),
    meta: {
      title: '主页信息',
      permission: 'system:statistics:view'
    }
  },
  
  // ========== 系统管理 ==========
  // 用户管理
  {
    path: '/userList',
    component: () => import('~/views/system/users/userList.vue'),
    meta: {
      title: '用户管理',
      permission: 'system:user:view'
    }
  },
  {
    path: '/userForm',
    component: () => import('~/views/system/users/userForm.vue'),
    meta: {
      title: '用户表单'
    }
  },
  // 角色管理
  {
    path: '/roleList',
    component: () => import('~/views/system/role/roleList.vue'),
    meta: {
      title: '角色管理',
      permission: 'system:role:view'
    }
  },
  {
    path: '/roleForm',
    component: () => import('~/views/system/role/roleForm.vue'),
    meta: {
      title: '角色表单'
    }
  },
  // 菜单管理
  {
    path: '/menuList',
    component: () => import('~/views/system/menu/menuList.vue'),
    meta: {
      title: '菜单管理',
      permission: 'system:menu:view'
    }
  },
  {
    path: '/menuForm',
    component: () => import('~/views/system/menu/menuForm.vue'),
    meta: {
      title: '菜单表单'
    }
  },
  // 部门管理
  {
    path: '/deptList',
    component: () => import('~/views/system/dept/deptList.vue'),
    meta: {
      title: '部门管理',
      permission: 'system:dept:view'
    }
  },
  {
    path: '/deptForm',
    component: () => import('~/views/system/dept/deptForm.vue'),
    meta: {
      title: '部门表单'
    }
  },
  
  // ========== 代码生成 ==========
  // 代码生成器
  {
    path: '/GeneratorCode',
    component: () => import('~/views/generator/code/GeneratorCode.vue'),
    meta: {
      title: '代码生成器',
      permission: 'system:generatorcode:view'
    }
  },
  // 表配置管理
  {
    path: '/GenTableList',
    component: () => import('~/views/generator/table/GenTableList.vue'),
    meta: {
      title: '表配置管理',
      permission: 'system:gentablelist:view'
    }
  },
  {
    path: '/GenTableForm',
    component: () => import('~/views/generator/table/GenTableForm.vue'),
    meta: {
      title: '表配置表单'
    }
  },
  // 生成历史
  {
    path: '/GenHistory',
    component: () => import('~/views/generator/history/GenHistory.vue'),
    meta: {
      title: '生成历史',
      permission: 'system:genhistory:view'
    }
  }
]
