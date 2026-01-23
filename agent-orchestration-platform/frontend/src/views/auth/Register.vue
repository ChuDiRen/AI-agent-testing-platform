<template>
  <div class="register-container">
    <!-- Background Decoration -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="register-wrapper">
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
          <h1 class="brand-title">加入 AgentFlow</h1>
          <p class="brand-subtitle">今天开始构建智能 AI 工作流</p>

          <div class="feature-list">
            <div class="feature-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>提供免费版本</span>
            </div>
            <div class="feature-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>无需信用卡</span>
            </div>
            <div class="feature-item">
              <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="feature-icon">
                <path d="M5 13l4 4L19 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>即时访问</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Register Form -->
      <div class="form-section">
        <div class="form-card">
          <div class="form-header">
            <h2 class="form-title">创建账户</h2>
            <p class="form-subtitle">注册新账户开始使用</p>
          </div>

          <form
            ref="registerFormRef"
            class="register-form"
            @submit.prevent="handleRegister"
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
                  v-model="registerForm.username"
                  type="text"
                  class="form-input"
                  :class="{ 'input-error': errors.username }"
                  placeholder="输入用户名"
                  autocomplete="username"
                  required
                  aria-required="true"
                  aria-invalid="!!errors.username"
                  :aria-describedby="errors.username ? 'username-error' : undefined"
                />
              </div>
              <span v-if="errors.username" id="username-error" class="error-message">
                {{ errors.username }}
              </span>
            </div>

            <div class="form-group">
              <label for="email" class="form-label">邮箱</label>
              <div class="input-wrapper">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="input-icon">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M22 6l-10 7L2 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <input
                  id="email"
                  v-model="registerForm.email"
                  type="email"
                  class="form-input"
                  :class="{ 'input-error': errors.email }"
                  placeholder="输入邮箱"
                  autocomplete="email"
                  aria-invalid="!!errors.email"
                  :aria-describedby="errors.email ? 'email-error' : undefined"
                />
              </div>
              <span v-if="errors.email" id="email-error" class="error-message">
                {{ errors.email }}
              </span>
            </div>

            <div class="form-group">
              <label for="fullName" class="form-label">全名</label>
              <div class="input-wrapper">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="input-icon">
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                </svg>
                <input
                  id="fullName"
                  v-model="registerForm.full_name"
                  type="text"
                  class="form-input"
                  placeholder="输入全名"
                  autocomplete="name"
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
                  v-model="registerForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  :class="{ 'input-error': errors.password }"
                  placeholder="输入密码"
                  autocomplete="new-password"
                  required
                  aria-required="true"
                  aria-invalid="!!errors.password"
                  :aria-describedby="errors.password ? 'password-error' : undefined"
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
              <span v-if="errors.password" id="password-error" class="error-message">
                {{ errors.password }}
              </span>
              <!-- Password Strength Indicator -->
              <div class="password-strength">
                <div class="strength-bar">
                  <div
                    class="strength-fill"
                    :class="passwordStrengthClass"
                    :style="{ width: passwordStrength + '%' }"
                  ></div>
                </div>
                <span class="strength-text">{{ passwordStrengthText }}</span>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认密码</label>
              <div class="input-wrapper">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="input-icon">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
                <input
                  id="confirmPassword"
                  v-model="registerForm.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-input"
                  :class="{ 'input-error': errors.confirmPassword }"
                  placeholder="确认密码"
                  autocomplete="new-password"
                  required
                  aria-required="true"
                  aria-invalid="!!errors.confirmPassword"
                  :aria-describedby="errors.confirmPassword ? 'confirmPassword-error' : undefined"
                />
                <button
                  type="button"
                  class="toggle-password"
                  @click="showConfirmPassword = !showConfirmPassword"
                  :aria-label="showConfirmPassword ? '隐藏密码' : '显示密码'"
                >
                  <svg
                    v-if="!showConfirmPassword"
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
              <span v-if="errors.confirmPassword" id="confirmPassword-error" class="error-message">
                {{ errors.confirmPassword }}
              </span>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="registerForm.terms" type="checkbox" class="checkbox" required />
                <span class="checkbox-text">我同意服务条款</span>
              </label>
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
                注册中...
              </span>
              <span v-else>注册</span>
            </button>

            <p class="signup-text">
              已有账号？
              <router-link to="/auth/login" class="signup-link">立即登录</router-link>
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api'

const router = useRouter()

const registerForm = reactive({
  username: '',
  email: '',
  full_name: '',
  password: '',
  confirmPassword: '',
  terms: false
})

const errors = ref({})
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const registerFormRef = ref(null)

// Password strength calculation
const passwordStrength = computed(() => {
  const password = registerForm.password
  if (!password) return 0

  let strength = 0
  if (password.length >= 6) strength += 20
  if (password.length >= 10) strength += 20
  if (/[A-Z]/.test(password)) strength += 20
  if (/[a-z]/.test(password)) strength += 20
  if (/[0-9]/.test(password)) strength += 20

  return Math.min(strength, 100)
})

const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength < 40) return 'strength-weak'
  if (strength < 70) return 'strength-medium'
  return 'strength-strong'
})

