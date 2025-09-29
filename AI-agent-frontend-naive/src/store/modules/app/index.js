import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state() {
    return {
      // 主题模式
      isDark: false,
      // 语言
      locale: 'zh-CN',
      // 侧边栏
      sidebarCollapsed: false,
      // 设备类型
      device: 'desktop',
      // 页面加载状态
      pageLoading: false,
      // 重新加载标识
      reloadFlag: true,
    }
  },
  
  getters: {
    // 是否为移动端
    isMobile: (state) => state.device === 'mobile',
  },
  
  actions: {
    // 切换主题
    toggleTheme() {
      this.isDark = !this.isDark
    },
    
    // 设置主题
    setTheme(isDark) {
      this.isDark = isDark
    },
    
    // 切换语言
    toggleLocale() {
      this.locale = this.locale === 'zh-CN' ? 'en-US' : 'zh-CN'
    },
    
    // 设置语言
    setLocale(locale) {
      this.locale = locale
    },
    
    // 切换侧边栏
    toggleSidebar() {
      this.sidebarCollapsed = !this.sidebarCollapsed
    },
    
    // 设置侧边栏状态
    setSidebarCollapsed(collapsed) {
      this.sidebarCollapsed = collapsed
    },
    
    // 设置设备类型
    setDevice(device) {
      this.device = device
    },
    
    // 设置页面加载状态
    setPageLoading(loading) {
      this.pageLoading = loading
    },
    
    // 重新加载页面
    async reloadPage() {
      this.reloadFlag = false
      await nextTick()
      this.reloadFlag = true
    },
  },
  
  persist: {
    key: 'app-store',
    storage: localStorage,
    paths: ['isDark', 'locale', 'sidebarCollapsed'],
  },
})
