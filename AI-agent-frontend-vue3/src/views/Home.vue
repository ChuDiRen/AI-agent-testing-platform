<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50 p-6 relative overflow-hidden">
    <!-- 背景装饰 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
      <div class="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="max-w-7xl mx-auto relative z-10">
      <!-- 头部区域 -->
      <div class="text-center mb-10 animate-fade-in-down">
        <h1 class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 mb-4 animate-gradient">
          AI Agent Testing Platform
        </h1>
        <p class="text-xl text-gray-600 animate-pulse-slow">智能代理测试平台 - 让AI测试更简单</p>
      </div>

      <!-- 欢迎卡片 -->
      <el-card class="welcome-card shadow-2xl rounded-3xl border-0 mb-8 backdrop-blur-sm bg-white/80 hover:shadow-purple-500/20 transition-all duration-500 transform hover:-translate-y-2">
        <template #header>
          <div class="flex-between py-2">
            <span class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              欢迎使用AI Agent测试平台
            </span>
            <el-tag type="success" effect="dark" class="animate-pulse">
              <span class="flex items-center gap-1">
                <span class="w-2 h-2 bg-white rounded-full animate-ping"></span>
                在线
              </span>
            </el-tag>
          </div>
        </template>
        <div class="text-center py-10 space-y-8">
          <p class="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
            这是一个用于测试AI Agent的专业平台，支持本地API测试环境联调，提供完整的测试用例管理和报告生成功能。
          </p>
          <div class="flex-center">
            <el-button type="primary" size="large" @click="startTest" class="px-10 py-3 btn-glow">
              <el-icon class="mr-2"><VideoPlay /></el-icon>
              <span class="font-semibold">开始测试</span>
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 功能特性网格 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-8">
        <el-card 
          v-for="(feature, index) in features" 
          :key="feature.title"
          class="feature-card hover:shadow-2xl transition-all duration-500 cursor-pointer transform hover:-translate-y-3 rounded-2xl border-0 backdrop-blur-sm bg-white/90"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div class="text-center space-y-5 py-4">
            <div class="relative inline-block">
              <div :class="['w-20 h-20 mx-auto rounded-2xl flex-center text-4xl transform transition-all duration-500 hover:rotate-12 hover:scale-110', feature.bgClass]">
                {{ feature.icon }}
              </div>
              <div :class="['absolute inset-0 rounded-2xl blur-xl opacity-50', feature.bgClass]"></div>
            </div>
            <h3 class="text-xl font-bold text-gray-800">{{ feature.title }}</h3>
            <p class="text-sm text-gray-600 leading-relaxed px-2">{{ feature.description }}</p>
          </div>
        </el-card>
      </div>

      <!-- 统计信息 -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.label"
          class="stat-card bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-xl text-center transform hover:scale-105 transition-all duration-500 hover:shadow-2xl"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <div :class="['text-4xl font-bold mb-3 animate-count', stat.color]">{{ stat.value }}</div>
          <div class="text-sm text-gray-600 font-medium">{{ stat.label }}</div>
          <div :class="['h-1 w-12 mx-auto mt-3 rounded-full', stat.bgColor]"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const features = reactive([
  {
    icon: '🤖',
    title: 'AI Agent测试',
    description: '支持多种AI模型的智能代理测试，提供全方位评估体系',
    bgClass: 'bg-gradient-to-br from-blue-400 to-blue-600 text-white shadow-blue-500/50'
  },
  {
    icon: '📊',
    title: '测试报告',
    description: '详细的测试报告和数据分析，可视化展示测试结果',
    bgClass: 'bg-gradient-to-br from-green-400 to-green-600 text-white shadow-green-500/50'
  },
  {
    icon: '🔧',
    title: '用例管理',
    description: '灵活的测试用例创建和管理，支持批量导入导出',
    bgClass: 'bg-gradient-to-br from-purple-400 to-purple-600 text-white shadow-purple-500/50'
  },
  {
    icon: '🚀',
    title: '快速部署',
    description: '支持本地和云端快速部署，一键启动测试环境',
    bgClass: 'bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow-orange-500/50'
  },
  {
    icon: '🔐',
    title: '安全可靠',
    description: '企业级安全认证和权限管理，保护您的数据安全',
    bgClass: 'bg-gradient-to-br from-red-400 to-red-600 text-white shadow-red-500/50'
  },
  {
    icon: '📱',
    title: '响应式设计',
    description: '支持多终端访问和使用，随时随地进行测试',
    bgClass: 'bg-gradient-to-br from-indigo-400 to-indigo-600 text-white shadow-indigo-500/50'
  }
])

const stats = reactive([
  { label: '测试用例', value: '1,234', color: 'text-blue-600', bgColor: 'bg-blue-600' },
  { label: '测试报告', value: '567', color: 'text-green-600', bgColor: 'bg-green-600' },
  { label: 'AI模型', value: '12', color: 'text-purple-600', bgColor: 'bg-purple-600' },
  { label: '活跃用户', value: '89', color: 'text-orange-600', bgColor: 'bg-orange-600' }
])

const startTest = async () => {
  try {
    ElMessage.success('测试启动成功！')
  } catch (error) {
    ElMessage.error('测试启动失败，请检查API连接')
    console.error(error)
  }
}
</script>

<style scoped>
/* 首页使用全局样式 */
</style>
