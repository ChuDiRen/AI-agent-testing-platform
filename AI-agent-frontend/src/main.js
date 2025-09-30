import { createApp } from 'vue'
import App from './App.vue'
import { setupRouter } from './router'
import { setupStore } from './store'
import { setupNaiveUI } from './plugins'
import { setupDirectives } from './directives'
import { setupI18n } from './locales'

// 样式
import 'virtual:uno.css'
import 'virtual:svg-icons-register'
import '@/styles/index.scss'

async function bootstrap() {
  const app = createApp(App)

  // 全局错误处理
  app.config.errorHandler = (err, instance, info) => {
    console.error('Vue全局错误:', err)
    console.error('错误信息:', info)
    console.error('组件实例:', instance)
  }

  // 配置 store
  setupStore(app)

  // 配置路由
  await setupRouter(app)

  // 配置 naive-ui
  setupNaiveUI(app)

  // 配置自定义指令
  setupDirectives(app)

  // 配置国际化
  setupI18n(app)

  // 挂载应用
  app.mount('#app')
}

bootstrap()
