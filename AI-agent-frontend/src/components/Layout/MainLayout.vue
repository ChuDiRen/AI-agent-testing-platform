<template>
  <div class="main-layout">
    <!-- 顶部导航 -->
    <AppHeader />
    
    <!-- 主体内容区 -->
    <div class="layout-container">
      <!-- 侧边栏 -->
      <AppSidebar />
      
      <!-- 内容区域 -->
      <div class="main-content" :class="{ 'collapsed': systemStore.collapsed }">
        <div class="content-wrapper">
          <!-- 面包屑导航 -->
          <AppBreadcrumb />
          
          <!-- 页面内容 -->
          <div class="page-content">
            <router-view />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'
import { useUserStore, useSystemStore } from '@/store'

const userStore = useUserStore()
const systemStore = useSystemStore()

// 初始化数据
onMounted(async () => {
  // 如果用户已登录，获取用户信息和权限
  if (userStore.token) {
    await userStore.getUserInfo()
    await userStore.getUserPermissions()
    await userStore.getUserMenus()
  }
})
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 250px;
  transition: margin-left 0.3s ease;
  
  &.collapsed {
    margin-left: 64px;
  }
  
  .content-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow: hidden;
  }
  
  .page-content {
    flex: 1;
    padding: 20px;
    background-color: #f5f7fa;
    overflow-y: auto;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    
    &.collapsed {
      margin-left: 0;
    }
  }
}
</style>