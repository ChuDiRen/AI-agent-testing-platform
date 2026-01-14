import { defineStore } from 'pinia'

/**
 * 菜单状态管理
 * 包括：用户动态菜单等
 */
export const useMenuStore = defineStore('menu', {
  state: () => ({
    menus: [] // 用户动态菜单
  }),

  actions: {
    /**
     * 设置用户菜单
     */
    setMenus(menus) {
      this.menus = menus
    },

    /**
     * 获取用户菜单
     */
    async fetchUserMenus() {
      try {
        const { getCurrentUserMenus } = await import('~/views/system/menu/menu.js')
        const response = await getCurrentUserMenus()

        if (response.data.code === 200) {
          this.setMenus(response.data.data || [])
          return response.data.data || []
        } else {
          console.error('获取用户菜单失败:', response.data.msg)
          this.setMenus([])
          return []
        }
      } catch (error) {
        console.error('获取用户菜单异常:', error)
        this.setMenus([])
        return []
      }
    }
  }
})
