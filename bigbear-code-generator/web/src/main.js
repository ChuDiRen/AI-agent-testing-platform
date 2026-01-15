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
}

// 初始化主题（在应用启动时）
initTheme()

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

app.mount('#app')


