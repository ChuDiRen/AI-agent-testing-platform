<template>
  <div class="login-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
      <div class="glow-orb orb-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="login-wrapper">
      <!-- Left Side - Branding -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-logo-wrapper">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-title text-glow">AgentFlow</h1>
          <p class="brand-subtitle">AI 编排的未来</p>

          <div class="feature-list">
            <div class="feature-item glass-panel">
              <div class="feature-icon-box">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="feature-text">
                <h3>自主 Agent</h3>
                <p>部署为您 24/7 工作的智能 Agent</p>
              </div>
            </div>
            <div class="feature-item glass-panel">
              <div class="feature-icon-box">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="feature-text">
                <h3>工作流自动化</h3>
                <p>使用可视化工具构建复杂工作流</p>
              </div>
            </div>
            <div class="feature-item glass-panel">
              <div class="feature-icon-box">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                  <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </div>
              <div class="feature-text">
                <h3>实时监控</h3>
                <p>实时跟踪性能和执行情况</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Login Form -->
      <div class="form-section">
        <div class="form-card glass-card">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">登录以继续您的旅程</p>
          </div>

          <form
            ref="loginFormRef"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <div class="form-group">
              <label for="username" class="form-label">用户名</label>
              <div class="input-wrapper">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="input-icon">
                  <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <input
                  id="username"
                  v-model="loginForm.username"
                  type="text"
                  class="form-input"
                  placeholder="请输入用户名"
                  autocomplete="username"
                  required
                  aria-required="true"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <div class="input-wrapper">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="input-icon">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <input
                  id="password"
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="请输入密码"
                  autocomplete="current-password"
                  required
                  aria-required="true"
                />
                <button
                  type="button"
                  class="toggle-password"
                  @click="showPassword = !showPassword"
                  :aria-label="showPassword ? '隐藏密码' : '显示密码'"
                >
                  <svg
                    v-if="!showPassword"
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    class="eye-icon"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <svg
                    v-else
                    viewBox="0 0 24 24"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    class="eye-icon"
                  >
                    <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="form-options">
              <label class="checkbox-label">
                <input v-model="loginForm.rememberMe" type="checkbox" class="checkbox" />
                <span class="checkbox-text">记住我</span>
              </label>
              <router-link to="/auth/forgot-password" class="forgot-link">
                忘记密码？
              </router-link>
            </div>

            <button
              type="submit"
              class="btn btn-primary-glow btn-block"
              :disabled="loading"
              aria-busy="loading"
            >
              <span v-if="loading" class="loading-text">
                <svg class="spinner" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-dasharray="60" stroke-dashoffset="30"/>
                </svg>
                登录中...
              </span>
              <span v-else>登录</span>
            </button>



            <p class="signup-text">
              还没有账号？
              <router-link to="/auth/register" class="signup-link">立即注册</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

const loading = ref(false)
const showPassword = ref(false)
const loginFormRef = ref(null)

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const success = await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    if (success) {
      ElMessage.success('欢迎回来！')
      router.push('/')
    } else {
      ElMessage.error('用户名或密码错误')
    }
  } catch (error) {
    console.error('登录错误:', error)
    ElMessage.error('登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-primary);
  position: relative;
  overflow: hidden;
}

/* Background Decoration */
.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
}

.glow-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 20s infinite ease-in-out;
}

.orb-1 {
  top: -10%;
  left: -10%;
  width: 50vw;
  height: 50vw;
  background: radial-gradient(circle, var(--color-primary) 0%, transparent 70%);
  animation-delay: 0s;
}

.orb-2 {
  bottom: -10%;
  right: -10%;
  width: 40vw;
  height: 40vw;
  background: radial-gradient(circle, var(--color-accent) 0%, transparent 70%);
  animation-delay: -5s;
}

.orb-3 {
  top: 40%;
  left: 40%;
  width: 30vw;
  height: 30vw;
  background: radial-gradient(circle, var(--color-primary-dark) 0%, transparent 70%);
  animation-delay: -10s;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  25% { transform: translate(5%, 10%); }
  50% { transform: translate(10%, -5%); }
  75% { transform: translate(-5%, -10%); }
}

.login-wrapper {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1200px;
  min-height: 600px;
  margin: var(--space-4);
}

/* Left Side - Branding */
.brand-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: var(--space-8);
  color: white;
}

.brand-content {
  max-width: 480px;
}

.brand-logo-wrapper {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-6);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.3);
}

.logo-icon {
  width: 32px;
  height: 32px;
  color: white;
}

.brand-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: var(--space-2);
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: var(--space-12);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateX(10px);
  background: rgba(255, 255, 255, 0.1);
}

.feature-icon-box {
  width: 40px;
  height: 40px;
  background: rgba(139, 92, 246, 0.2);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a78bfa;
}

.feature-icon {
  width: 20px;
  height: 20px;
}

.feature-text h3 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 2px;
}

.feature-text p {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Right Side - Form */
.form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-4);
}

.form-card {
  width: 100%;
  max-width: 440px;
  padding: var(--space-8);
  background: var(--color-bg-glass-heavy);
  backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-glass);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-2xl);
}

.form-header {
  text-align: center;
  margin-bottom: var(--space-8);
}

.form-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.form-subtitle {
  color: var(--color-text-secondary);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: var(--space-3);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  pointer-events: none;
  z-index: 1;
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-3) var(--space-3) 2.5rem;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
  background: rgba(0, 0, 0, 0.3);
}

.toggle-password {
  position: absolute;
  right: var(--space-3);
  background: none;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-password:hover {
  color: var(--color-text-primary);
}

.eye-icon {
  width: 20px;
  height: 20px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.875rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  color: var(--color-text-secondary);
}

.checkbox {
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}

.forgot-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}

.forgot-link:hover {
  color: var(--color-primary-light);
  text-decoration: underline;
}

.btn-primary-glow {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 0 15px var(--color-primary-glow);
}

.btn-primary-glow:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 25px var(--color-primary-glow);
  background: var(--color-primary-dark);
}

.btn-primary-glow:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.spinner {
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

.divider {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  color: var(--color-text-muted);
  font-size: 0.875rem;
  margin: var(--space-4) 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--color-border-light);
}

.social-login {
  display: flex;
  gap: var(--space-4);
  justify-content: center;
}

.social-btn {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--color-text-secondary);
}

.social-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--color-text-primary);
  color: var(--color-text-primary);
  transform: translateY(-2px);
}

.social-icon {
  width: 24px;
  height: 24px;
}

.signup-text {
  text-align: center;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.signup-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  margin-left: var(--space-1);
}

.signup-link:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 900px) {
  .login-wrapper {
    flex-direction: column;
    margin: 0;
    min-height: 100vh;
  }

  .brand-section {
    padding: var(--space-8) var(--space-6);
    flex: 0 0 auto;
    text-align: center;
  }

  .brand-content {
    max-width: 100%;
  }

  .brand-logo-wrapper {
    margin: 0 auto var(--space-6);
  }

  .feature-list {
    display: none;
  }

  .form-section {
    flex: 1;
    padding: var(--space-6);
    align-items: flex-start;
  }
}
</style>