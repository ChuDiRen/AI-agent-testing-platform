<template>
  <div class="not-found flex-center flex-column">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="goHome">返回首页</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.not-found {
  height: 100vh;
  text-align: center;
}

h1 {
  font-size: 72px;
  color: var(--primary-color);
  margin-bottom: 0;
}

p {
  font-size: 24px;
  margin-bottom: 20px;
}
</style>