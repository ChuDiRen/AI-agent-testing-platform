<template>
  <div class="modern-header">
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
      <button class="menu-toggle" @click="appStore.toggleCollapse()">
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
          <el-avatar :size="36" :src="circleUrl" class="user-avatar" />
          <div class="user-details">
            <span class="user-name">管理员</span>
            <span class="user-role">Admin</span>
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
import { ElMessageBox } from 'element-plus';
import { reactive, toRefs } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore, useAppStore } from '@/store/modules'

const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

const state = reactive({
  circleUrl:
    'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
  squareUrl:
    'https://cube.elemecdn.com/9/c2/f0ee8a3c7c9638a54940382568c9dpng.png',
  sizeList: ['small', '', 'large'],
})

const { circleUrl, squareUrl, sizeList } = toRefs(state)

// 跳转到个人中心
function goToProfile() {
  router.push('/profile')
}

// 跳转到系统设置
function goToSettings() {
  router.push('/settings')
}

// 退出功能
function handleLogout() {
  showModal("是否要退出登录？", "warning", "").then((res) => {
      // 调用Pinia store的logout方法，清除所有用户数据
      userStore.logout();
      window.location.href = '/login';
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
.modern-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  z-index: var(--z-fixed);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  transition: all var(--transition-base);
}

/* 左侧区域 */
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
  border-right: 1px solid var(--color-border);
}

.logo-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border-radius: var(--radius-md);
  color: white;
}

.logo-icon svg {
  width: 20px;
  height: 20px;
}

.logo-text {
  font-family: var(--font-heading);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
}

.menu-toggle {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.menu-toggle:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

/* 右侧区域 */
.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* 搜索框 */
.search-box {
  position: relative;
  display: flex;
  align-items: center;
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: var(--color-text-muted);
  font-size: 18px;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 1rem 0 2.5rem;
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-full);
  transition: all var(--transition-base);
}

.search-input:focus {
  outline: none;
  background: white;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.search-input::placeholder {
  color: var(--color-text-placeholder);
}

/* 图标按钮 */
.icon-button {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.icon-button:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.notification-badge {
  position: absolute;
  top: 6px;
  right: 6px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
  background: var(--color-error);
  border-radius: var(--radius-full);
  border: 2px solid rgba(255, 255, 255, 0.95);
}

/* 用户菜单 */
.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.user-info:hover {
  background: var(--color-bg-hover);
}

.user-avatar {
  border: 2px solid var(--color-border);
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.user-role {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  line-height: 1.2;
}

.dropdown-arrow {
  color: var(--color-text-muted);
  font-size: 14px;
  transition: transform var(--transition-base);
}

.user-dropdown.is-active .dropdown-arrow {
  transform: rotate(180deg);
}

/* 下拉菜单样式覆盖 */
:deep(.modern-dropdown) {
  min-width: 200px;
  padding: 0.5rem;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
}

:deep(.modern-dropdown .el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

:deep(.modern-dropdown .el-dropdown-menu__item:hover) {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

:deep(.modern-dropdown .el-dropdown-menu__item.is-divided) {
  margin-top: 0.5rem;
  border-top: 1px solid var(--color-border);
  padding-top: 0.75rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-box {
    display: none;
  }
  
  .user-details {
    display: none;
  }
}
</style>