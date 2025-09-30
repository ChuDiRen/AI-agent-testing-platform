<template>
  <PageWrapper>
    <NCard title="测试用例管理" :bordered="false" class="page-card">
      <NEmpty description="功能开发中，敬请期待" size="large">
        <template #icon>
          <AppIcon name="mdi:file-document-outline" :size="80" color="#2080f0" />
        </template>
        <template #extra>
          <NSpace vertical>
            <NText depth="3">此功能将支持：</NText>
            <ul class="feature-list">
              <li>测试用例的创建、编辑、删除</li>
              <li>测试用例分类管理</li>
              <li>测试用例执行记录</li>
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

