<template>
  <div class="forgot-password-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="forgot-password-wrapper">
      <!-- Left Side - Branding -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-title">AgentFlow</h1>
          <p class="brand-subtitle">AI Agent 编排平台</p>

          <div class="feature-list">
            <div class="feature-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>智能密码重置</span>
            </div>
            <div class="feature-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>安全邮箱验证</span>
            </div>
            <div class="feature-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>快速恢复访问</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Forgot Password Form -->
      <div class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2 class="form-title">重置密码</h2>
            <p class="form-subtitle">输入您的邮箱地址，我们将发送重置链接</p>
          </div>

          <form
            ref="forgotPasswordFormRef"
            class="forgot-password-form"
            @submit.prevent="handleForgotPassword"
          >
            <div class="form-group">
              <label for="email" class="form-label">邮箱地址</label>
              <div class="input-wrapper">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="input-icon">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" stroke-width="2"/>
                  <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2"/>
                </svg>
                <input
                  id="email"
                  v-model="forgotPasswordForm.email"
                  type="email"
                  class="form-input"
                  placeholder="请输入您的邮箱地址"
                  autocomplete="email"
                  required
                  aria-required="true"
                />
              </div>
            </div>

            <button
              type="submit"
              class="btn btn-primary btn-block"
              :disabled="loading"
              aria-busy="loading"
            >
              <span v-if="loading" class="loading-text">
                <svg class="spinner" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-dasharray="60" stroke-dashoffset="30"/>
                </svg>
                发送中...
              </span>
              <span v-else>发送重置链接</span>
            </button>
          </form>

          <div class="form-footer">
            <p class="back-to-login">
              记起密码了？
              <router-link to="/auth/login" class="link">返回登录</router-link>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'ForgotPassword',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const forgotPasswordFormRef = ref(null)

    const forgotPasswordForm = reactive({
      email: ''
    })

    const handleForgotPassword = async () => {
      loading.value = true
      
      try {
        // TODO: 实现忘记密码 API 调用
        ElMessage.success('重置链接已发送到您的邮箱')
        
        // 3秒后跳转到登录页面
        setTimeout(() => {
          router.push('/auth/login')
        }, 3000)
        
      } catch (error) {
        console.error('Forgot password failed:', error)
        ElMessage.error('发送失败，请检查邮箱地址')
      } finally {
        loading.value = false
      }
    }

    return {
      loading,
      forgotPasswordFormRef,
      forgotPasswordForm,
      handleForgotPassword
    }
  }
}
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 80px;
  height: 80px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 120px;
  height: 120px;
  top: 70%;
  right: 10%;
  animation-delay: 2s;
}

.circle-3 {
  width: 60px;
  height: 60px;
  bottom: 20%;
  left: 30%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.forgot-password-wrapper {
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-height: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.brand-section {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  color: white;
}

.brand-content {
  text-align: center;
}

.brand-logo {
  margin-bottom: 30px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  color: white;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 40px;
}

.feature-list {
  text-align: left;
  max-width: 300px;
  margin: 0 auto;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.feature-icon {
  width: 20px;
  height: 20px;
  margin-right: 15px;
  color: #4ade80;
}

.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-card {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 10px;
}

.form-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
}

.form-group {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #374151;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #9ca3af;
}

.form-input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: #f9fafb;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.form-footer {
  text-align: center;
  margin-top: 30px;
}

.back-to-login {
  color: #6b7280;
  font-size: 0.9rem;
}

.link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .forgot-password-wrapper {
    flex-direction: column;
    margin: 20px;
  }
  
  .brand-section {
    padding: 40px 20px;
  }
  
  .form-section {
    padding: 30px 20px;
  }
  
  .brand-title {
    font-size: 2rem;
  }
}
</style>
