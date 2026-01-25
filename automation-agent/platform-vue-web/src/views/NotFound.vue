<template>
  <div class="not-found">
    <div class="error-code">404</div>
    <h2>页面未找到</h2>
    <p>抱歉，您访问的页面不存在或已被移除</p>
    
    <div class="action-buttons">
      <router-link to="/workbench" class="home-link">
        <el-icon><House /></el-icon>
        返回工作台
      </router-link>
      <button @click="goBack" class="back-link">
        <el-icon><ArrowLeft /></el-icon>
        返回上页
      </button>
    </div>
    
    <div class="help-text">
      <p>您可以尝试：</p>
      <ul>
        <li>检查URL是否正确</li>
        <li>返回工作台重新导航</li>
        <li>联系系统管理员</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { House, ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  // 如果有历史记录，返回上一页
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    // 否则返回工作台
    router.push('/workbench')
  }
}
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 50px 20px;
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.error-code {
  font-size: clamp(5rem, 20vw, 10rem);
  font-weight: bold;
  color: #ff4d4f;
  margin: 20px 0;
  line-height: 1;
}

h2 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

p {
  color: #606266;
  margin-bottom: 30px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.home-link, .back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background-color: #42b983;
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  text-decoration: none;
  transition: all 0.3s;
  border: none;
  cursor: pointer;
  font-size: 14px;
}

.home-link:hover, .back-link:hover {
  background-color: #359469;
  transform: translateY(-2px);
}

.back-link {
  background-color: #909399;
}

.back-link:hover {
  background-color: #767a82;
}

.help-text {
  text-align: left;
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  max-width: 400px;
  margin-top: 20px;
}

.help-text p {
  margin-bottom: 10px;
  font-weight: 500;
  color: #303133;
}

.help-text ul {
  margin: 0;
  padding-left: 20px;
  color: #606266;
}

.help-text li {
  margin-bottom: 5px;
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .home-link, .back-link {
    width: 200px;
    justify-content: center;
  }
}
</style>
