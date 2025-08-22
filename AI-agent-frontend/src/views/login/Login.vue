<template>
  <div class="login-container">
    <div class="login-form">
      <div class="login-header">
        <h2>AI智能代理测试平台</h2>
        <p>欢迎登录系统管理后台</p>
      </div>
      
      <el-form 
        :model="loginForm" 
        :rules="rules" 
        ref="loginFormRef" 
        label-width="0px"
        class="login-form-content"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名" 
            prefix-icon="User"
            size="large"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="rememberMe" size="small">
            记住密码
          </el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="userStore.loading" 
            size="large"
            class="login-button"
          >
            {{ userStore.loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>默认账号：admin / 123456</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/store'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const rememberMe = ref(false)

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' }
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
    
    const success = await userStore.login(loginForm.username, loginForm.password)
    
    if (success) {
      // 如果勾选了记住密码，保存到localStorage
      if (rememberMe.value) {
        localStorage.setItem('rememberedUsername', loginForm.username)
        localStorage.setItem('rememberedPassword', loginForm.password)
      } else {
        localStorage.removeItem('rememberedUsername')
        localStorage.removeItem('rememberedPassword')
      }
      
      // 登录成功，跳转到主页
      await router.push('/')
    }
  } catch (error: any) {
    ElMessage.error(error.message || '登录失败，请重试')
  }
}

// 初始化记住的密码
onMounted(() => {
  const rememberedUsername = localStorage.getItem('rememberedUsername')
  const rememberedPassword = localStorage.getItem('rememberedPassword')
  
  if (rememberedUsername && rememberedPassword) {
    loginForm.username = rememberedUsername
    loginForm.password = rememberedPassword
    rememberMe.value = true
  }
  
  // 如果已经登录，直接跳转
  if (userStore.isLoggedIn) {
    router.push('/')
  }
})
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.login-form {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 50px 40px;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
  
  .login-header {
    text-align: center;
    margin-bottom: 40px;
    
    h2 {
      font-size: 28px;
      font-weight: 600;
      color: #2c3e50;
      margin: 0 0 10px 0;
    }
    
    p {
      color: #7f8c8d;
      font-size: 14px;
      margin: 0;
    }
  }
  
  .login-form-content {
    .el-form-item {
      margin-bottom: 25px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    .el-input {
      --el-input-border-radius: 10px;
      
      :deep(.el-input__wrapper) {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e4e7ed;
        
        &:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        &.is-focus {
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
      }
    }
    
    .login-button {
      width: 100%;
      height: 45px;
      border-radius: 10px;
      font-size: 16px;
      font-weight: 500;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border: none;
      
      &:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
      }
      
      &:active {
        transform: translateY(0);
      }
    }
  }
  
  .login-footer {
    text-align: center;
    margin-top: 30px;
    
    p {
      color: #95a5a6;
      font-size: 12px;
      margin: 0;
    }
  }
}

// 响应式设计
@media (max-width: 480px) {
  .login-container {
    padding: 10px;
  }
  
  .login-form {
    padding: 30px 20px;
    
    .login-header {
      margin-bottom: 30px;
      
      h2 {
        font-size: 24px;
      }
    }
  }
}
</style>
