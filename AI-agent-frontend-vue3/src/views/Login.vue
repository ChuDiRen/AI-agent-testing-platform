<template>
  <div class="login-container flex-center">
    <el-card class="login-card">
      <h2 class="login-title">AI Agent测试平台</h2>
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" class="login-button" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const loginFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid: boolean): Promise<void> => {
    if (valid) {
      // 这里可以调用API进行登录验证
      // 模拟登录成功
      localStorage.setItem('token', 'demo-token')
      ElMessage.success('登录成功')
      router.push('/')
    } else {
      ElMessage.error('请填写正确的登录信息')
      return
    }
  })
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  background-color: var(--background-color);
}

.login-card {
  width: 400px;
  padding: 20px;
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: var(--primary-color);
}

.login-button {
  width: 100%;
}
</style>