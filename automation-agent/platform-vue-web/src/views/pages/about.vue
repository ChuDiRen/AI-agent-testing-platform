<template>
  <div class="about-page">
    <div class="page-header">
      <h1 class="page-title">关于我们</h1>
      <p class="page-subtitle">大熊AI自动化测试平台</p>
    </div>

    <div class="about-content">
      <el-card class="info-card">
        <h2>系统信息</h2>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="系统名称">大熊AI自动化测试</el-descriptions-item>
          <el-descriptions-item label="版本号">1.0.0</el-descriptions-item>
          <el-descriptions-item label="系统描述">专业的接口测试管理解决方案</el-descriptions-item>
          <el-descriptions-item label="开发团队">大熊AI团队</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="info-card">
        <h2>功能特性</h2>
        <ul class="feature-list">
          <li>智能用例管理</li>
          <li>接口自动化测试</li>
          <li>测试报告生成</li>
          <li>权限管理系统</li>
          <li>多环境支持</li>
        </ul>
      </el-card>
    </div>
  </div>
</template>

<script setup>
// 关于页面组件
</script>

<style scoped>
.about-page {
  padding: 2rem;
  background: var(--color-bg-primary, #f5f5f5);
  min-height: calc(100vh - 70px);
}

.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary, #333);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--color-text-muted, #666);
}

.about-content {
  max-width: 1200px;
  margin: 0 auto;
}

.info-card {
  margin-bottom: 2rem;
}

.info-card h2 {
  margin-bottom: 1rem;
  color: var(--color-text-primary, #333);
}

.feature-list {
  list-style: none;
  padding: 0;
}

.feature-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border, #eee);
}

.feature-list li:last-child {
  border-bottom: none;
}
</style>
