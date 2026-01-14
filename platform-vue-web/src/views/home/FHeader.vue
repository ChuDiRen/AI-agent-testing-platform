<template>
  <div class="f-header">
    <span class="logo">
      <el-icon class="logo-icon"><Opportunity /></el-icon>
      <span class="logo-text">大熊AI代码生成器</span>
    </span>
    
    <el-icon class="icon-btn" @click="handleAsideWidth">
      <Fold v-if="asideWidth == '250px'"/>
      <Expand v-else/>
    </el-icon>
    
    <div class="ml-auto flex items-center" style="gap: 16px;">
      <!-- 主题切换按钮 -->
      <el-tooltip :content="isDark ? '切换到浅色模式' : '切换到深色模式'" placement="bottom">
        <el-icon class="theme-toggle" @click="toggleTheme" :size="20">
          <Sunny v-if="isDark" />
          <Moon v-else />
        </el-icon>
      </el-tooltip>
      
      <!-- 用户下拉菜单 -->
      <el-dropdown>
        <span class="user-dropdown">
          <el-avatar :size="32" :src="circleUrl" />
          <el-icon class="el-icon--right">
            <arrow-down />
          </el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu class="drop-down">
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import { useRouter } from "vue-router"
import { useAppStore, useUserStore, usePermissionStore } from '~/stores/index.js'
import { getUserInfo } from '~/views/login/login'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const permissionStore = usePermissionStore()
const asideWidth = computed(() => appStore.asideWidth)

const handleAsideWidth = () => {
  appStore.handleAsideWidth()
}

// 从 Pinia store 获取用户头像
const circleUrl = computed(() => {
  return userStore.userInfo?.avatar || ''
})

// 页面加载时获取用户信息
onMounted(async () => {
  // 如果 Pinia store 中没有用户信息，但有 token，则通过 token 重新获取
  const token = localStorage.getItem('token')
  if (!userStore.userInfo && token) {
    try {
      const res = await getUserInfo()
      if (res.data.code === 200) {
        userStore.setUserInfo(res.data.data)
      }
    } catch (error) {
      // 静默处理错误
    }
  }
})

// 主题相关
const isDark = computed(() => appStore.theme === 'dark')

const toggleTheme = () => {
  appStore.toggleTheme()
}

function handleLogout() {
  showModal("是否要退出登录？", "warning", "").then((res) => {
    // 清除动态路由
    permissionStore.clearRoutes()
    
    // 清除用户信息
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    userStore.clearUserInfo()
    
    // 跳转到登录页
    router.push("/login");
  });
}

function showModal(content,type,title){
    return ElMessageBox.confirm(
        content,
        title,
        {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type,
        }
      )
}
</script>
<style scoped>
.f-header {
  display: flex;
  align-items: center;
  background: var(--primary-gradient);
  color: white;
  height: 64px;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 250px;
  white-space: nowrap;
}

.logo:hover {
  transform: scale(1.05);
}

.logo-icon {
  font-size: 28px;
  animation: rotate 20s linear infinite;
  flex-shrink: 0;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.icon-btn {
  margin-left: 24px;
  font-size: 22px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.icon-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.theme-toggle {
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.theme-toggle:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: rotate(180deg);
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.user-dropdown:hover {
  background: rgba(255, 255, 255, 0.2);
}

:deep(.drop-down) {
  width: 150px;
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .logo-text {
    display: none;
  }
  
  .logo {
    min-width: auto;
  }
  
  .f-header {
    padding: 0 16px;
    gap: 12px;
  }
  
  .icon-btn {
    margin-left: 12px;
    padding: 6px;
  }
  
  .theme-toggle,
  .user-dropdown {
    padding: 6px;
  }
}

@media (max-width: 480px) {
  .f-header {
    padding: 0 12px;
    height: 56px;
  }
  
  .logo-icon {
    font-size: 24px;
  }
  
  .icon-btn {
    margin-left: 8px;
    font-size: 20px;
    padding: 5px;
  }
  
  .theme-toggle,
  .user-dropdown {
    padding: 5px;
  }
}
</style>