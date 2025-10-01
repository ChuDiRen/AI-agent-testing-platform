<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-form">
        <div class="login-header">
          <div class="logo">
            <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
              <defs>
                <linearGradient id="loginLogoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                </linearGradient>
              </defs>

              <!-- 背景圆角矩形 -->
              <rect width="64" height="64" rx="16" fill="url(#loginLogoGradient)"/>

              <!-- 机器人图标 -->
              <g transform="translate(12, 12)">
                <!-- 头部 -->
                <rect x="12" y="8" width="16" height="12" rx="2" fill="white" opacity="0.9"/>

                <!-- 眼睛 -->
                <circle cx="16" cy="12" r="1.5" fill="url(#loginLogoGradient)"/>
                <circle cx="24" cy="12" r="1.5" fill="url(#loginLogoGradient)"/>

                <!-- 身体 -->
                <rect x="8" y="20" width="24" height="16" rx="3" fill="white" opacity="0.9"/>

                <!-- 胸部指示灯 -->
                <circle cx="20" cy="26" r="2" fill="url(#loginLogoGradient)"/>
                <circle cx="20" cy="31" r="1" fill="url(#loginLogoGradient)" opacity="0.7"/>

                <!-- 手臂 -->
                <rect x="4" y="22" width="4" height="8" rx="2" fill="white" opacity="0.8"/>
                <rect x="32" y="22" width="4" height="8" rx="2" fill="white" opacity="0.8"/>

                <!-- 腿部 -->
                <rect x="12" y="36" width="4" height="6" rx="2" fill="white" opacity="0.8"/>
                <rect x="24" y="36" width="4" height="6" rx="2" fill="white" opacity="0.8"/>

                <!-- 天线 -->
                <line x1="20" y1="8" x2="20" y2="4" stroke="white" stroke-width="2" stroke-linecap="round" opacity="0.9"/>
                <circle cx="20" cy="4" r="1.5" fill="white" opacity="0.9"/>
              </g>
            </svg>
          </div>
          <h1 class="title">AI Agent Testing Platform</h1>
          <p class="subtitle">基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台</p>
        </div>
        
        <NForm
          ref="formRef"
          :model="formData"
          :rules="rules"
          size="large"
          :show-label="false"
        >
          <NFormItem path="username">
            <NInput
              v-model:value="formData.username"
              placeholder="请输入用户名"
              :input-props="{ autocomplete: 'username' }"
            >
              <template #prefix>
                <Icon name="mdi:account" />
              </template>
            </NInput>
          </NFormItem>
          
          <NFormItem path="password">
            <NInput
              v-model:value="formData.password"
              type="password"
              placeholder="请输入密码"
              show-password-on="mousedown"
              :input-props="{ autocomplete: 'current-password' }"
              @keydown.enter="handleLogin"
            >
              <template #prefix>
                <Icon name="mdi:lock" />
              </template>
            </NInput>
          </NFormItem>
          
          <NFormItem>
            <NButton
              type="primary"
              size="large"
              :loading="loading"
              :block="true"
              @click="handleLogin"
            >
              登录
            </NButton>
          </NFormItem>
        </NForm>
        
        <div class="login-footer">
          <p>默认账号密码：admin / 123456</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Icon } from '@iconify/vue'
import { useUserStore } from '@/store'
import { setToken } from '@/utils'
import api from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)

// 表单数据
const formData = reactive({
  username: 'admin',
  password: '123456',
})

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

// 登录处理
const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true

    const res = await api.login(formData)

    if (res.code === 200) {
      // 保存token
      setToken(res.data.access_token)

      // 获取用户信息
      await userStore.getUserInfo()

      window.$message.success('登录成功')

      // 跳转到目标页面
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      window.$message.error(res.msg || '登录失败')
    }

  } catch (error) {
    console.error('登录失败:', error)
    window.$message.error('登录失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-content {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.login-form {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px auto;
  animation: logoFloat 3s ease-in-out infinite;
}

.logo-svg {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 8px 32px rgba(102, 126, 234, 0.3));
  animation: logoRotate 8s linear infinite;
}

@keyframes logoFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes logoRotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
}

.login-footer p {
  font-size: 12px;
  color: #999;
  margin: 0;
}

:deep(.n-input) {
  height: 48px;
}

:deep(.n-button) {
  height: 48px;
}
</style>
