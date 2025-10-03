<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="dashboard-content" v-loading="dashboardStore.loading">
    <!-- 统计卡片区 -->
    <div class="stats-cards">
      <el-card class="stat-card" @click="router.push('/api/testcase')">
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
</template>

<script setup lang="ts">
// Copyright (c) 2025 左岚. All rights reserved.
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore } from '@/store/dashboard'
import { ElMessage } from 'element-plus'
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
const dashboardStore = useDashboardStore()

// 监听刷新事件
const handleRefresh = () => {
  dashboardStore.fetchDashboardData()
}

// 初始化数据
onMounted(() => {
  dashboardStore.fetchDashboardData()
  
  // 监听刷新事件
  window.addEventListener('manual-refresh', handleRefresh)
  window.addEventListener('auto-refresh', handleRefresh)
})

// 组件卸载时清理事件监听
onUnmounted(() => {
  window.removeEventListener('manual-refresh', handleRefresh)
  window.removeEventListener('auto-refresh', handleRefresh)
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
    top: '10%'
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
.dashboard-content {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 64px);
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

/* 响应式设计 */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .dashboard-content {
    padding: 16px;
  }
}
</style>
