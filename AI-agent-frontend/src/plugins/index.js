import { darkTheme } from 'naive-ui'

export function setupNaiveUI(app) {
  // Naive UI 全局配置
  app.config.globalProperties.$NAIVE = {
    theme: darkTheme,
  }
}

export { darkTheme }
