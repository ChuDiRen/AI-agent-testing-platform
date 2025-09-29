import { getToken } from '@/utils'

const WHITE_LIST = ['/login'] // 白名单路由

export function setupRouterGuard(router) {
  // 全局前置守卫
  router.beforeEach(async (to, from, next) => {
    // 开始加载条
    window.$loadingBar?.start()
    
    const token = getToken()
    
    // 如果有token
    if (token) {
      if (to.path === '/login') {
        // 已登录状态访问登录页，重定向到首页
        next({ path: '/' })
      } else {
        next()
      }
    } else {
      // 没有token
      if (WHITE_LIST.includes(to.path)) {
        // 在白名单中，直接访问
        next()
      } else {
        // 不在白名单中，重定向到登录页
        next({ path: '/login', query: { redirect: to.fullPath } })
      }
    }
  })
  
  // 全局后置守卫
  router.afterEach((to) => {
    // 结束加载条
    window.$loadingBar?.finish()
    
    // 设置页面标题
    document.title = to.meta?.title ? `${to.meta.title} - AI Agent Testing Platform` : 'AI Agent Testing Platform'
  })
  
  // 路由错误处理
  router.onError((error) => {
    console.error('路由错误:', error)
    window.$loadingBar?.error()
  })
}