const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength < 40) return '弱'
  if (strength < 70) return '中'
  return '强'
})

// Real-time validation
watch(() => registerForm.password, () => {
  validateForm()
})

watch(() => registerForm.confirmPassword, () => {
  validateForm()
})

function validateForm() {
  const newErrors = {}

  if (!registerForm.username) {
    newErrors.username = '请输入用户名'
  } else if (registerForm.username.length < 3) {
    newErrors.username = '用户名至少需要3个字符'
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!registerForm.email) {
    newErrors.email = '请输入邮箱地址'
  } else if (!emailRegex.test(registerForm.email)) {
    newErrors.email = '请输入有效的邮箱地址'
  }

  if (!registerForm.password) {
    newErrors.password = '请输入密码'
  } else if (registerForm.password.length < 8) {
    newErrors.password = '密码至少需要8个字符'
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    newErrors.confirmPassword = '两次输入的密码不一致'
  }

  errors.value = newErrors
  return Object.keys(newErrors).length === 0
}

async function handleRegister() {
  if (!registerForm.terms) {
    ElMessage.warning('请同意服务条款')
    return
  }

  if (!validateForm()) return

  try {
    loading.value = true
    const response = await register({
      username: registerForm.username,
      email: registerForm.email,
      full_name: registerForm.full_name,
      password: registerForm.password
    })

    if (response.code === 200) {
      ElMessage.success('注册成功！正在跳转登录...')
      setTimeout(() => {
        router.push('/auth/login')
      }, 1500)
    } else {
      ElMessage.error(response.message || '注册失败')
    }
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error('注册失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-tertiary) 100%);
  position: relative;
  overflow: hidden;
  padding: var(--space-4);
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  filter: blur(80px);
}

.circle-1 {
  width: 400px;
  height: 400px;
  background: var(--color-primary);
  top: -200px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.circle-2 {
  width: 300px;
  height: 300px;
  background: var(--color-accent);
  bottom: -150px;
  left: -100px;
  animation: float 10s ease-in-out infinite reverse;
}

.circle-3 {
  width: 250px;
  height: 250px;
  background: var(--color-primary-light);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float 12s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

.register-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-8);
  width: 100%;
  max-width: 1200px;
  position: relative;
  z-index: 1;
}

@media (min-width: var(--breakpoint-lg)) {
  .register-wrapper {
    grid-template-columns: 1fr 1fr;
  }
}

/* Brand Section */
.brand-section {
  display: none;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
}

@media (min-width: var(--breakpoint-lg)) {
  .brand-section {
    display: flex;
  }
}

.brand-content {
  color: var(--color-text-primary);
}

.brand-logo {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-xl);
}

.logo-icon {
  width: 48px;
  height: 48px;
}

.brand-title {
  font-size: var(--text-5xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-2);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: var(--text-lg);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-8);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-base);
  color: var(--color-text-secondary);
}

.feature-icon {
  width: 20px;
  height: 20px;
  color: var(--color-success);
  flex-shrink: 0;
}

/* Form Section */
.form-section {
  display: flex;
  justify-content: center;
  align-items: center;
}

.form-card {
  width: 100%;
  max-width: 500px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-2xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--color-border-light);
}

.form-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.form-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.form-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
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
}

.form-input {
  width: 100%;
  padding: var(--space-3) var(--space-4) var(--space-3) 3rem;
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all 0.2s ease-out;
}

.form-input::placeholder {
  color: var(--color-text-disabled);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.form-input.input-error {
  border-color: var(--color-error);
}

.form-input.input-error:focus {
  box-shadow: 0 0 0 3px var(--color-error-100);
}

.error-message {
  font-size: var(--text-xs);
  color: var(--color-error);
  margin-top: var(--space-1);
}

.toggle-password {
  position: absolute;
  right: var(--space-3);
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  transition: all 0.2s ease-out;
}

.toggle-password:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-primary);
}

.eye-icon {
  width: 20px;
  height: 20px;
}

/* Password Strength */
.password-strength {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.strength-bar {
  flex: 1;
  height: 4px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: all 0.3s ease-out;
}

.strength-fill.strength-weak {
  background: var(--color-error);
}

.strength-fill.strength-medium {
  background: var(--color-warning);
}

.strength-fill.strength-strong {
  background: var(--color-success);
}

.strength-text {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-secondary);
}

/* Checkbox */
.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  cursor: pointer;
  user-select: none;
  line-height: 1.5;
}

.checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  accent-color: var(--color-primary);
  cursor: pointer;
  margin-top: 2px;
  flex-shrink: 0;
}

.checkbox-text {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-semibold);
  transition: color 0.2s ease-out;
}

.link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

.btn-block {
  width: 100%;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.spinner {
  width: 20px;
  height: 20px;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-text {
  text-align: center;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.login-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-semibold);
  transition: color 0.2s ease-out;
}

.login-link:hover {
  color: var(--color-primary-dark);
  text-decoration: underline;
}

/* Responsive */
@media (max-width: var(--breakpoint-sm)) {
  .form-card {
    padding: var(--space-6);
  }

  .form-title {
    font-size: var(--text-2xl);
  }

  .brand-title {
    font-size: var(--text-3xl);
  }
}
</style>
