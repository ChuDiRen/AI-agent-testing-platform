<template>
  <PageWrapper>
    <NCard title="AI代理列表" :bordered="false" class="page-card">
      <NEmpty description="功能开发中，敬请期待" size="large">
        <template #icon>
          <AppIcon name="mdi:format-list-bulleted" :size="80" color="#18a058" />
        </template>
        <template #extra>
          <NSpace vertical>
            <NText depth="3">此功能将支持：</NText>
            <ul class="feature-list">
              <li>AI代理的创建和管理</li>
              <li>代理状态监控</li>
              <li>代理性能分析</li>
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

