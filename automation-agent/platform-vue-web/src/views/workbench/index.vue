<template>
  <div class="workbench">
    <div class="welcome-section">
      <h1>欢迎使用API测试平台</h1>
      <p>这是一个现代化的API自动化测试管理平台</p>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-title">项目总数</div>
          <div class="stat-value">0</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012 2h2a2 2 0 012-2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-title">用例总数</div>
          <div class="stat-value">0</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-title">执行次数</div>
          <div class="stat-value">0</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-title">成功率</div>
          <div class="stat-value">0%</div>
        </div>
      </div>
    </div>
    
    <div class="quick-actions">
      <h2>快速开始</h2>
      <div class="action-grid">
        <div class="action-card">
          <h3>创建项目</h3>
          <p>创建新的API测试项目</p>
          <button class="action-btn">开始创建</button>
        </div>
        
        <div class="action-card">
          <h3>导入用例</h3>
          <p>从文件导入测试用例</p>
          <button class="action-btn">导入用例</button>
        </div>
        
        <div class="action-card">
          <h3>执行测试</h3>
          <p>运行测试套件</p>
          <button class="action-btn">执行测试</button>
        </div>
        
        <div class="action-card">
          <h3>查看报告</h3>
          <p>查看测试执行报告</p>
          <button class="action-btn">查看报告</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 工作台页面逻辑
</script>

<style scoped>
.workbench {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-section h1 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 10px;
}

.welcome-section p {
  font-size: 1.1rem;
  color: #666;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  background: #f0f9ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1890ff;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #333;
}

.quick-actions {
  margin-bottom: 40px;
}

.quick-actions h2 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 20px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.action-card {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
}

.action-card h3 {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 10px;
}

.action-card p {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.5;
}

.action-btn {
  background: #1890ff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.action-btn:hover {
  background: #40a9ff;
}
</style>
