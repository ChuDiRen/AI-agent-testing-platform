<template>
  <PageWrapper title="一级菜单" icon="mdi:menu">
    <NCard>
      <div class="top-menu-content">
        <NResult
          status="info"
          title="一级菜单页面"
          description="这是一个顶级菜单页面示例，用于展示单独的一级菜单功能。"
        >
          <template #footer>
            <NSpace justify="center">
              <NButton type="primary" @click="handleAction">
                <template #icon>
                  <Icon name="mdi:rocket-launch" />
                </template>
                开始使用
              </NButton>
              <NButton @click="handleInfo">
                <template #icon>
                  <Icon name="mdi:information" />
                </template>
                了解更多
              </NButton>
            </NSpace>
          </template>
        </NResult>

        <NDivider />

        <div class="feature-grid">
          <NCard
            v-for="feature in features"
            :key="feature.id"
            hoverable
            class="feature-card"
          >
            <div class="feature-content">
              <div class="feature-icon">
                <Icon :name="feature.icon" :size="32" />
              </div>
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
              <NButton text type="primary" @click="handleFeatureClick(feature)">
                了解详情 →
              </NButton>
            </div>
          </NCard>
        </div>
      </div>
    </NCard>
  </PageWrapper>
</template>

<script setup>
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import { PageWrapper } from '@/components'

defineOptions({ name: '一级菜单' })

// 功能特性数据
const features = ref([
  {
    id: 1,
    title: '用户管理',
    description: '完整的用户管理功能，包括用户增删改查、角色分配等。',
    icon: 'mdi:account-group',
  },
  {
    id: 2,
    title: '权限控制',
    description: '基于RBAC的权限管理系统，支持细粒度的权限控制。',
    icon: 'mdi:shield-account',
  },
  {
    id: 3,
    title: '系统监控',
    description: '实时监控系统状态，提供详细的日志和统计信息。',
    icon: 'mdi:monitor-dashboard',
  },
  {
    id: 4,
    title: '数据分析',
    description: '强大的数据分析功能，帮助您更好地了解业务情况。',
    icon: 'mdi:chart-line',
  },
])

// 处理操作
const handleAction = () => {
  window.$message?.success('欢迎使用系统！')
}

const handleInfo = () => {
  window.$message?.info('这是一个基于Vue 3 + Naive UI的管理系统')
}

const handleFeatureClick = (feature) => {
  window.$message?.info(`点击了功能：${feature.title}`)
}
</script>

<style scoped>
.top-menu-content {
  padding: 20px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.feature-card {
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-2px);
}

.feature-content {
  text-align: center;
  padding: 20px;
}

.feature-icon {
  margin-bottom: 16px;
  color: var(--primary-color);
}

.feature-content h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-1);
}

.feature-content p {
  margin: 0 0 16px 0;
  color: var(--text-color-2);
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .top-menu-content {
    padding: 16px;
  }
}
</style>
