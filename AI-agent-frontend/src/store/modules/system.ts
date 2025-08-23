import { defineStore } from 'pinia'
import type { MenuInfo, RoleInfo, DeptInfo, UserInfo } from '@/api/types'

export interface SystemState {
  menuList: MenuInfo[]
  roleList: RoleInfo[]
  deptList: DeptInfo[]
  userList: UserInfo[]
  collapsed: boolean
  pagination: {
    page: number
    size: number
    total: number
  }
}

export const useSystemStore = defineStore('system', {
  state: (): SystemState => ({
    menuList: [],
    roleList: [],
    deptList: [],
    userList: [],
    collapsed: false,
    pagination: {
      page: 1,
      size: 10,
      total: 0
    }
  }),

  getters: {
    topMenus: (state) => {
      return state.menuList.filter(menu => menu.parent_id === 0)
    },
    menuMap: (state) => {
      const map = new Map()
      state.menuList.forEach(menu => {
        map.set(menu.menu_id, menu)
      })
      return map
    },
    roleMap: (state) => {
      const map = new Map()
      state.roleList.forEach(role => {
        map.set(role.role_id, role)
      })
      return map
    },
    deptMap: (state) => {
      const map = new Map()
      state.deptList.forEach(dept => {
        map.set(dept.dept_id, dept)
      })
      return map
    },
    userMap: (state) => {
      const map = new Map()
      state.userList.forEach(user => {
        map.set(user.user_id, user)
      })
      return map
    }
  },

  actions: {
    // 切换侧边栏折叠状态
    toggleCollapsed() {
      this.collapsed = !this.collapsed
    },

    // 设置侧边栏折叠状态
    setCollapsed(collapsed: boolean) {
      this.collapsed = collapsed
    },

    // 设置菜单列表
    setMenuList(menuList: MenuInfo[]) {
      this.menuList = menuList
    },

    // 设置角色列表
    setRoleList(roleList: RoleInfo[]) {
      this.roleList = roleList
    },

    // 设置部门列表
    setDeptList(deptList: DeptInfo[]) {
      this.deptList = deptList
    },

    // 设置用户列表
    setUserList(userList: UserInfo[]) {
      this.userList = userList
    },

    // 设置分页信息
    setPagination(pagination: Partial<SystemState['pagination']>) {
      this.pagination = { ...this.pagination, ...pagination }
    },

    // 重置分页
    resetPagination() {
      this.pagination = {
        page: 1,
        size: 10,
        total: 0
      }
    }
  },

  persist: {
    key: 'system-store',
    storage: localStorage
  }
})