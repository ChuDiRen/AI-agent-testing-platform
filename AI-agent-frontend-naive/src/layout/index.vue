<template>
  <div class="layout-container">
    <NLayout has-sider>
      <!-- 侧边栏 -->
      <NLayoutSider
        bordered
        collapse-mode="width"
        :collapsed-width="64"
        :width="240"
        :collapsed="collapsed"
        show-trigger
        @collapse="collapsed = true"
        @expand="collapsed = false"
      >
        <div class="logo">
          <img src="/favicon.ico" alt="logo" />
          <span v-show="!collapsed">AI Agent Platform</span>
        </div>
        <NMenu
          :collapsed="collapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :options="menuOptions"
          :value="activeKey"
          @update:value="handleMenuSelect"
        />
      </NLayoutSider>
      
      <!-- 主内容区 -->
      <NLayout>
        <!-- 头部 -->
        <NLayoutHeader bordered class="header">
          <div class="header-left">
            <NBreadcrumb>
              <NBreadcrumbItem v-for="item in breadcrumbs" :key="item.path">
                {{ item.title }}
              </NBreadcrumbItem>
            </NBreadcrumb>
          </div>
          <div class="header-right">
            <NSpace>
              <!-- 主题切换 -->
              <NButton quaternary circle @click="toggleTheme">
                <template #icon>
                  <Icon :name="isDark ? 'mdi:weather-sunny' : 'mdi:weather-night'" />
                </template>
              </NButton>
              
              <!-- 用户菜单 -->
              <NDropdown :options="userMenuOptions" @select="handleUserMenuSelect">
                <div class="user-info">
                  <NAvatar round size="small" :src="userStore.avatar" />
                  <span class="username">{{ userStore.name }}</span>
                </div>
              </NDropdown>
            </NSpace>
          </div>
        </NLayoutHeader>
        
        <!-- 内容区 -->
        <NLayoutContent class="content">
          <RouterView v-if="appStore.reloadFlag" />
        </NLayoutContent>
      </NLayout>
    </NLayout>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore, useUserStore, usePermissionStore } from '@/store'
import { Icon } from '@iconify/vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

// 侧边栏折叠状态
const collapsed = ref(appStore.sidebarCollapsed)

// 主题相关
const isDark = computed(() => appStore.isDark)

// 当前激活的菜单项
const activeKey = computed(() => route.path)

// 菜单选项
const menuOptions = computed(() => {
  return permissionStore.menus.map(menu => ({
    label: menu.meta?.title || menu.name,
    key: menu.path,
    icon: () => h(Icon, { name: menu.meta?.icon || 'mdi:menu' }),
    children: menu.children?.filter(child => !child.isHidden).map(child => ({
      label: child.meta?.title || child.name,
      key: child.path,
      icon: () => h(Icon, { name: child.meta?.icon || 'mdi:circle-small' }),
    })),
  }))
})

// 面包屑
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    title: item.meta.title,
    path: item.path,
  }))
})

// 用户菜单选项
const userMenuOptions = [
  {
    label: '个人资料',
    key: 'profile',
    icon: () => h(Icon, { name: 'mdi:account' }),
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
    label: '退出登录',
    key: 'logout',
    icon: () => h(Icon, { name: 'mdi:logout' }),
  },
]

// 切换主题
const toggleTheme = () => {
  appStore.toggleTheme()
}

// 菜单选择
const handleMenuSelect = (key) => {
  router.push(key)
}

// 用户菜单选择
const handleUserMenuSelect = (key) => {
  switch (key) {
    case 'profile':
      router.push('/profile')
      break
    case 'password':
      // 打开修改密码对话框
      break
    case 'logout':
      userStore.logout()
      break
  }
}

// 监听折叠状态变化
watch(collapsed, (val) => {
  appStore.setSidebarCollapsed(val)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.logo {
  display: flex;
  align-items: center;
  padding: 16px;
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 64px;
}

.header-left {
  flex: 1;
}

.header-right {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: var(--hover-color);
}

.username {
  margin-left: 8px;
  font-size: 14px;
}

.content {
  padding: 16px;
  background-color: var(--body-color);
}
</style>
