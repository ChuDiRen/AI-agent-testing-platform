<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <el-icon class="logo-icon"><BulbFilled /></el-icon>
        <h1 class="title">华测自动化测试平台</h1>
        <el-icon class="menu-icon"><Expand /></el-icon>
      </div>

      <!-- 菜单列表 -->
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        @select="handleMenuSelect"
      >
        <!-- 系统管理 -->
        <el-sub-menu index="1">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="1-1" @click="router.push('/system/user')">用户管理</el-menu-item>
          <el-menu-item index="1-2" @click="router.push('/system/role')">角色管理</el-menu-item>
          <el-menu-item index="1-3" @click="router.push('/system/permission')">权限管理</el-menu-item>
        </el-sub-menu>

        <!-- 接口自动化 -->
        <el-sub-menu index="2">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>接口自动化</span>
          </template>
          <el-menu-item index="2-1" @click="router.push('/api/testcase')">测试用例</el-menu-item>
          <el-menu-item index="2-2" @click="router.push('/api/execute')">测试执行</el-menu-item>
          <el-menu-item index="2-3" @click="router.push('/api/report')">测试报告</el-menu-item>
        </el-sub-menu>

        <!-- WEB自动化 -->
        <el-sub-menu index="3">
          <template #title>
            <el-icon><ChromeFilled /></el-icon>
            <span>WEB自动化</span>
          </template>
          <el-menu-item index="3-1" @click="router.push('/web/testcase')">测试用例</el-menu-item>
          <el-menu-item index="3-2" @click="router.push('/web/execute')">测试执行</el-menu-item>
          <el-menu-item index="3-3" @click="router.push('/web/report')">测试报告</el-menu-item>
        </el-sub-menu>

        <!-- APP自动化 -->
        <el-sub-menu index="4">
          <template #title>
            <el-icon><MobileFilled /></el-icon>
            <span>APP自动化</span>
          </template>
          <el-menu-item index="4-1" @click="router.push('/app/testcase')">测试用例</el-menu-item>
          <el-menu-item index="4-2" @click="router.push('/app/execute')">测试执行</el-menu-item>
          <el-menu-item index="4-3" @click="router.push('/app/report')">测试报告</el-menu-item>
        </el-sub-menu>

        <!-- 消息通知管理 -->
        <el-sub-menu index="5">
          <template #title>
            <el-icon><Message /></el-icon>
            <span>消息通知管理</span>
          </template>
          <el-menu-item index="5-1" @click="router.push('/message/list')">消息列表</el-menu-item>
          <el-menu-item index="5-2" @click="router.push('/message/setting')">通知设置</el-menu-item>
        </el-sub-menu>

        <!-- 测试数据管理 -->
        <el-sub-menu index="6">
          <template #title>
            <el-icon><DataAnalysis /></el-icon>
            <span>数据管理</span>
          </template>
          <el-menu-item index="6-1" @click="router.push('/data/testdata')">测试数据</el-menu-item>
        </el-sub-menu>

        <!-- AI 功能 -->
        <el-sub-menu index="7">
          <template #title>
            <el-icon><MagicStick /></el-icon>
            <span>AI 功能</span>
          </template>
          <el-menu-item index="7-1" @click="router.push('/ai/chat')">AI 助手</el-menu-item>
        </el-sub-menu>
      </el-menu>

      <!-- 不固定标签 -->
      <div class="sidebar-footer">
        <span class="footer-text">不固定</span>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 顶部标题栏 -->
      <header class="content-header">
        <div class="header-tabs">
          <div class="tab active">
            <span>主页信息</span>
            <el-icon class="close-icon"><Close /></el-icon>
          </div>
        </div>
        <div class="header-actions">
          <div class="refresh-controls">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              style="margin-right: 15px"
              @change="handleAutoRefreshChange"
            />
            <el-button :icon="Refresh" circle @click="handleManualRefresh" :loading="refreshing" title="刷新数据" />
          </div>
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <el-avatar :size="36" :src="authStore.userInfo?.avatar || defaultAvatar" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>{{ authStore.userInfo?.nickname || '用户' }}</el-dropdown-item>
                <el-dropdown-item divided command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容主体 -->
      <div class="content-body" v-loading="dashboardStore.loading">
        <!-- 统计卡片区 -->
        <div class="stats-cards">
          <el-card class="stat-card" @click="router.push('/testcase')">
            <div class="stat-title">测试用例总数</div>
            <div class="stat-value">{{ dashboardStore.stats.totalCases }}</div>
          </el-card>
          <el-card class="stat-card stat-card-web" @click="router.push('/web/testcase')">
            <div class="stat-title">WEB自动化用例总数</div>
            <div class="stat-value stat-value-web">{{ dashboardStore.stats.webCases }}</div>
          </el-card>
          <el-card class="stat-card stat-card-api" @click="router.push('/api/testcase')">
            <div class="stat-title">API自动化用例总数</div>
            <div class="stat-value stat-value-api">{{ dashboardStore.stats.apiCases }}</div>
          </el-card>
          <el-card class="stat-card stat-card-app" @click="router.push('/app/testcase')">
            <div class="stat-title">APP自动化用例总数</div>
            <div class="stat-value stat-value-app">{{ dashboardStore.stats.appCases }}</div>
          </el-card>
        </div>

        <!-- 图表区 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">近12月增用例趋势图</span>
            </div>
          </template>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-dot legend-dot-web"></span>
              <span>WEB自动化</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot legend-dot-api"></span>
              <span>API自动化</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot legend-dot-app"></span>
              <span>APP自动化</span>
            </div>
          </div>
          <div class="chart-container">
            <v-chart class="chart" :option="chartOption" autoresize />
          </div>
          <div class="chart-note">结合你的选择，进行页面显示</div>
        </el-card>

        <!-- 热点任务状态图表占位 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">热点任务状态图列</span>
            </div>
          </template>
          <div class="placeholder-content">
            <el-empty description="功能开发中..." />
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useDashboardStore } from '@/store/dashboard'
import { ElMessageBox, ElMessage } from 'element-plus'
import { Refresh, DataAnalysis, MagicStick } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'

