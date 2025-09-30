<template>
  <NBreadcrumb class="app-breadcrumb">
    <NBreadcrumbItem 
      v-for="(item, index) in breadcrumbs" 
      :key="item.path"
      :clickable="index < breadcrumbs.length - 1"
      @click="handleBreadcrumbClick(item, index)"
    >
      <div class="breadcrumb-item">
        <Icon 
          v-if="item.icon" 
          :name="item.icon" 
          class="breadcrumb-icon" 
        />
        <span class="breadcrumb-text">{{ item.title }}</span>
      </div>
    </NBreadcrumbItem>
  </NBreadcrumb>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const route = useRoute()
const router = useRouter()

// 面包屑数据
const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  
  // 添加首页
  const items = [
    {
      title: '首页',
      path: '/workbench',
      icon: 'mdi:home',
    }
  ]
  
  // 添加匹配的路由
  matched.forEach(item => {
    if (item.path !== '/' && item.path !== '/workbench') {
      items.push({
        title: item.meta.title,
        path: item.path,
        icon: item.meta?.icon,
      })
    }
  })
  
  return items
})

// 面包屑点击处理
const handleBreadcrumbClick = (item, index) => {
  if (index < breadcrumbs.value.length - 1 && item.path !== route.path) {
    router.push(item.path)
  }
}
</script>

<style scoped>
.app-breadcrumb {
  user-select: none;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.breadcrumb-icon {
  font-size: 14px;
  color: var(--text-color-3);
  transition: color 0.3s ease;
}

.breadcrumb-text {
  font-size: 14px;
  color: var(--text-color-2);
  transition: color 0.3s ease;
}

/* 可点击的面包屑项 */
:deep(.n-breadcrumb-item--clickable) .breadcrumb-item {
  cursor: pointer;
}

:deep(.n-breadcrumb-item--clickable) .breadcrumb-item:hover {
  color: var(--primary-color);
}

:deep(.n-breadcrumb-item--clickable) .breadcrumb-item:hover .breadcrumb-icon {
  color: var(--primary-color);
}

:deep(.n-breadcrumb-item--clickable) .breadcrumb-item:hover .breadcrumb-text {
  color: var(--primary-color);
}

/* 当前页面的面包屑项 */
:deep(.n-breadcrumb-item:last-child) .breadcrumb-text {
  color: var(--text-color-1);
  font-weight: 500;
}

:deep(.n-breadcrumb-item:last-child) .breadcrumb-icon {
  color: var(--primary-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-breadcrumb {
    display: none;
  }
}
</style>
