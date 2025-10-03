<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 登录卡片 -->
    <el-card class="login-card">
      <div class="login-header">
        <el-icon class="logo-icon"><BulbFilled /></el-icon>
        <h1 class="title">华测自动化测试平台</h1>
        <p class="subtitle">AI Agent Testing Platform</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            size="large"
            clearable
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="loginForm.rememberMe">记住密码</el-checkbox>
            <el-link type="primary" :underline="false">忘记密码？</el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>

        <el-form-item>
          <div class="register-link">
            还没有账号？
            <el-link type="primary" :underline="false" @click="handleRegister">
              立即注册
            </el-link>
          </div>
        </el-form-item>
      </el-form>

      <!-- 快速登录提示 -->
      <div class="quick-login-tip">
        <el-divider>测试账号</el-divider>
        <div class="test-accounts">
          <el-tag @click="fillTestAccount('admin')">管理员: BNTang / 1234qwer</el-tag>
        </div>
      </div>
    </el-card>

    <!-- 页脚 -->
    <div class="login-footer">
      <p>&copy; 2025 华测自动化测试平台. All rights reserved.</p>
      <p>Powered by Vue 3 + TypeScript + Element Plus</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const loginFormRef = ref<FormInstance>()

// 表单数据
const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

// 加载状态
const loading = ref(false)

// 表单验证规则
const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    const valid = await loginFormRef.value.validate()
    if (!valid) return

    loading.value = true

    const success = await authStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    if (success) {
      // 登录成功，跳转到首页
      router.push('/dashboard')
    }
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}

// 处理注册
const handleRegister = () => {
  ElMessage.info('注册功能开发中...')
}

// 填充测试账号
const fillTestAccount = (type: 'admin') => {
  loginForm.username = 'BNTang'
  loginForm.password = '1234qwer'
  ElMessage.success('已填充测试账号')
}
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  left: -150px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -100px;
  animation-delay: 7s;
}

.circle-3 {
  width: 250px;
  height: 250px;
  bottom: -125px;
  left: 50%;
  animation-delay: 14s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

/* 登录卡片 */
.login-card {
  position: relative;
  width: 100%;
  max-width: 420px;
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.98);
  animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  font-size: 64px;
  color: #667eea;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.title {
  margin: 16px 0 8px;
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

/* 登录表单 */
.login-form {
  margin-top: 32px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.register-link {
  text-align: center;
  width: 100%;
  color: #6b7280;
  font-size: 14px;
}

/* 快速登录提示 */
.quick-login-tip {
  margin-top: 24px;
}

.test-accounts {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.test-accounts :deep(.el-tag) {
  cursor: pointer;
  transition: all 0.3s;
}

.test-accounts :deep(.el-tag:hover) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 页脚 */
.login-footer {
  position: absolute;
  bottom: 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
}

.login-footer p {
  margin: 4px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    max-width: 90%;
    padding: 16px;
  }

  .title {
    font-size: 24px;
  }

  .circle {
    display: none;
  }
}
</style>