// 注册 ECharts 组件
use([
  CanvasRenderer,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()
const authStore = useAuthStore()
const dashboardStore = useDashboardStore()

const activeMenu = ref('1')
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

const handleMenuSelect = (index: string) => {
  activeMenu.value = index
  console.log('选中菜单:', index)
}

const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'settings':
      router.push('/message/setting')
      break
    case 'logout':
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await authStore.logout()
      router.push('/login')
      break
  }
}

// 刷新相关
const autoRefresh = ref(false)
const refreshing = ref(false)
let refreshTimer: number | null = null
const REFRESH_INTERVAL = 30000 // 30秒刷新一次

// 手动刷新
const handleManualRefresh = async () => {
  refreshing.value = true
  try {
    await dashboardStore.fetchDashboardData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

// 自动刷新切换
const handleAutoRefreshChange = (value: boolean) => {
  if (value) {
    // 启动自动刷新
    refreshTimer = window.setInterval(() => {
      dashboardStore.fetchDashboardData()
    }, REFRESH_INTERVAL)
    ElMessage.success('已开启自动刷新（每30秒）')
  } else {
    // 停止自动刷新
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
    ElMessage.info('已关闭自动刷新')
  }
}

// 初始化数据
onMounted(() => {
  dashboardStore.fetchDashboardData()
})

// 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})

// 图表配置 - 使用真实数据
const chartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderColor: '#e5e7eb',
    borderWidth: 1,
    textStyle: {
      color: '#374151'
    }
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: dashboardStore.trendData.timeline,
    axisLine: {
      lineStyle: {
        color: '#e5e7eb'
      }
    },
    axisLabel: {
      color: '#9ca3af',
      fontSize: 12
    }
  },
  yAxis: {
    type: 'value',
    axisLine: {
      show: false
    },
    axisLabel: {
      color: '#9ca3af',
      fontSize: 12
    },
    splitLine: {
      lineStyle: {
        color: '#f3f4f6',
        type: 'dashed'
      }
    }
  },
  series: [
    {
      name: 'WEB自动化',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      data: dashboardStore.trendData.web,
      lineStyle: {
        width: 3,
        color: '#5470c6'
      },
      itemStyle: {
        color: '#5470c6',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0,
              color: 'rgba(84, 112, 198, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(84, 112, 198, 0.05)'
            }
          ]
        }
      }
    },
    {
      name: 'API自动化',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      data: dashboardStore.trendData.api,
      lineStyle: {
        width: 3,
        color: '#91cc75'
      },
      itemStyle: {
        color: '#91cc75',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0,
              color: 'rgba(145, 204, 117, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(145, 204, 117, 0.05)'
            }
          ]
        }
      }
    },
    {
      name: 'APP自动化',
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      data: dashboardStore.trendData.app,
      lineStyle: {
        width: 3,
        color: '#fac858'
      },
      itemStyle: {
        color: '#fac858',
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0,
              color: 'rgba(250, 200, 88, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(250, 200, 88, 0.05)'
            }
          ]
        }
      }
    }
  ]
}))
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

