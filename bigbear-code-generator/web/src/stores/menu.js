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
          const menuData = response.data.data || []
          this.setMenus(menuData)
          return menuData
        } else {
          this.setMenus([])
          return []
        }
      } catch (error) {
        this.setMenus([])
        return []
      }
    }
  }
})
