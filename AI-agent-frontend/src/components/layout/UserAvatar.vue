<template>
  <NDropdown 
    :options="userMenuOptions" 
    @select="handleUserMenuSelect"
    placement="bottom-end"
  >
    <div class="user-info">
      <NAvatar 
        round 
        size="small" 
        :src="userStore.userInfo?.avatar" 
        :fallback-src="defaultAvatar"
        class="user-avatar"
      />
      <div v-if="!isMobile" class="user-details">
        <span class="username">{{ userStore.userInfo?.username || '用户' }}</span>
        <span class="user-role">{{ userStore.userInfo?.role_name || '普通用户' }}</span>
      </div>
      <Icon name="mdi:chevron-down" class="user-arrow" />
    </div>
  </NDropdown>
</template>

<script setup>
import { computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore, useAppStore } from '@/store'
import { Icon } from '@iconify/vue'

const router = useRouter()
const userStore = useUserStore()
const appStore = useAppStore()

// 默认头像
const defaultAvatar = 'https://avatars.githubusercontent.com/u/54677442?v=4'

// 是否为移动端
const isMobile = computed(() => appStore.isMobile)

// 用户菜单选项
const userMenuOptions = computed(() => [
  {
    label: '个人资料',
    key: 'profile',
    icon: () => h(Icon, { name: 'mdi:account' }),
  },
  {
    label: '账户设置',
    key: 'settings',
    icon: () => h(Icon, { name: 'mdi:cog' }),
  },
  {
    label: '修改密码',
    key: 'password',
    icon: () => h(Icon, { name: 'mdi:lock' }),
  },
  {
    type: 'divider',
  },
  {
    label: '帮助中心',
    key: 'help',
    icon: () => h(Icon, { name: 'mdi:help-circle' }),
  },
  {
    label: '关于系统',
    key: 'about',
    icon: () => h(Icon, { name: 'mdi:information' }),
  },
  {
    type: 'divider',
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: () => h(Icon, { name: 'mdi:logout', style: { color: 'var(--error-color)' } }),
    props: {
      style: {
        color: 'var(--error-color)',
      },
    },
  },
])

// 用户菜单选择处理
const handleUserMenuSelect = (key) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      window.$message?.info('账户设置功能开发中...')
      break
    case 'password':
      window.$message?.info('修改密码功能开发中...')
      break
    case 'help':
      window.$message?.info('帮助中心功能开发中...')
      break
    case 'about':
      window.$dialog?.info({
        title: '关于系统',
        content: `
          AI Agent Testing Platform v1.0.0
          
          基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台
          
          技术栈：
          • 前端：Vue 3 + Naive UI + Vite
          • 后端：FastAPI + SQLAlchemy + Pydantic
          • 数据库：SQLite / PostgreSQL / MySQL
          
          © 2025 左岚团队. All rights reserved.
        `,
        positiveText: '确定',
      })
      break
    case 'logout':
      window.$dialog?.warning({
        title: '确认退出',
        content: '确定要退出登录吗？',
        positiveText: '确定',
        negativeText: '取消',
        onPositiveClick: () => {
          userStore.logout()
          window.$message?.success('已退出登录')
        },
      })
      break
  }
}
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  background: var(--hover-color);
  min-width: 120px;
}

.user-info:hover {
  background-color: var(--primary-color-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-avatar {
  flex-shrink: 0;
  border: 2px solid var(--border-color);
  transition: border-color 0.3s ease;
}

.user-info:hover .user-avatar {
  border-color: var(--primary-color);
}

.user-details {
  display: flex;
  flex-direction: column;
  margin: 0 8px;
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color-1);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: var(--text-color-3);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-arrow {
  font-size: 12px;
  color: var(--text-color-3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.user-info:hover .user-arrow {
  color: var(--primary-color);
  transform: rotate(180deg);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-info {
    min-width: auto;
    padding: 8px;
  }
  
  .user-details {
    display: none;
  }
}
</style>
