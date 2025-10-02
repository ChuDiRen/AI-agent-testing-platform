<template>
  <div class="min-h-screen flex-center bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 relative overflow-hidden">
    <!-- 动态背景元素 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 left-0 w-full h-full">
        <div v-for="i in 15" :key="i" 
          class="floating-shape absolute" 
          :style="getShapeStyle(i)">
        </div>
      </div>
    </div>

    <div class="text-center space-y-10 px-6 relative z-10">
      <!-- 404动画区域 -->
      <div class="relative">
        <!-- 主404文字 -->
        <div class="text-404 text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 animate-glitch">
          404
        </div>
        <!-- 故障效果层 -->
        <div class="text-404 text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 absolute inset-0 animate-glitch-2" style="clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%);">
          404
        </div>
        <div class="text-404 text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 absolute inset-0 animate-glitch-3" style="clip-path: polygon(0 55%, 100% 55%, 100% 100%, 0 100%);">
          404
        </div>
        <!-- 光晕效果 -->
        <div class="absolute inset-0 blur-3xl opacity-30">
          <div class="text-9xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 animate-pulse">
            404
          </div>
        </div>
      </div>

      <!-- 消息区域 -->
      <div class="space-y-5 animate-fade-in-up">
        <h1 class="text-4xl font-bold text-gray-800 animate-bounce-in">页面走丢了</h1>
        <p class="text-xl text-gray-600 max-w-md mx-auto leading-relaxed">
          糟糕！您访问的页面似乎去了另一个维度 🌌
        </p>
      </div>

      <!-- 动画插图 -->
      <div class="flex-center text-8xl animate-float-rotate">
        <div class="relative">
          <div class="animate-spin-slow">🔍</div>
          <div class="absolute inset-0 animate-ping-slow opacity-50">🔍</div>
        </div>
      </div>

      <!-- 建议卡片 -->
      <el-card class="max-w-lg mx-auto shadow-2xl rounded-3xl border-0 backdrop-blur-lg bg-white/80 transform hover:scale-105 transition-all duration-500 animate-slide-up">
        <div class="space-y-5">
          <h3 class="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">
            您可以尝试：
          </h3>
          <ul class="text-left space-y-4 text-gray-600">
            <li class="flex items-center space-x-3 p-3 rounded-xl hover:bg-indigo-50 transition-all duration-300 cursor-pointer transform hover:translate-x-2">
              <span class="w-3 h-3 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-pulse"></span>
              <span class="text-base">检查URL是否正确输入</span>
            </li>
            <li class="flex items-center space-x-3 p-3 rounded-xl hover:bg-purple-50 transition-all duration-300 cursor-pointer transform hover:translate-x-2">
              <span class="w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full animate-pulse animation-delay-200"></span>
              <span class="text-base">返回首页重新开始探索</span>
            </li>
            <li class="flex items-center space-x-3 p-3 rounded-xl hover:bg-pink-50 transition-all duration-300 cursor-pointer transform hover:translate-x-2">
              <span class="w-3 h-3 bg-gradient-to-r from-pink-500 to-orange-500 rounded-full animate-pulse animation-delay-400"></span>
              <span class="text-base">联系管理员获取帮助</span>
            </li>
          </ul>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="flex flex-wrap justify-center gap-5 pt-6 animate-fade-in-up animation-delay-600">
        <el-button 
          type="primary" 
          size="large" 
          @click="goHome"
          class="btn-primary px-10 py-4 text-base font-semibold transform hover:scale-110 transition-all duration-300"
        >
          <el-icon class="mr-2"><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button 
          size="large" 
          @click="goBack"
          class="btn-secondary px-10 py-4 text-base font-semibold transform hover:scale-110 transition-all duration-300"
        >
          <el-icon class="mr-2"><Back /></el-icon>
          返回上一页
        </el-button>
      </div>

      <!-- 提示信息 -->
      <div class="text-sm text-gray-500 pt-10 animate-fade-in animation-delay-800">
        <p class="flex items-center justify-center space-x-2">
          <span>💡</span>
          <span>如果问题持续存在，请联系技术支持</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/home')
}

const goBack = () => {
  router.go(-1)
}

const getShapeStyle = (index: number) => {
  const shapes = ['circle', 'square', 'triangle']
  const shape = shapes[index % 3]
  const size = 20 + Math.random() * 60
  const left = Math.random() * 100
  const top = Math.random() * 100
  const delay = Math.random() * 5
  const duration = 3 + Math.random() * 5
  
  const baseStyle = {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    background: `linear-gradient(135deg, 
      hsl(${240 + Math.random() * 60}, 70%, 60%), 
      hsl(${280 + Math.random() * 60}, 70%, 70%))`
  }
  
  if (shape === 'circle') {
    return { ...baseStyle, borderRadius: '50%' }
  } else if (shape === 'triangle') {
    return { ...baseStyle, clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }
  }
  
  return baseStyle
}
</script>

<style scoped>
/* 404页面使用全局样式 */
</style>
