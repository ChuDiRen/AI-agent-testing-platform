import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import 'element-plus/dist/index.css'
import App from './App.vue'
import 'virtual:windi.css'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import store from '../src/store'
import directives from './directives/permission'

const app = createApp(App)
console.log(router)
app.use(store)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

// 注册全局图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册全局权限指令
app.directive('permission', directives.permission)
app.directive('role', directives.role)

app.mount('#app')

