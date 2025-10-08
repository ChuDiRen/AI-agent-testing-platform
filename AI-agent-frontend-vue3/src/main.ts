// Copyright (c) 2025 左岚. All rights reserved.
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import pinia from './store'

import 'virtual:windi.css'
import './assets/main.css'
import './assets/animations.css'
import './assets/components.css'

// 导入插件系统
import { pluginRegistry } from './plugins'
import apiEnginePlugin from './plugins/api-engine'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(pinia)
app.use(router)

// 注册API引擎插件
pluginRegistry.register(apiEnginePlugin)

// 初始化插件(加载插件路由和store)
// 将插件路由作为MainLayout的子路由添加
const pluginRoutes = pluginRegistry.getRoutes()
pluginRoutes.forEach(route => {
  router.addRoute('MainLayout', route) // 添加到MainLayout下,使插件页面也有侧边栏和顶部导航
})

app.mount('#app')
