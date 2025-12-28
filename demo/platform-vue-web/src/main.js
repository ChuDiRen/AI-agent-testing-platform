// src/main.js
import { createApp } from 'vue'
// import './style.css'
import App from './App.vue'
import router from './router'  // 引入路由配置
// 导入ElementPlus组件库
import ElementPlus from 'element-plus'
// 导入ElementPlus样式
import 'element-plus/dist/index.css'
// 导入import 'virtual:windi.css'样式
import 'virtual:windi.css'
// 导入图标的第三包
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// 引入 store
import store from './store' 
import zhCn from 'element-plus/es/locale/lang/zh-cn' // 引入中文语言包

// 创建Vue应用实例
const app = createApp(App)

// 全局注册ElementPlus
// app.use(ElementPlus)

// 使用路由插件 - 关键步骤
app.use(router)

// 引用store
app.use(store)

// 配置 Element Plus 使用中文
app.use(ElementPlus, {
  locale: zhCn,
})

// 图标需要加的代码
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 将应用挂载到DOM元素 #app
app.mount('#app')
