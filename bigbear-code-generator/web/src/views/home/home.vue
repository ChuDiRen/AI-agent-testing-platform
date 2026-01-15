<template>
  <el-container class="layout-container">
    <el-header class="fixed-header">
      <f-header />
    </el-header>
    
    <el-container class="main-container">
      <el-aside :width="appStore.asideWidth" :class="{ 'mobile-menu': isMobile, 'show': isMobile && menuVisible }">
        <f-menu />
      </el-aside>

      <el-main class="main-content" :style="{ marginLeft: isMobile ? '0' : appStore.asideWidth }">
        <f-tag-list />
        <div class="content-wrapper">
          <f-breadcrumb />
          <router-view v-slot="{ Component }">
            <transition name="fade-slide" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
    
    <!-- 移动端遮罩 -->
    <div v-if="isMobile && menuVisible" class="mobile-overlay" @click="closeMenu"></div>
  </el-container>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useAppStore, useMenuStore } from '~/stores/index.js'
import FHeader from './FHeader.vue'
import FMenu from './FMenu.vue'
import FTagList from './FTagList.vue'
import FBreadcrumb from './FBreadcrumb.vue'

const appStore = useAppStore()
const menuStore = useMenuStore()

// 监听窗口大小变化
const handleResize = () => {
  const width = window.innerWidth
  const height = window.innerHeight
  
  // 更新 store 中的窗口尺寸
  appStore.updateWindowSize(width, height)
  
  // 响应式调整侧边栏宽度
  appStore.adjustAsideWidth()
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  // 初始化窗口尺寸
  appStore.updateWindowSize(window.innerWidth, window.innerHeight)
  
  // 加载用户菜单（如果还没有加载）
  if (!menuStore.menus || menuStore.menus.length === 0) {
    await menuStore.fetchUserMenus()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 使用 store 的响应式状态
const isMobile = computed(() => appStore.isMobile)
const menuVisible = computed(() => {
  if (isMobile.value) {
    return appStore.asideWidth !== '0px'
  }
  return true
})

const closeMenu = () => {
  if (isMobile.value) {
    appStore.handleAsideWidth()
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  background: var(--bg-secondary);
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  padding: 0;
  height: 64px;
}

.main-container {
  margin-top: 64px;
  min-height: calc(100vh - 64px);
}

.el-aside {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: fixed;
  left: 0;
  top: 64px;
  bottom: 0;
  z-index: 100;
}

.main-content {
  background: var(--bg-secondary);
  min-height: calc(100vh - 64px);
  padding: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-x: hidden;
  width: 100%;
  box-sizing: border-box;
}

.content-wrapper {
  padding: 20px;
  overflow-x: hidden;
}

/* 笔记本电脑适配 (1024px-1366px) */
@media (min-width: 769px) and (max-width: 1366px) {
  .content-wrapper {
    padding: 18px 16px;
  }
}

.mobile-overlay {
  position: fixed;
  top: 64px;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 998;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 页面过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 平板适配 */
@media (max-width: 1024px) {
  .content-wrapper {
    padding: 16px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .el-aside {
    left: -250px;
    z-index: 999;
    box-shadow: var(--shadow-xl);
  }
  
  .el-aside.show {
    left: 0;
  }
  
  .main-content {
    margin-left: 0 !important;
    width: 100%;
    overflow-x: hidden;
  }
  
  .content-wrapper {
    padding: 14px 12px;
  }
}

/* 小屏幕手机适配 */
@media (max-width: 480px) {
  .content-wrapper {
    padding: 12px 8px;
  }
}

/* 大屏幕适配 (1920px+) */
@media (min-width: 1920px) {
  .content-wrapper {
    padding: 24px 32px;
  }
}

/* 超大屏幕适配 (2K+) */
@media (min-width: 2560px) {
  .content-wrapper {
    padding: 32px 48px;
  }
}
</style>

