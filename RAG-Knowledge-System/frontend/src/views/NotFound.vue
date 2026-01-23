<template>
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <div class="error-message">页面未找到</div>
      <div class="error-description">
        抱歉，您访问的页面不存在或已被移除
      </div>
      
      <div class="actions">
        <el-button type="primary" @click="goHome">
          <el-icon><House /></el-icon>
          返回首页
        </el-button>
        <el-button @click="goBack">
          <el-icon><ArrowLeft /></el-icon>
          返回上页
        </el-button>
      </div>
      
      <div class="help-links">
        <h4>您可能在寻找：</h4>
        <div class="links">
          <router-link to="/chat" class="link-item">
            <el-icon><ChatDotRound /></el-icon>
            智能问答
          </router-link>
          <router-link v-if="authStore.isAdmin" to="/admin/dashboard" class="link-item">
            <el-icon><Monitor /></el-icon>
            管理后台
          </router-link>
          <router-link to="/profile" class="link-item">
            <el-icon><User /></el-icon>
            个人信息
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="illustration">
      <el-icon size="200" color="#e4e7ed">
        <DocumentDelete />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import { House, ArrowLeft, ChatDotRound, Monitor, User, DocumentDelete } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const goHome = () => {
  if (authStore.isAdmin) {
    router.push('/admin/dashboard')
  } else {
    router.push('/chat')
  }
}

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goHome()
  }
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f5f5;
  padding: 20px;
  gap: 60px;
}

.not-found-content {
  text-align: center;
  max-width: 500px;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
  margin-bottom: 20px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-message {
  font-size: 32px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.error-description {
  font-size: 16px;
  color: #606266;
  margin-bottom: 40px;
  line-height: 1.6;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 60px;
}

.help-links h4 {
  color: #303133;
  margin-bottom: 20px;
  font-size: 18px;
}

.links {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
  color: #606266;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.link-item:hover {
  background: #409eff;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
}

.illustration {
  opacity: 0.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .not-found-container {
    flex-direction: column;
    gap: 40px;
    text-align: center;
  }
  
  .error-code {
    font-size: 80px;
  }
  
  .error-message {
    font-size: 24px;
  }
  
  .error-description {
    font-size: 14px;
  }
  
  .actions {
    flex-direction: column;
    align-items: center;
  }
  
  .actions .el-button {
    width: 200px;
  }
  
  .illustration {
    order: -1;
  }
  
  .illustration .el-icon {
    font-size: 120px !important;
  }
}

@media (max-width: 480px) {
  .not-found-container {
    padding: 16px;
  }
  
  .error-code {
    font-size: 60px;
  }
  
  .error-message {
    font-size: 20px;
  }
  
  .actions .el-button {
    width: 100%;
  }
}
</style>
