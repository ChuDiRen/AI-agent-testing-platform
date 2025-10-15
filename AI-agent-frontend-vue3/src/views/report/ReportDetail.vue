<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="report-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Document /></el-icon>
            报告详情
          </span>
          <div class="actions">
            <el-button @click="handleBack">
              <el-icon><Back /></el-icon>
              返回
            </el-button>
            <el-button type="success" @click="handleExport('excel')">
              <el-icon><Download /></el-icon>
              导出Excel
            </el-button>
            <el-button type="success" @click="handleExport('pdf')">
              <el-icon><Download /></el-icon>
              导出PDF
            </el-button>
            <el-button type="danger" @click="handleDelete">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="report" class="detail-content">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" :column="2" border>
          <el-descriptions-item label="报告ID">
            {{ report.report_id }}
          </el-descriptions-item>
          <el-descriptions-item label="报告名称">
            {{ report.name }}
          </el-descriptions-item>
          <el-descriptions-item label="报告类型">
            <el-tag>{{ report.report_type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(report.status)">
              {{ getStatusText(report.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总用例数">
            {{ report.total_cases }}
          </el-descriptions-item>
          <el-descriptions-item label="通过率">
            <el-progress
              :percentage="report.pass_rate"
              :color="getProgressColor(report.pass_rate)"
            />
          </el-descriptions-item>
          <el-descriptions-item label="执行时长">
            {{ report.duration || 0 }}ms
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(report.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 统计图表 -->
        <div class="charts-section">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12">
              <el-card shadow="hover">
                <template #header>
                  <span>用例状态分布</span>
                </template>
                <div ref="pieChartRef" style="height: 300px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-card shadow="hover">
                <template #header>
                  <span>用例执行结果</span>
                </template>
                <div ref="barChartRef" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <!-- 执行记录 -->
        <div class="section">
          <h3>执行记录</h3>
          <el-table :data="executions" border stripe>
            <el-table-column type="index" label="#" width="60" />
            <el-table-column prop="testcase_id" label="用例ID" width="100" />
            <el-table-column label="用例名称" min-width="200">
              <template #default="{ row }">
                <span>用例 {{ row.testcase_id }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getExecutionStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时(ms)" width="100" />
            <el-table-column prop="created_at" label="执行时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="错误信息" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="row.error_message" class="error-text">
                  {{ row.error_message }}
                </span>
                <span v-else>-</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Back,
  Download,
  Delete
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import {
  getReportAPI,
  getReportExecutionsAPI,
  deleteReportAPI,
  downloadReportFile,
  type TestReportDetail,
  type TestExecution
} from '@/api/report'

const route = useRoute()
const router = useRouter()

// 状态
const loading = ref(false)
const report = ref<TestReportDetail | null>(null)
const executions = ref<TestExecution[]>([])

// 图表引用
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
let pieChart: ECharts | null = null
let barChart: ECharts | null = null

// 加载报告详情
const loadReport = async () => {
  loading.value = true
  try {
    const response = await getReportAPI(Number(route.params.id))
    if (response.data) {
      report.value = response.data
      loadExecutions()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
    router.back()
  } finally {
    loading.value = false
  }
}

// 加载执行记录
const loadExecutions = async () => {
  try {
    const response = await getReportExecutionsAPI(Number(route.params.id))
    if (response.data) {
      executions.value = response.data
      // 加载数据后渲染图表
      nextTick(() => {
        renderCharts()
      })
    }
  } catch (error) {
    console.error('加载执行记录失败:', error)
  }
}

// 渲染图表
const renderCharts = () => {
  if (!report.value) return

  // 饼图 - 用例状态分布
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    const pieOption = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          name: '用例状态',
          type: 'pie',
          radius: '60%',
          data: [
            { value: report.value.passed_cases, name: '通过', itemStyle: { color: '#67c23a' } },
            { value: report.value.failed_cases, name: '失败', itemStyle: { color: '#f56c6c' } },
            {
              value: report.value.total_cases - report.value.passed_cases - report.value.failed_cases,
              name: '跳过',
              itemStyle: { color: '#909399' }
            }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
    pieChart.setOption(pieOption)
  }

  // 柱状图 - 用例执行结果
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    const barOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['通过', '失败', '跳过']
      },
      xAxis: {
        type: 'category',
        data: ['测试结果']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '通过',
          type: 'bar',
          data: [report.value.passed_cases],
          itemStyle: { color: '#67c23a' }
        },
        {
          name: '失败',
          type: 'bar',
          data: [report.value.failed_cases],
          itemStyle: { color: '#f56c6c' }
        },
        {
          name: '跳过',
          type: 'bar',
          data: [report.value.total_cases - report.value.passed_cases - report.value.failed_cases],
          itemStyle: { color: '#909399' }
        }
      ]
    }
    barChart.setOption(barOption)
  }
}

// 返回
const handleBack = () => {
  router.push('/report/list')
}

// 导出报告
const handleExport = async (format: 'pdf' | 'excel') => {
  if (!report.value) return

  try {
    ElMessage.info(`正在导出${format.toUpperCase()}...`)
    await downloadReportFile(
      report.value.report_id,
      format,
      `${report.value.name}.${format === 'pdf' ? 'pdf' : 'xlsx'}`
    )
    ElMessage.success('导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出失败')
  }
}

// 删除
const handleDelete = async () => {
  await ElMessageBox.confirm(
    '确认删除此报告吗？此操作不可恢复。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )

  try {
    await deleteReportAPI(Number(route.params.id))
    ElMessage.success('删除成功')
    router.push('/report/list')
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 辅助函数
const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '待处理',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

const getExecutionStatusType = (status: string) => {
  const statusMap: Record<string, any> = {
    passed: 'success',
    failed: 'danger',
    skipped: 'info',
    error: 'warning'
  }
  return statusMap[status] || ''
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 初始化
onMounted(() => {
  loadReport()
})

// 清理
onUnmounted(() => {
  if (pieChart) {
    pieChart.dispose()
  }
  if (barChart) {
    barChart.dispose()
  }
})
</script>

<style scoped lang="scss">
.report-detail-container {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 500;
    }

    .actions {
      display: flex;
      gap: 10px;
    }
  }

  .detail-content {
    .charts-section {
      margin-top: 30px;
    }

    .section {
      margin-top: 30px;

      h3 {
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #409eff;
        font-size: 16px;
        color: #303133;
      }
    }

    .error-text {
      color: #f56c6c;
    }
  }
}
</style>

