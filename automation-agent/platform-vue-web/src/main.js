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
// 导入全局设计系统
import './styles/design-system.css'
// 导入图标的第三包
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// 引入 store
import store from './store' 
import zhCn from 'element-plus/es/locale/lang/zh-cn' // 引入中文语言包
// 导入权限管理
import { permissionDirective, checkRoutePermission } from './utils/permission'

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

// 注册权限指令
app.directive('permission', permissionDirective)

// 图标需要加的代码
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 添加路由权限守卫
router.beforeEach(async (to, from, next) => {
  // 检查登录状态
  const token = localStorage.getItem('token')
  const username = localStorage.getItem('username')
  
  // 未登录且不是登录页面，重定向到登录页
  if ((!token || !username) && to.path !== '/login') {
    next('/login')
    return
  }
  
  // 已登录访问登录页，重定向到首页
  if (token && username && to.path === '/login') {
    next('/home')
    return
  }
  
  // 检查路由权限
  if (token && username && to.path !== '/login') {
    try {
      // 如果 store 中没有权限信息，先加载
      if (!store.state.permissions || store.state.permissions.menus.length === 0) {
        await store.dispatch('getUserPermissions')
        await store.dispatch('getUserInfo')
      }
      
      // 检查是否为超级管理员
      const isSuperUser = store.getters.isSuperUser
      if (isSuperUser) {
        next()
        return
      }
      
      // 检查菜单权限
      const hasPermission = store.getters.hasMenuPermission(to.path)
      
      // 对于首页、统计页面和管理页面，允许所有登录用户访问
      const publicPaths = ['/home', '/Statistics', '/profile', '/settings', '/userList', '/roleList', '/menuList', '/deptList', '/apiList', '/auditLogList']
      if (publicPaths.includes(to.path) || hasPermission) {
        next()
        return
      }
      
      // 权限不足
      console.warn(`用户无权限访问页面: ${to.path}`)
      ElMessage.error('权限不足，无法访问该页面')
      next('/home')
      return
      
    } catch (error) {
      console.error('权限检查失败:', error)
      // 权限检查失败时，允许访问首页和公共页面
      const publicPaths = ['/home', '/Statistics', '/profile', '/settings', '/userList', '/roleList', '/menuList', '/deptList', '/apiList', '/auditLogList']
      if (publicPaths.includes(to.path)) {
        next()
      } else {
        next('/home')
      }
      return
    }
  }
  
  next()
})

// 将应用挂载到DOM元素 #app
app.mount('#app')