/* 侧边栏样式 */
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #5b6bdc 0%, #4755c9 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 28px;
  color: #fbbf24;
}

.title {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: white;
}

.menu-icon {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.menu-icon:hover {
  transform: rotate(180deg);
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
  overflow-y: auto;
}

:deep(.el-menu) {
  background-color: transparent;
  border: none;
}

:deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.9);
  height: 48px;
  line-height: 48px;
  font-size: 14px;
  padding-left: 20px !important;
}

:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.el-menu-item) {
  color: rgba(255, 255, 255, 0.8);
  height: 44px;
  line-height: 44px;
  font-size: 13px;
  padding-left: 50px !important;
}

:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
}

:deep(.el-sub-menu .el-menu) {
  background-color: rgba(0, 0, 0, 0.1);
}

:deep(.el-sub-menu__icon-arrow) {
  color: rgba(255, 255, 255, 0.7);
}

.sidebar-footer {
  padding: 20px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-header {
  background: white;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-tabs {
  display: flex;
  gap: 8px;
}

.tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.3s;
}

.tab.active {
  background: #eff6ff;
  color: #2563eb;
}

.close-icon {
  font-size: 12px;
  cursor: pointer;
  transition: color 0.3s;
}

.close-icon:hover {
  color: #ef4444;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.refresh-controls {
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-right: 1px solid #e5e7eb;
}

.user-dropdown {
  cursor: pointer;
}

.content-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #f5f7fa;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-card-web {
  background: linear-gradient(135deg, #667eea 0%, #5a67d8 100%);
  color: white;
}

.stat-card-web :deep(.el-card__body) {
  color: white;
}

.stat-card-api {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

.stat-card-api :deep(.el-card__body) {
  color: white;
}

.stat-card-app {
  background: linear-gradient(135deg, #f6ad55 0%, #ed8936 100%);
  color: white;
}

.stat-card-app :deep(.el-card__body) {
  color: white;
}

.stat-title {
  font-size: 14px;
  margin-bottom: 12px;
  opacity: 0.9;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #1f2937;
}

.stat-value-web,
.stat-value-api,
.stat-value-app {
  color: white;
}

/* 图表卡片 */
.chart-card {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.chart-legend {
  display: flex;
  gap: 32px;
  margin-bottom: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot-web {
  background: #5470c6;
}

.legend-dot-api {
  background: #91cc75;
}

.legend-dot-app {
  background: #fac858;
}

.chart-container {
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-note {
  text-align: center;
  color: #ef4444;
  font-size: 14px;
  margin-top: 16px;
}

.placeholder-content {
  padding: 60px 0;
  text-align: center;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  
  .title {
    display: none;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>

