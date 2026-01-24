/**
 * 应用store模块 - 参考vue-fastapi-admin实现
 * 管理应用全局状态
 */
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state() {
    return {
      collapsed: false, // 侧边栏折叠状态
      asideWidth: '250px',
    }
  },
  getters: {
    sidebarWidth: (state) => (state.collapsed ? '64px' : state.asideWidth),
  },
  actions: {
    toggleCollapse() {
      this.collapsed = !this.collapsed
    },
    setAsideWidth(width) {
      this.asideWidth = width
    },
  },
})

