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
        class="layout-sider"
      >
        <!-- Logo区域 -->
        <div class="logo" @click="$router.push('/')">
          <div class="logo-icon-wrapper">
            <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
              <defs>
                <linearGradient id="sidebarLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                </linearGradient>
              </defs>

              <!-- 背景圆角矩形 -->
              <rect width="40" height="40" rx="10" fill="url(#sidebarLogoGradient)"/>

              <!-- 机器人图标 -->
              <g transform="translate(8, 8)">
                <!-- 头部 -->
                <rect x="7" y="5" width="10" height="7" rx="1" fill="white" opacity="0.9"/>

                <!-- 眼睛 -->
                <circle cx="10" cy="7.5" r="0.8" fill="url(#sidebarLogoGradient)"/>
                <circle cx="14" cy="7.5" r="0.8" fill="url(#sidebarLogoGradient)"/>

                <!-- 身体 -->
                <rect x="5" y="12" width="14" height="10" rx="2" fill="white" opacity="0.9"/>

                <!-- 胸部指示灯 -->
                <circle cx="12" cy="16" r="1.2" fill="url(#sidebarLogoGradient)"/>
                <circle cx="12" cy="19" r="0.6" fill="url(#sidebarLogoGradient)" opacity="0.7"/>

                <!-- 手臂 -->
                <rect x="2" y="13" width="3" height="5" rx="1.5" fill="white" opacity="0.8"/>
                <rect x="19" y="13" width="3" height="5" rx="1.5" fill="white" opacity="0.8"/>

                <!-- 天线 -->
                <line x1="12" y1="5" x2="12" y2="2" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.9"/>
                <circle cx="12" cy="2" r="1" fill="white" opacity="0.9"/>
              </g>
            </svg>
          </div>
          <span v-show="!collapsed" class="logo-text">AI Agent Platform</span>
        </div>

        <!-- 菜单 -->
        <NMenu
          :collapsed="collapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :options="menuOptions"
          :value="activeKey"
          @update:value="handleMenuSelect"
          class="layout-menu"
        />
      </NLayoutSider>

      <!-- 主内容区 -->
      <NLayout class="layout-main">
        <!-- 头部 -->
        <NLayoutHeader bordered class="header">
          <div class="header-left">
            <!-- 菜单折叠按钮 -->
            <NButton quaternary circle @click="toggleSidebar" class="collapse-btn">
              <template #icon>
                <Icon :name="collapsed ? 'mdi:menu-open' : 'mdi:menu'" />
              </template>
            </NButton>

            <!-- 面包屑 -->
            <AppBreadcrumb class="breadcrumb" />
          </div>

          <div class="header-right">
            <NSpace>
              <!-- 全屏切换 -->
              <NTooltip>
                <template #trigger>
                  <NButton quaternary circle @click="toggleFullscreen">
                    <template #icon>
                      <Icon :name="isFullscreen ? 'mdi:fullscreen-exit' : 'mdi:fullscreen'" />
                    </template>
                  </NButton>
                </template>
                {{ isFullscreen ? '退出全屏' : '全屏' }}
              </NTooltip>

              <!-- 语言切换 -->
              <NTooltip>
                <template #trigger>
                  <NButton quaternary circle @click="toggleLanguage">
                    <template #icon>
                      <Icon name="mdi:translate" />
                    </template>
                  </NButton>
                </template>
                {{ appStore.locale === 'zh-CN' ? '中文' : 'English' }}
              </NTooltip>

              <!-- GitHub链接 -->
              <NTooltip>
                <template #trigger>
                  <NButton quaternary circle @click="openGithub">
                    <template #icon>
                      <Icon name="mdi:github" />
                    </template>
                  </NButton>
                </template>
                GitHub
              </NTooltip>

              <!-- 主题切换 -->
              <NTooltip>
                <template #trigger>
                  <NButton quaternary circle @click="toggleTheme">
                    <template #icon>
                      <Icon :name="isDark ? 'mdi:weather-sunny' : 'mdi:weather-night'" />
                    </template>
                  </NButton>
                </template>
                {{ isDark ? '浅色模式' : '深色模式' }}
              </NTooltip>

              <!-- 用户菜单 -->
              <UserAvatar />
            </NSpace>
          </div>
        </NLayoutHeader>

        <!-- Tags标签页 -->
        <div v-if="tagsStore.tags.length > 0" class="tags-container">
          <AppTags />
        </div>

        <!-- 内容区 -->
        <NLayoutContent class="content">
          <RouterView v-if="appStore.reloadFlag" />
        </NLayoutContent>
      </NLayout>
    </NLayout>
  </div>
