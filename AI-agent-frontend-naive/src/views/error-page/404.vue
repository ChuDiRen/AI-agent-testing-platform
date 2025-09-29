<template>
  <div class="error-page">
    <div class="error-content">
      <div class="error-image">
        <Icon name="mdi:emoticon-sad-outline" size="120" />
      </div>
      <h1 class="error-title">404</h1>
      <p class="error-description">抱歉，您访问的页面不存在</p>
      <div class="error-actions">
        <NButton type="primary" @click="goHome">
          返回首页
        </NButton>
        <NButton @click="goBack">
          返回上页
        </NButton>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--body-color);
}

.error-content {
  text-align: center;
  max-width: 500px;
  padding: 40px;
}

.error-image {
  margin-bottom: 24px;
  color: var(--text-color-3);
}

.error-title {
  font-size: 72px;
  font-weight: bold;
  color: var(--primary-color);
  margin: 0 0 16px 0;
}

.error-description {
  font-size: 18px;
  color: var(--text-color-2);
  margin: 0 0 32px 0;
}

.error-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}
</style>
