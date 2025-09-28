import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import pinia from '@/store/store'
import { setupPermissionDirectives } from '@/directives/permission'
import { formatStandardDateTime, formatDate, formatTime } from '@/utils/dateFormat'
import { initTokenValidator } from '@/utils/tokenValidator' // 导入token验证器
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'

// 公共样式引入
import './assets/style/reset.scss'
import './assets/style/global.scss'
import './assets/style/table-fix.scss'

// 在应用启动前初始化token验证器
console.log('Initializing application...')
const tokenCleanedUp = initTokenValidator()

if (tokenCleanedUp) {
  console.log('Invalid tokens detected and cleaned up. User will need to re-login.')
}

const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(ElementPlus, { locale: zhCn })
setupPermissionDirectives(app)

// 注册全局时间格式化方法
app.config.globalProperties.$formatDateTime = formatStandardDateTime
app.config.globalProperties.$formatDate = formatDate
app.config.globalProperties.$formatTime = formatTime

app.mount('#app')
