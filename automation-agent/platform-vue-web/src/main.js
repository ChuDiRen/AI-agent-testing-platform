// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import { setupRouter } from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'virtual:windi.css'
import './styles/design-system.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { pinia } from './store'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { permissionDirective } from './utils/permission'

// 开发环境导入调试工具
if (process.env.NODE_ENV === 'development') {
  // 调试工具已清理
}

const app = createApp(App)

// 使用Pinia状态管理
app.use(pinia)

// 配置Element Plus
app.use(ElementPlus, { locale: zhCn })

// 注册权限指令
app.directive('permission', permissionDirective)

// 注册图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 初始化路由并挂载应用
async function bootstrap() {
  await setupRouter(app)
  app.mount('#app')
}

bootstrap()
