<template>
  <PageWrapper>
    <NCard title="AI生成测试用例" :bordered="false" class="page-card">
      <NEmpty description="功能开发中，敬请期待" size="large">
        <template #icon>
          <AppIcon name="mdi:magic-staff" :size="80" color="#18a058" />
        </template>
        <template #extra>
          <NSpace vertical>
            <NText depth="3">此功能将支持：</NText>
            <ul class="feature-list">
              <li>基于AI的智能测试用例生成</li>
              <li>多种测试场景覆盖</li>
              <li>自动化测试脚本生成</li>
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

