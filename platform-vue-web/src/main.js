import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import App from './App.vue'
import 'virtual:windi.css'
import router from './router/index.js'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import directives from './directives/permission.js'
import { getPerformanceMonitor } from '~/utils/performanceMonitor'

// 引入 Element-Plus-X 组件
import ElementPlusX from 'vue-element-plus-x'

// 引入自定义主题和样式
import './styles/theme.css'
import './styles/common-list.css'
import './styles/common-form.css'

/**
 * 初始化主题
 * 优先从 localStorage 恢复用户的主题偏好，否则使用系统默认
 */
function initTheme() {
  const savedTheme = localStorage.getItem('theme')
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const theme = savedTheme || (prefersDark ? 'dark' : 'light')
  
  // 设置到 document
  document.documentElement.setAttribute('data-theme', theme)
  
  // 确保 localStorage 中有保存的主题
  if (!savedTheme) {
    localStorage.setItem('theme', theme)
  }
  
  console.log(`主题已初始化: ${theme}`)
}

// 初始化主题（在应用启动时）
initTheme()

/**
 * 初始化性能监控
 * 仅在生产环境或开发模式下启用（可通过环境变量控制）
 */
function initPerformanceMonitoring() {
  // 可以根据环境变量控制是否启用性能监控
  // if (import.meta.env.PROD || import.meta.env.DEV) {
    try {
      const monitor = getPerformanceMonitor()
      monitor.start()
      console.log('性能监控已启动')
    } catch (error) {
      console.warn('性能监控启动失败:', error)
    }
  // }
}

// 创建 Pinia 实例
const pinia = createPinia()

const app = createApp(App)

// 过滤 Element Plus 的 slot 警告（已知的兼容性问题，不影响功能）
app.config.warnHandler = (msg, instance, trace) => {
  if (msg.includes('Slot "default" invoked outside of the render function')) {
    return // 忽略此警告
  }
  console.warn(`[Vue warn]: ${msg}${trace}`)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})
app.use(ElementPlusX)

// 注册全局图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册全局权限指令
app.directive('permission', directives.permission)
app.directive('role', directives.role)

// 初始化性能监控
initPerformanceMonitoring()

app.mount('#app')

// 页面加载完成后输出性能指标
window.addEventListener('load', () => {
  setTimeout(() => {
    const monitor = getPerformanceMonitor()
    const metrics = monitor.getMetrics()
    if (metrics) {
      console.log('=== 应用性能指标 ===')
      console.log('FCP (首次内容绘制):', metrics.fcp ? `${metrics.fcp.toFixed(2)}ms` : '未检测到')
      console.log('LCP (最大内容绘制):', metrics.lcp ? `${metrics.lcp.toFixed(2)}ms` : '未检测到')
      console.log('FID (首次输入延迟):', metrics.fid ? `${metrics.fid.toFixed(2)}ms` : '未检测到')
      console.log('CLS (累积布局偏移):', metrics.cls !== null ? metrics.cls.toFixed(4) : '未检测到')
      console.log('页面加载时间:', metrics.pageLoad ? `${metrics.pageLoad.total.toFixed(2)}ms` : '未检测到')
      console.log('====================')
    }
  }, 1000)
})


