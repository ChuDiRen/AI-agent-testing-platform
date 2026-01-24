<template>
  <div class="dashboard-container">
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎使用 API 测试平台</h1>
      <p class="welcome-subtitle">高效、可靠的接口自动化测试解决方案</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Document /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">128</span>
          <span class="stat-label">测试用例</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success"><el-icon><CircleCheck /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">96%</span>
          <span class="stat-label">通过率</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning"><el-icon><Timer /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">45</span>
          <span class="stat-label">今日执行</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon error"><el-icon><Warning /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">3</span>
          <span class="stat-label">失败用例</span>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h3 class="section-title">快速操作</h3>
      <div class="action-grid">
        <el-button type="primary" size="large" @click="$router.push('/testcase')">
          <el-icon><Plus /></el-icon> 新建测试
        </el-button>
        <el-button size="large" @click="$router.push('/report')">
          <el-icon><DataAnalysis /></el-icon> 查看报告
        </el-button>
        <el-button size="large" @click="$router.push('/environment')">
          <el-icon><Setting /></el-icon> 环境配置
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Dashboard组件
</script>

<style scoped>
.dashboard-container { padding: 24px; }
.welcome-section { text-align: center; margin-bottom: 32px; }
.welcome-title { font-size: 28px; font-weight: 600; color: #1f2937; margin-bottom: 8px; }
.welcome-subtitle { font-size: 16px; color: #6b7280; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  background: #dbeafe;
  color: #2563eb;
  font-size: 24px;
}
.stat-icon.success { background: #dcfce7; color: #16a34a; }
.stat-icon.warning { background: #fef3c7; color: #d97706; }
.stat-icon.error { background: #fee2e2; color: #dc2626; }

.stat-value { display: block; font-size: 28px; font-weight: 700; color: #1f2937; }
.stat-label { font-size: 14px; color: #6b7280; }

.section-title { font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 16px; }
.action-grid { display: flex; gap: 12px; flex-wrap: wrap; }
</style>

