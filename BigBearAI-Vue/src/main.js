import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

// Import Phosphor Icons
import '@phosphor-icons/web/regular'
import '@phosphor-icons/web/fill'

// Import Custom CSS
import './assets/css/style.css'
import './assets/css/layout.css'
import './assets/css/components.css'
import './assets/css/home.css'

const app = createApp(App)
app.use(router)
app.mount('#app')
