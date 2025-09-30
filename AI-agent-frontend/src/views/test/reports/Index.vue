<template>
  <PageWrapper>
    <NCard title="测试报告" :bordered="false" class="page-card">
      <NEmpty description="功能开发中，敬请期待" size="large">
        <template #icon>
          <AppIcon name="mdi:chart-pie" :size="80" color="#f0a020" />
        </template>
        <template #extra>
          <NSpace vertical>
            <NText depth="3">此功能将支持：</NText>
            <ul class="feature-list">
              <li>测试结果统计分析</li>
              <li>测试覆盖率报告</li>
              <li>测试趋势图表展示</li>
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

