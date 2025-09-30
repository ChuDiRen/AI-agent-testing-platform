<template>
  <PageWrapper>
    <NCard title="AI模型配置" :bordered="false" class="page-card">
      <NEmpty description="功能开发中，敬请期待" size="large">
        <template #icon>
          <AppIcon name="mdi:cog-outline" :size="80" color="#d03050" />
        </template>
        <template #extra>
          <NSpace vertical>
            <NText depth="3">此功能将支持：</NText>
            <ul class="feature-list">
              <li>AI模型参数配置</li>
              <li>模型版本管理</li>
              <li>模型性能监控</li>
            </ul>
          </NSpace>
        </template>
      </NEmpty>
    </NCard>
  </PageWrapper>
</template>

<script setup>
import { AppIcon } from '@/components'
</script>

<style scoped>
.page-card {
  min-height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.feature-list {
  list-style: disc;
  padding-left: 20px;
  text-align: left;
}
</style>

