<template>
  <aside class="sidebar glass-panel" :class="{ 'sidebar-collapsed': collapsed }">
    <!-- Logo -->
    <div class="sidebar-header">
      <div class="logo">
        <div class="logo-icon-wrapper">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span v-if="!collapsed" class="logo-text text-glow">AgentFlow</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li v-for="item in navItems" :key="item.path" class="nav-item">
          <router-link
            :to="item.path"
            class="nav-link"
            :class="{ 'nav-link-active': isActive(item.path) }"
            :aria-label="item.label"
          >
            <div class="nav-icon-wrapper">
              <component :is="item.icon" class="nav-icon" />
            </div>
            <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
            <div v-if="isActive(item.path)" class="active-indicator"></div>
          </router-link>
        </li>
      </ul>
    </nav>

    <!-- User Menu -->
    <div class="sidebar-footer">
      <div class="user-menu glass-card">
        <div class="user-avatar">
          <img src="https://ui-avatars.com/api/?name=Admin+User&background=8b5cf6&color=fff" alt="User" />
        </div>
        <div v-if="!collapsed" class="user-info">
          <div class="user-name">{{ userName }}</div>
          <button class="logout-btn" @click="handleLogout" aria-label="退出登录">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="logout-icon">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M16 17l5-5-5-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M21 12H9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'

const props = defineProps({
  collapsed: {
    type: Boolean,
    default: false
  }
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const userName = computed(() => {
  return localStorage.getItem('userName') || 'Admin User'
})

const navItems = [
  {
    path: '/agents',
    label: '智能代理',
    icon: 'AgentIcon'
  },
  {
    path: '/workflows',
    label: '工作流',
    icon: 'WorkflowIcon'
  },
  {
    path: '/tools',
    label: '工具管理',
    icon: 'ToolIcon'
  },
  {
    path: '/monitoring',
    label: '执行监控',
    icon: 'MonitorIcon'
  },
  {
    path: '/billing',
    label: '计费统计',
    icon: 'BillingIcon'
  }
]

function isActive(path) {
  return route.path.startsWith(path)
}

function handleLogout() {
  authStore.logout()
  ElMessage.success('退出登录成功')
  router.push('/auth/login')
}
</script>

<script>
const AgentIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>
  `
}

const WorkflowIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const ToolIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const MonitorIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `
}

const BillingIcon = {
  template: `
    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="5" width="20" height="14" rx="2" stroke="currentColor" stroke-width="2"/>
      <path d="M2 10h20" stroke="currentColor" stroke-width="2"/>
    </svg>
  `
}

export default {
  components: {
    AgentIcon,
    WorkflowIcon,
    ToolIcon,
    MonitorIcon,
    BillingIcon
  }
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 16px;
  left: 16px;
  bottom: 16px;
  width: 260px;
  background: var(--color-bg-glass-heavy);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-xl);
  display: flex;
  flex-direction: column;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}

.sidebar-collapsed {
  width: 80px;
}

.sidebar-header {
  padding: var(--space-6) var(--space-4);
  display: flex;
  justify-content: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--color-primary);
  text-decoration: none;
}

.logo-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(139, 92, 246, 0.1);
  border-radius: var(--radius-lg);
  color: var(--color-primary);
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.2);
}

.logo-icon {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--color-text-primary);
  white-space: nowrap;
  opacity: 1;
  transition: opacity 0.3s;
}

.sidebar-collapsed .logo-text {
  display: none;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-4) var(--space-2);
  overflow-y: auto;
}

.nav-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  color: var(--color-text-secondary);
  text-decoration: none;
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
  overflow: hidden;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--color-text-primary);
}

.nav-link-active {
  background: rgba(139, 92, 246, 0.1) !important;
  color: var(--color-primary) !important;
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.1);
}

.nav-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.nav-icon {
  width: 24px;
  height: 24px;
  transition: transform 0.2s ease;
}

.nav-link:hover .nav-icon {
  transform: scale(1.1);
}

.nav-label {
  font-weight: 500;
  white-space: nowrap;
}

.active-indicator {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-primary);
  border-radius: 0 4px 4px 0;
  box-shadow: 0 0 10px var(--color-primary);
}

.sidebar-footer {
  padding: var(--space-4);
}

.user-menu {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease;
}

.user-avatar img {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: 2px solid var(--color-border-glass);
}

.user-info {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  overflow: hidden;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-sm);
  transition: color 0.2s;
}

.logout-btn:hover {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}

.logout-icon {
  width: 18px;
  height: 18px;
}

/* Scrollbar for nav */
.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}
.sidebar-nav::-webkit-scrollbar-thumb {
  background: transparent;
}
.sidebar-nav:hover::-webkit-scrollbar-thumb {
  background: var(--color-border-glass);
}
</style>
