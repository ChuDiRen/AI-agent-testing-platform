import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import pinia from "@/store/store"

// 公共样式引入
import './assets/style/reset.scss'
import './assets/style/global.scss'

const app = createApp(App)

app.use(router)
app.use(pinia)

app.mount('#app')