</template>

<script setup>
import { computed, ref, watch, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAppStore, usePermissionStore, useTagsStore } from '@/store'
import { Icon } from '@iconify/vue'
import { NIcon } from 'naive-ui'
import AppTags from '@/components/layout/AppTags.vue'
import AppBreadcrumb from '@/components/layout/AppBreadcrumb.vue'
import UserAvatar from '@/components/layout/UserAvatar.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const permissionStore = usePermissionStore()
const tagsStore = useTagsStore()

// 侧边栏折叠状态
const collapsed = ref(appStore.sidebarCollapsed)

// 全屏状态
const isFullscreen = ref(false)

// 主题相关
const isDark = computed(() => appStore.isDark)

// 当前激活的菜单项
const activeKey = computed(() => route.path)

// 渲染图标函数
const renderMenuIcon = (icon) => {
  return () => h(NIcon, null, { default: () => h(Icon, { icon: icon || 'mdi:menu' }) })
}

// 菜单选项
const menuOptions = computed(() => {
  return permissionStore.menus.map(menu => {
    const menuOption = {
      label: menu.meta?.title || menu.name,
      key: menu.path,
      icon: renderMenuIcon(menu.meta?.icon),
    }

    // 如果是直接菜单（如工作台），不显示children，避免下拉箭头
    if (!menu.meta?.isDirect && menu.children) {
      const visibleChildren = menu.children.filter(child => !child.isHidden)
      if (visibleChildren.length > 0) {
        menuOption.children = visibleChildren.map(child => ({
          label: child.meta?.title || child.name,
          key: child.path,
          icon: renderMenuIcon(child.meta?.icon || 'mdi:circle-small'),
        }))
      }
    }

    return menuOption
  })
})





// 切换侧边栏
const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

// 切换主题
const toggleTheme = () => {
  appStore.toggleTheme()
}

// 切换语言
const toggleLanguage = () => {
  appStore.toggleLocale()
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

// 打开GitHub
const openGithub = () => {
  window.open('https://github.com/mizhexiaoxiao/vue-fastapi-admin', '_blank')
}

// 菜单选择
const handleMenuSelect = (key) => {
  router.push(key)
}



// 监听路由变化，添加标签页
watch(
  () => route.path,
  () => {
    if (route.meta?.title && route.path !== '/login') {
      tagsStore.addTag({
        name: route.name,
        path: route.path,
        title: route.meta.title,
        icon: route.meta?.icon,
        closable: route.path !== '/workbench', // 工作台不可关闭
      })
    }
  },
  { immediate: true }
)

// 监听折叠状态变化
watch(collapsed, (val) => {
  appStore.setSidebarCollapsed(val)
})

// 监听全屏状态变化
document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  overflow: hidden;
}

.layout-sider {
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.layout-main {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.logo {
  display: flex;
  align-items: center;
  padding: 16px;
  font-size: 18px;
  font-weight: bold;
  color: var(--primary-color);
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid var(--border-color);
}

.logo:hover {
  background-color: var(--hover-color);
}

.logo-icon-wrapper {
  width: 32px;
  height: 32px;
  margin-right: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.logo-svg {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.logo:hover .logo-icon-wrapper {
  transform: scale(1.1);
  filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.3));
}

.logo:hover .logo-svg {
  transform: rotate(360deg);
}

.logo-text {
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.layout-menu {
  height: calc(100vh - 73px);
  overflow-y: auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 64px;
  background: var(--card-color);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 99;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.header-right {
  flex-shrink: 0;
}

.collapse-btn {
  margin-right: 16px;
}

.breadcrumb {
  margin-left: 8px;
}

.breadcrumb-icon {
  margin-right: 4px;
  font-size: 14px;
}



.tags-container {
  height: 40px;
  border-bottom: 1px solid var(--border-color);
  background: var(--card-color);
  flex-shrink: 0;
}

.content {
  flex: 1;
  padding: 16px;
  background-color: var(--body-color);
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .breadcrumb {
    display: none;
  }

  .header-left .collapse-btn {
    margin-right: 8px;
  }

  .username {
    display: none;
  }
}
</style>
