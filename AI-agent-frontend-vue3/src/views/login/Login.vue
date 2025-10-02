<template>
  <div class="min-h-screen flex-center bg-animated-gradient overflow-hidden relative">
    <!-- 背景动画粒子 -->
    <div class="particles-container">
      <div v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></div>
    </div>
    
    <!-- 浮动的装饰圆圈 -->
    <div class="floating-circles">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <div class="w-full max-w-md px-6 relative z-10">
      <el-card class="login-card backdrop-blur-lg bg-white/90 shadow-2xl rounded-3xl border-0 transform hover:scale-105 transition-all duration-500">
        <template #header>
          <div class="flex-col-center space-y-4 py-2">
            <!-- Logo with animation -->
            <div class="logo-container relative">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex-center text-white text-4xl font-bold shadow-2xl animate-float">
                AI
              </div>
              <div class="absolute inset-0 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 blur-xl opacity-50 animate-pulse"></div>
            </div>
            
            <div class="text-center">
              <h2 class="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2 animate-fade-in">
                AI Agent测试平台
              </h2>
              <p class="text-sm text-gray-500 animate-fade-in-delay">欢迎回来，请登录您的账户</p>
            </div>
          </div>
        </template>

        <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="space-y-5">
          <el-form-item prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名" 
              prefix-icon="User"
              size="large"
              class="w-full input-animated"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              prefix-icon="Lock"
              size="large"
              class="w-full input-animated"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-form-item class="mb-0">
            <el-button 
              type="primary" 
              size="large"
              class="w-full h-12 text-base font-semibold btn-animated"
              @click="handleLogin"
              :loading="loading"
            >
              <span v-if="!loading" class="flex items-center justify-center gap-2">
                <span>登录</span>
                <span class="text-lg">→</span>
              </span>
              <span v-else>登录中...</span>
            </el-button>
          </el-form-item>
        </el-form>

        <div class="mt-6 text-center">
          <div class="flex-between text-sm">
            <a href="#" class="text-blue-500 hover:text-blue-600 transition-colors duration-300 hover:underline">忘记密码？</a>
            <a href="#" class="text-blue-500 hover:text-blue-600 transition-colors duration-300 hover:underline">注册账号</a>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ]
})

const getParticleStyle = (_index: number) => {
  const randomX = Math.random() * 100
  const randomY = Math.random() * 100
  const randomDelay = Math.random() * 5
  const randomDuration = 3 + Math.random() * 4
  
  return {
    left: `${randomX}%`,
    top: `${randomY}%`,
    animationDelay: `${randomDelay}s`,
    animationDuration: `${randomDuration}s`
  }
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid: boolean): Promise<void> => {
    if (valid) {
      loading.value = true
      try {
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        localStorage.setItem('token', 'demo-token')
        localStorage.setItem('username', loginForm.username)
        
        ElMessage.success('登录成功！')
        router.push('/home')
      } catch (error) {
        ElMessage.error('登录失败，请重试')
      } finally {
        loading.value = false
      }
    } else {
      ElMessage.error('请填写正确的登录信息')
      return
    }
  })
}
</script>

<style scoped>
/* 登录页面使用全局样式，仅保留特殊定制 */
.animate-fade-in-delay {
  animation: fade-in 0.6s ease-out 0.2s both;
}
</style>
