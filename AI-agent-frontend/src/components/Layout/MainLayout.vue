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
    
    <!-- Token状态显示组件 -->
    <TokenStatus 
      :show-in-dev="true" 
      position="bottom-right" 
      :auto-hide="true" 
      :hide-delay="3000" 
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'
import TokenStatus from '@/components/TokenStatus.vue' // 导入Token状态组件
import { useUserStore, useSystemStore } from '@/store'

const userStore = useUserStore()
const systemStore = useSystemStore()

// 初始化数据（统一到一次性初始化，避免重复请求）
onMounted(async () => {
  if (userStore.token) {
    await userStore.initializeAfterLogin().catch(() => {})
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
  min-width: 0; // 确保内容区域可以正常缩放
  
  &.collapsed {
    margin-left: 64px;
  }
  
  .content-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 0;
    overflow: hidden;
    min-width: 0;
  }
  
  .page-content {
    flex: 1;
    padding: 20px;
    background-color: #f5f7fa;
    overflow-y: auto;
    overflow-x: auto; // 允许横向滚动
    min-width: 0;
    
    // 确保内容区域的滚动条可见
    &::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 4px;
      
      &:hover {
        background: #a8a8a8;
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .main-content {
    .page-content {
      padding: 15px;
    }
  }
}

@media (max-width: 992px) {
  .main-content {
    .page-content {
      padding: 12px;
    }
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;

    &.collapsed {
      margin-left: 0;
    }

    .page-content {
      padding: 10px;
      overflow-x: auto; // 移动端也确保横向滚动
    }
  }
}

@media (max-width: 576px) {
  .main-content {
    .page-content {
      padding: 8px;
    }
  }
}
</style>