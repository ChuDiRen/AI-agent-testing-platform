<template>
  <div class="f-breadcrumb" :style="breadcrumbStyle">
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index" :to="index === breadcrumbs.length - 1 ? '' : item.path">
        {{ item.title }}
      </el-breadcrumb-item>
    </el-breadcrumb>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '~/stores/index.js'

const route = useRoute()
const appStore = useAppStore()

// 计算面包屑样式 - 响应式调整
const breadcrumbStyle = computed(() => {
  const width = window.innerWidth
  const isMobile = width < 768
  return {
    marginLeft: isMobile ? '0' : appStore.asideWidth,
    transition: 'margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
  }
})

// 根据路由生成面包屑
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  
  return matched.map(item => ({
    title: item.meta.title,
    path: item.path
  }))
})
</script>

<style scoped>
.f-breadcrumb {
  padding: 16px 20px;
  margin-bottom: 16px;
  background: var(--bg-card);
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-breadcrumb__item) {
  font-size: 14px;
}

:deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.3s ease;
}

:deep(.el-breadcrumb__inner:hover) {
  color: var(--primary-color);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
  font-weight: 600;
  cursor: default;
}

:deep(.el-breadcrumb__separator) {
  color: var(--text-disabled);
  margin: 0 8px;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .f-breadcrumb {
    padding: 12px 16px;
    margin-bottom: 12px;
    margin-left: 0 !important;
  }
  
  :deep(.el-breadcrumb__item) {
    font-size: 13px;
  }
  
  :deep(.el-breadcrumb__separator) {
    margin: 0 6px;
  }
}

@media (max-width: 480px) {
  .f-breadcrumb {
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  
  :deep(.el-breadcrumb__item) {
    font-size: 12px;
  }
  
  :deep(.el-breadcrumb__inner) {
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

/* 平板适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .f-breadcrumb {
    padding: 14px 18px;
  }
}
</style>
