import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import App from './App.vue'
import 'virtual:windi.css'
import router from './router/index.js'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import store from './store/index.js'
import directives from './directives/permission.js'

// 引入 Element-Plus-X 组件
import ElementPlusX from 'vue-element-plus-x'
// 注意：CSS 样式通过 Vite 插件在 vite.config.js 中注入，避免 exports 限制问题
// import 'vue-element-plus-x/dist/index.css'

// 引入自定义主题和样式
import './styles/theme.css'
import './styles/common-list.css'
import './styles/common-form.css'

const app = createApp(App)
app.use(store)
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

