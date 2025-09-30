import { darkTheme } from 'naive-ui'

export function setupNaiveUI(app) {
  // Naive UI 全局配置
  app.config.globalProperties.$NAIVE = {
    theme: darkTheme,
  }

  // 添加 $Monitor 全局属性（用于监控功能）
  app.config.globalProperties.$Monitor = {
    // 监控相关的方法和属性
    log: (message, level = 'info') => {
      console.log(`[Monitor ${level.toUpperCase()}]:`, message)
    },
    error: (error) => {
      console.error('[Monitor ERROR]:', error)
    },
    warn: (message) => {
      console.warn('[Monitor WARN]:', message)
    },
    // 可以根据需要添加更多监控功能
    track: (event, data = {}) => {
      console.log(`[Monitor TRACK]: ${event}`, data)
    }
  }
}

export { darkTheme }
