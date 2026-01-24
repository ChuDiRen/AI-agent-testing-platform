<template>
  <el-container class="layout-container">
    <!-- 顶部 Header -->
    <el-header class="layout-header">
      <AppHeader />
    </el-header>
    
    <el-container class="layout-body">
      <!-- 侧边栏 -->
      <el-aside :width="sidebarWidth" class="layout-aside">
        <SideBar />
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="layout-main">
        <!-- 标签页 -->
        <AppTags />
        <!-- 路由视图 -->
        <div class="main-content">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <keep-alive :include="keepAliveRoutes">
                <component :is="Component" :key="$route.fullPath" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/store/modules/app'
import { usePermissionStore } from '@/store/modules/permission'
import AppHeader from './components/header/index.vue'
import SideBar from './components/sidebar/index.vue'
import AppTags from './components/tags/index.vue'

const appStore = useAppStore()
const permissionStore = usePermissionStore()

// 侧边栏宽度
const sidebarWidth = computed(() => appStore.collapsed ? '64px' : '250px')

// 需要缓存的路由名称
const keepAliveRoutes = computed(() => {
  return permissionStore.routes
    .filter(route => route.meta?.keepAlive)
    .map(route => route.name)
})
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.layout-header {
  height: 60px;
  padding: 0;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  z-index: 1001;
}

.layout-body {
  flex: 1;
  overflow: hidden;
}

.layout-aside {
  background: #fff;
  border-right: 1px solid #e5e7eb;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.3s;
}

.layout-main {
  padding: 0;
  background: #f5f6fb;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

