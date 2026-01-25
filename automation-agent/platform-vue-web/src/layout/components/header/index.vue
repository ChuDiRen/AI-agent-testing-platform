<template>
  <div class="app-header">
    <!-- 左侧区域 -->
    <div class="header-left">
      <!-- Logo 和标题 -->
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="logo-text">API 测试平台</span>
      </div>

      <!-- 菜单折叠按钮 -->
      <button class="menu-toggle" @click="toggleCollapse">
        <el-icon>
          <Fold v-if="!appStore.collapsed"/>
          <Expand v-else/>
        </el-icon>
      </button>
    </div>

    <!-- 右侧区域 -->
    <div class="header-right">
      <!-- 搜索框 -->
      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input type="text" placeholder="搜索功能..." class="search-input" />
      </div>

      <!-- 通知图标 -->
      <button class="icon-button">
        <el-icon><Bell /></el-icon>
        <span class="notification-badge">3</span>
      </button>

      <!-- 用户菜单 -->
      <el-dropdown trigger="click" class="user-dropdown">
        <div class="user-info">
          <el-avatar :size="36" :src="userStore.avatar || defaultAvatar" class="user-avatar" />
          <div class="user-details">
            <span class="user-name">{{ userStore.username || '管理员' }}</span>
            <span class="user-role">{{ userStore.isSuperUser ? 'Admin' : 'User' }}</span>
          </div>
          <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu class="modern-dropdown">
            <el-dropdown-item @click="goToProfile">
              <el-icon><User /></el-icon>
              <span>个人中心</span>
            </el-dropdown-item>
            <el-dropdown-item @click="goToSettings">
              <el-icon><Setting /></el-icon>
              <span>系统设置</span>
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>
              <span>退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store/modules/app'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()

const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const toggleCollapse = () => {
  appStore.toggleCollapse()
}

const goToProfile = () => {
  router.push('/profile')
}

const goToSettings = () => {
  router.push('/system/settings')
}

const handleLogout = () => {
  ElMessageBox.confirm('是否要退出登录？', '', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    userStore.logout()
    window.location.href = '/login'
  })
}
</script>

<style scoped>
.app-header {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-right: 1rem;
  border-right: 1px solid #e5e7eb;
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border-radius: 8px;
  color: white;
}

.logo-icon svg { width: 20px; height: 20px; }
.logo-text { font-size: 1.125rem; font-weight: 600; color: #1f2937; white-space: nowrap; }

.menu-toggle {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  background: transparent; border: none; border-radius: 8px;
  color: #6b7280; cursor: pointer; transition: all 0.2s;
}
.menu-toggle:hover { background: #f3f4f6; color: #2563eb; }

.header-right { display: flex; align-items: center; gap: 1rem; }

.search-box { position: relative; display: flex; align-items: center; width: 300px; }
.search-icon { position: absolute; left: 12px; color: #9ca3af; font-size: 18px; }
.search-input {
  width: 100%; height: 40px; padding: 0 1rem 0 2.5rem;
  font-size: 14px; color: #1f2937; background: #f3f4f6;
  border: 1px solid transparent; border-radius: 20px; transition: all 0.2s;
}
.search-input:focus { outline: none; background: white; border-color: #2563eb; }
.search-input::placeholder { color: #9ca3af; }

.icon-button {
  position: relative; width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  background: transparent; border: none; border-radius: 8px;
  color: #6b7280; cursor: pointer; transition: all 0.2s;
}
.icon-button:hover { background: #f3f4f6; color: #2563eb; }
.notification-badge {
  position: absolute; top: 6px; right: 6px;
  min-width: 18px; height: 18px; padding: 0 4px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; color: white; background: #ef4444;
  border-radius: 50%; border: 2px solid white;
}

.user-dropdown { cursor: pointer; }
.user-info {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.5rem 1rem; border-radius: 8px; transition: all 0.2s;
}
.user-info:hover { background: #f3f4f6; }
.user-avatar { border: 2px solid #e5e7eb; }
.user-details { display: flex; flex-direction: column; align-items: flex-start; }
.user-name { font-size: 14px; font-weight: 600; color: #1f2937; line-height: 1.2; }
.user-role { font-size: 12px; color: #9ca3af; line-height: 1.2; }
.dropdown-arrow { color: #9ca3af; font-size: 14px; transition: transform 0.2s; }
</style>

