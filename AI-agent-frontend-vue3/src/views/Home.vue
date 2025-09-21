<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="home">
    <h1>AI Agent Testing Platform</h1>
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>欢迎使用AI Agent测试平台</span>
        </div>
      </template>
      <div class="card-content">
        <p>这是一个用于测试AI Agent的平台，支持本地API测试环境联调。</p>
        <el-button type="primary" @click="startTest">开始测试</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { ElMessage } from 'element-plus'

const startTest = async () => {
  try {
    // 这里可以调用后端API
    ElMessage.success('测试启动成功！')
  } catch (error) {
    ElMessage.error('测试启动失败，请检查API连接')
    console.error(error)
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}
</style>