<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-form">
        <div class="login-header">
          <img src="/favicon.ico" alt="logo" class="logo" />
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
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
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
