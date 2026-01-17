<template>
  <div class="login-container">
    <!-- 渐变背景 -->
    <div class="gradient-bg"></div>
    
    <!-- 装饰性几何图形 -->
    <div class="geometric-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <!-- 主内容区域 -->
    <div class="content-wrapper">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-content">
          <h1 class="brand-title">
            <span class="brand-icon">🧪</span>
            API 自动化测试平台
          </h1>
          <p class="brand-subtitle">专业的接口测试管理解决方案</p>
          <div class="feature-list">
            <div class="feature-item">
              <svg class="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>智能用例管理</span>
            </div>
            <div class="feature-item">
              <svg class="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>高效执行引擎</span>
            </div>
            <div class="feature-item">
              <svg class="feature-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span>可视化报告</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录卡片 -->
      <div class="login-card-wrapper">
        <div class="login-card">
          <div class="card-header">
            <h2 class="card-title">欢迎回来</h2>
            <p class="card-subtitle">登录您的账户以继续</p>
          </div>

          <el-form ref="formRef" :model="form" :rules="rules" class="login-form">
            <el-form-item prop="username">
              <div class="input-wrapper">
                <label class="input-label">用户名</label>
                <el-input 
                  v-model="form.username" 
                  placeholder="请输入用户名"
                  size="large"
                  class="modern-input"
                >
                  <template #prefix>
                    <el-icon><User /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>
            
            <el-form-item prop="password">
              <div class="input-wrapper">
                <label class="input-label">密码</label>
                <el-input 
                  v-model="form.password" 
                  placeholder="请输入密码" 
                  type="password" 
                  show-password
                  size="large"
                  class="modern-input"
                >
                  <template #prefix>
                    <el-icon><Lock /></el-icon>
                  </template>
                </el-input>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button 
                type="primary" 
                @click="onSubmit" 
                class="login-button"
                size="large"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>

          <div class="card-footer">
            <p class="footer-text">首次使用？请联系管理员开通账号</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 导入响应式模块
import { ref,reactive } from "vue";
// 导入route管理
import { useRouter } from "vue-router";
//  导入登录的脚本
import loginApi from "./loginApi";
import { ElMessage } from "element-plus";
// 实例化对象
const router = useRouter();

// 字段校验：script增加如下代码
const rules = {
  username: [{ required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 3, max: 15, message: '用户名长度必须在3-15之间', trigger: 'blur' },],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' },
  { min: 6, max: 12, message: '用户名长度必须在6-12之间', trigger: 'blur' },],
  // ...
}

// do not use same name with ref
const form = reactive({
  username: "",
  password: "",
});

// 第一步：获取页面的数据-响应式API(记得要导入)
const formRef =ref(null)
// 第二步：进行数据校验
const onSubmit = () => {
  // 执行对应的数据校验
  console.log(formRef.value.validate); // 回调函数...执行一遍之后结果可以当参数传递
  // 函数即可调用
  formRef.value.validate((valid)=>{
    console.log(valid) // 无数据返回：false；否则返回：true
    // 接下来我们就可以在这个位置写逻辑
    if(!valid){
      console.log("校验不通过")
      return false // 如果是false ，则直接返回
    }
    console.log("校验通过")
    // 验证通过之后进行开始发送请求
    loginApi.login({ username: form.username, password: form.password })
    .then(res=>{
      console.log("当前的响应数据：",res.data.data.token)

      // 前端进行判断并且跳转
      if(res.data.code ==200 && res.data.data.token != null){
      // 写入token到请求头中
      // 存储令牌（加密后的字符串）
      localStorage.setItem('token', res.data.data.token);
      // 存储 refreshToken
      localStorage.setItem('refreshToken', res.data.data.refreshToken);
      console.log("登录成功，token 和 refreshToken 已保存")
      router.push("/home")// 假设我们跳转到主页面
      ElMessage.success(res.data.msg)
      }
    })
    .catch(err=>{
       console.log(err)
    })
    // router.push("/home")// 假设我们跳转到主页面
  })
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');

.login-container {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  font-family: 'Open Sans', sans-serif;
}

/* 背景 */
.gradient-bg {
  position: absolute;
  inset: 0;
  background: var(--color-bg-primary);
  z-index: 0;
}

/* 装饰性几何图形 */
.geometric-shapes {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0.05;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: var(--color-primary);
}

.shape-1 {
  width: 400px;
  height: 400px;
  top: -100px;
  left: -100px;
  animation: float 20s ease-in-out infinite;
}

.shape-2 {
  width: 300px;
  height: 300px;
  bottom: -50px;
  right: 10%;
  animation: float 15s ease-in-out infinite reverse;
}

.shape-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -50px;
  animation: float 18s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(5deg); }
}

/* 主内容区域 */
.content-wrapper {
  position: relative;
  z-index: 2;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  padding: 2rem;
  align-items: center;
}

/* 左侧品牌区域 */
.brand-section {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.brand-content {
  max-width: 500px;
}

.brand-title {
  font-family: 'Poppins', sans-serif;
  font-size: 3rem;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 1rem;
  line-height: 1.2;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand-icon {
  font-size: 3.5rem;
}

.brand-subtitle {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  margin-bottom: 3rem;
  font-weight: 300;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--color-text-primary);
  font-size: 1.1rem;
  padding: 1rem;
  background: white;
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

.feature-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateX(10px);
  border-color: var(--color-primary);
}

.feature-icon {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}

/* 右侧登录卡片 */
.login-card-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.card-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.card-title {
  font-family: 'Poppins', sans-serif;
  font-size: 2rem;
  font-weight: 600;
  color: #1E293B;
  margin-bottom: 0.5rem;
}

.card-subtitle {
  font-size: 0.95rem;
  color: #64748B;
  font-weight: 400;
}

.login-form {
  margin-top: 2rem;
}

.input-wrapper {
  margin-bottom: 0.5rem;
}

.input-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 0.5rem;
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.3);
}

.card-footer {
  margin-top: 2rem;
  text-align: center;
}

.footer-text {
  font-size: 0.875rem;
  color: #64748B;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .content-wrapper {
    grid-template-columns: 1fr;
    padding: 1rem;
  }
  
  .brand-section {
    display: none;
  }
  
  .login-card {
    max-width: 100%;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-input__wrapper) {
  background-color: #F8FAFC;
  border-radius: 12px;
  padding: 12px 16px;
  box-shadow: none;
  border: 1px solid #E2E8F0;
  transition: all 0.2s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #CBD5E1;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #2563EB;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

:deep(.el-input__inner) {
  font-size: 0.95rem;
  color: #1E293B;
}

:deep(.el-input__inner::placeholder) {
  color: #94A3B8;
}
</style>