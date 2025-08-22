import { defineStore } from 'pinia'
import type { 
  RoleInfo, 
  MenuTreeNode, 
  DeptTreeNode,
  UserInfo 
} from '@/api/types'

// 系统管理状态接口
interface SystemState {
  // 菜单相关
  menuList: MenuTreeNode[]
  menuTree: MenuTreeNode[]
  
  // 角色相关
  roleList: RoleInfo[]
  currentRole: RoleInfo | null
  
  // 部门相关
  deptList: DeptTreeNode[]
  deptTree: DeptTreeNode[]
  
  // 用户相关
  userList: UserInfo[]
  currentUser: UserInfo | null
  
  // 界面状态
  collapsed: boolean // 侧边栏折叠状态
  loading: boolean
  
  // 分页信息
  pagination: {
    page: number
    size: number
    total: number
  }
}

export const useSystemStore = defineStore('system', {
  state: (): SystemState => ({
    // 菜单相关
    menuList: [],
    menuTree: [],
    
    // 角色相关
    roleList: [],
    currentRole: null,
    
    // 部门相关
    deptList: [],
    deptTree: [],
    
    // 用户相关
    userList: [],
    currentUser: null,
    
    // 界面状态
    collapsed: false,
    loading: false,
    
    // 分页信息
    pagination: {
      page: 1,
      size: 10,
      total: 0
    }
  }),

  getters: {
    // 获取顶级菜单
    topMenus: (state) => state.menuList.filter(menu => menu.parent_id === 0),
    
    // 获取菜单映射
    menuMap: (state) => {
      const map = new Map<number, MenuTreeNode>()
      const addToMap = (menus: MenuTreeNode[]) => {
        menus.forEach(menu => {
          map.set(menu.menu_id, menu)
          if (menu.children) {
            addToMap(menu.children)
          }
        })
      }
      addToMap(state.menuList)
      return map
    },
    
    // 获取角色映射
    roleMap: (state) => {
      const map = new Map<number, RoleInfo>()
      state.roleList.forEach(role => {
        map.set(role.role_id, role)
      })
      return map
    },
    
    // 获取部门映射
    deptMap: (state) => {
      const map = new Map<number, DeptTreeNode>()
      const addToMap = (depts: DeptTreeNode[]) => {
        depts.forEach(dept => {
          map.set(dept.dept_id, dept)
          if (dept.children) {
            addToMap(dept.children)
          }
        })
      }
      addToMap(state.deptList)
      return map
    },
    
    // 获取用户映射
    userMap: (state) => {
      const map = new Map<number, UserInfo>()
      state.userList.forEach(user => {
        map.set(user.user_id, user)
      })
      return map
    }
  },

  actions: {
    // 设置侧边栏折叠状态
    setCollapsed(collapsed: boolean) {
      this.collapsed = collapsed
    },
    
    // 切换侧边栏折叠状态
    toggleCollapsed() {
      this.collapsed = !this.collapsed
    },
    
    // 设置加载状态
    setLoading(loading: boolean) {
      this.loading = loading
    },
    
    // 设置分页信息
    setPagination(pagination: Partial<SystemState['pagination']>) {
      this.pagination = { ...this.pagination, ...pagination }
    },
    
    // 重置分页信息
    resetPagination() {
      this.pagination = {
        page: 1,
        size: 10,
        total: 0
      }
    },
    
    // 菜单相关方法
    setMenuList(menuList: MenuTreeNode[]) {
      this.menuList = menuList
    },
    
    setMenuTree(menuTree: MenuTreeNode[]) {
      this.menuTree = menuTree
    },
    
    addMenu(menu: MenuTreeNode) {
      this.menuList.push(menu)
    },
    
    updateMenu(menu: MenuTreeNode) {
      const index = this.menuList.findIndex(m => m.menu_id === menu.menu_id)
      if (index !== -1) {
        this.menuList[index] = menu
      }
    },
    
    removeMenu(menuId: number) {
      this.menuList = this.menuList.filter(m => m.menu_id !== menuId)
    },
    
    // 角色相关方法
    setRoleList(roleList: RoleInfo[]) {
      this.roleList = roleList
    },
    
    setCurrentRole(role: RoleInfo | null) {
      this.currentRole = role
    },
    
    addRole(role: RoleInfo) {
      this.roleList.push(role)
    },
    
    updateRole(role: RoleInfo) {
      const index = this.roleList.findIndex(r => r.role_id === role.role_id)
      if (index !== -1) {
        this.roleList[index] = role
      }
    },
    
    removeRole(roleId: number) {
      this.roleList = this.roleList.filter(r => r.role_id !== roleId)
    },
    
    // 部门相关方法
    setDeptList(deptList: DeptTreeNode[]) {
      this.deptList = deptList
    },
    
    setDeptTree(deptTree: DeptTreeNode[]) {
      this.deptTree = deptTree
    },
    
    addDept(dept: DeptTreeNode) {
      this.deptList.push(dept)
    },
    
    updateDept(dept: DeptTreeNode) {
      const index = this.deptList.findIndex(d => d.dept_id === dept.dept_id)
      if (index !== -1) {
        this.deptList[index] = dept
      }
    },
    
    removeDept(deptId: number) {
      this.deptList = this.deptList.filter(d => d.dept_id !== deptId)
    },
    
    // 用户相关方法
    setUserList(userList: UserInfo[]) {
      this.userList = userList
    },
    
    setCurrentUser(user: UserInfo | null) {
      this.currentUser = user
    },
    
    addUser(user: UserInfo) {
      this.userList.push(user)
    },
    
    updateUser(user: UserInfo) {
      const index = this.userList.findIndex(u => u.user_id === user.user_id)
      if (index !== -1) {
        this.userList[index] = user
      }
    },
    
    removeUser(userId: number) {
      this.userList = this.userList.filter(u => u.user_id !== userId)
    },
    
    // 清空所有数据
    clearAll() {
      this.menuList = []
      this.menuTree = []
      this.roleList = []
      this.currentRole = null
      this.deptList = []
      this.deptTree = []
      this.userList = []
      this.currentUser = null
      this.resetPagination()
    }
  },

  // 持久化配置
  persist: {
    key: 'system_store',
    storage: localStorage,
    paths: ['collapsed']
  }
})