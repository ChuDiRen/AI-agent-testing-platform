import { defineStore } from 'pinia'

/**
 * 响应式断点配置
 */
const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
  laptop: 1366,
  desktop: 1920
}

/**
 * 应用全局状态管理
 * 包括：侧边栏宽度、主题模式、响应式状态等
 */
export const useAppStore = defineStore('app', {
  state: () => ({
    asideWidth: getInitialAsideWidth(),
    theme: localStorage.getItem('theme') || 'light',
    windowWidth: window.innerWidth,
    windowHeight: window.innerHeight
  }),

  getters: {
    // 是否是移动端
    isMobile: (state) => state.windowWidth <= BREAKPOINTS.mobile,
    
    // 是否是平板
    isTablet: (state) => state.windowWidth > BREAKPOINTS.mobile && state.windowWidth <= BREAKPOINTS.tablet,
    
    // 是否是笔记本
    isLaptop: (state) => state.windowWidth > BREAKPOINTS.tablet && state.windowWidth <= BREAKPOINTS.laptop,
    
    // 是否是大屏
    isDesktop: (state) => state.windowWidth > BREAKPOINTS.laptop,
    
    // 是否是超大屏
    isLargeDesktop: (state) => state.windowWidth > BREAKPOINTS.desktop,
    
    // 当前设备类型
    deviceType: (state) => {
      if (state.windowWidth <= BREAKPOINTS.mobile) return 'mobile'
      if (state.windowWidth <= BREAKPOINTS.tablet) return 'tablet'
      if (state.windowWidth <= BREAKPOINTS.laptop) return 'laptop'
      if (state.windowWidth <= BREAKPOINTS.desktop) return 'desktop'
      return 'large-desktop'
    },
    
    // 侧边栏是否折叠
    isCollapsed: (state) => state.asideWidth === '64px' || state.asideWidth === '0px'
  },

  actions: {
    /**
     * 更新窗口尺寸
     */
    updateWindowSize(width, height) {
      this.windowWidth = width
      this.windowHeight = height
    },

    /**
     * 侧边栏宽度切换
     */
    handleAsideWidth() {
      const width = this.windowWidth
      if (width <= BREAKPOINTS.mobile) {
        // 移动端：显示/隐藏
        this.asideWidth = this.asideWidth === "0px" ? "250px" : "0px"
      } else if (width <= BREAKPOINTS.laptop) {
        // 笔记本：200px <-> 64px
        this.asideWidth = this.asideWidth === "200px" ? "64px" : "200px"
      } else {
        // 大屏：250px <-> 64px
        this.asideWidth = this.asideWidth === "250px" ? "64px" : "250px"
      }
      // 保存到 localStorage
      localStorage.setItem('asideWidth', this.asideWidth)
    },

    /**
     * 响应式调整侧边栏宽度（窗口大小变化时）
     */
    adjustAsideWidth() {
      const width = this.windowWidth
      const isCollapsed = this.asideWidth === "64px" || this.asideWidth === "0px"

      // 移动端特殊处理
      if (width <= BREAKPOINTS.mobile) {
        if (!isCollapsed) {
          this.asideWidth = "0px"
        }
        return
      }

      // 非移动端：保持折叠状态，只调整展开时的宽度
      if (isCollapsed) {
        this.asideWidth = "64px"
      } else {
        // 根据屏幕尺寸调整展开时的宽度
        if (width <= BREAKPOINTS.laptop) {
          this.asideWidth = "200px"
        } else {
          this.asideWidth = "250px"
        }
      }
      // 保存到 localStorage
      localStorage.setItem('asideWidth', this.asideWidth)
    },

    /**
     * 设置主题
     */
    setTheme(theme) {
      this.theme = theme
      document.documentElement.setAttribute('data-theme', theme)
      localStorage.setItem('theme', theme)
    },

    /**
     * 切换主题
     */
    toggleTheme() {
      const newTheme = this.theme === 'light' ? 'dark' : 'light'
      this.setTheme(newTheme)
    }
  }
})

/**
 * 根据屏幕宽度设置初始侧边栏宽度，优先从 localStorage 恢复
 */
function getInitialAsideWidth() {
  const width = window.innerWidth
  const savedWidth = localStorage.getItem('asideWidth')

  // 移动端始终返回 0px
  if (width <= BREAKPOINTS.mobile) {
    return "0px"
  }

  // 清理无效的 0px 状态（非移动端不应该是 0px）
  if (savedWidth === "0px") {
    localStorage.removeItem('asideWidth')
  }

  // 非移动端：忽略折叠状态，默认展开
  // 如果需要记住折叠状态，取消下面的注释
  // if (savedWidth === "64px") {
  //     return "64px"
  // }

  if (savedWidth === "200px" || savedWidth === "250px") {
    // 根据屏幕尺寸调整展开宽度
    const expandedWidth = width <= BREAKPOINTS.laptop ? "200px" : "250px"
    return expandedWidth
  }

  // 没有有效的保存宽度，使用默认展开状态
  const defaultWidth = width <= BREAKPOINTS.laptop ? "200px" : "250px"
  return defaultWidth
}

/**
 * 导出断点配置，供其他模块使用
 */
export { BREAKPOINTS }
