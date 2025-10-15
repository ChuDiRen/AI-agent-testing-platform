<template>
  <div class="execution-console-container">
    <el-page-header @back="goBack">
      <template #content>
        <span>执行控制台</span>
      </template>
      <template #extra>
        <el-tag :type="getStatusType(executionStatus)">{{ executionStatus }}</el-tag>
      </template>
    </el-page-header>

    <el-card class="case-info-card">
      <h3>用例信息</h3>
      <el-descriptions :column="3" border v-if="currentCase">
        <el-descriptions-item label="用例名称">{{ currentCase.name }}</el-descriptions-item>
        <el-descriptions-item label="优先级">{{ currentCase.priority }}</el-descriptions-item>
        <el-descriptions-item label="配置模式">
          <el-tag :type="currentCase.config_mode === 'form' ? 'success' : 'info'">
            {{ currentCase.config_mode === 'form' ? '表单' : 'YAML' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="3">
          {{ currentCase.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="execution-controls">
      <div class="control-bar">
        <el-button
          type="primary"
          :loading="executing"
          :disabled="executionStatus === 'running'"
          @click="handleExecute"
        >
          <el-icon><VideoPlay /></el-icon>
          {{ executing ? '执行中...' : '开始执行' }}
        </el-button>
        <el-button @click="clearLogs">
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>

      <el-divider />

      <div class="context-config">
        <h4>全局变量配置 (可选)</h4>
        <el-input
          v-model="contextJson"
          type="textarea"
          :rows="4"
          placeholder='{"key": "value"}'
        />
      </div>
    </el-card>

    <!-- 执行进度 -->
    <el-card class="progress-card" v-if="executing || executionResult">
      <template #header>
        <div class="progress-header">
          <h3>执行进度</h3>
          <div class="progress-info">
            <el-tag :type="getStatusType(executionStatus)" size="small">{{ executionStatus }}</el-tag>
            <span v-if="executionDuration" class="duration">耗时: {{ executionDuration }}s</span>
          </div>
        </div>
      </template>

      <div class="progress-content">
        <el-progress
          :percentage="progressPercentage"
          :status="getProgressStatus()"
          :stroke-width="8"
          :text-inside="true"
        />

        <div class="step-progress" v-if="stepResults.length > 0">
          <h4>步骤执行进度</h4>
          <el-timeline>
            <el-timeline-item
              v-for="step in stepResults"
              :key="step.step_number"
              :type="getStepStatusType(step.status)"
              :icon="getStepIcon(step.status)"
              :timestamp="step.execution_time ? `${step.execution_time.toFixed(2)}s` : ''"
              placement="top"
            >
              <div class="step-content">
                <div class="step-header">
                  <span class="step-name">{{ step.step_name }}</span>
                  <el-tag :type="getStepStatusType(step.status)" size="small">
                    {{ step.status }}
                  </el-tag>
                </div>
                <div v-if="step.error_message" class="step-error">
                  <el-alert
                    :title="step.error_message"
                    type="error"
                    :closable="false"
                    show-icon
                  />
                </div>
                <div v-if="step.response_data" class="step-response">
                  <el-collapse>
                    <el-collapse-item title="响应数据">
                      <pre class="response-data">{{ JSON.stringify(step.response_data, null, 2) }}</pre>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
    </el-card>

    <!-- 执行日志 -->
    <el-card class="logs-card">
      <template #header>
        <div class="logs-header">
          <h3>执行日志</h3>
          <div class="logs-controls">
            <el-switch
              v-model="autoScroll"
              active-text="自动滚动"
              size="small"
            />
            <el-button size="small" @click="clearLogs">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
            <el-button size="small" @click="downloadLogs">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </div>
        </div>
      </template>

      <div class="logs-container" ref="logsContainerRef">
        <div class="logs-content" v-html="formattedLogs"></div>
      </div>
    </el-card>

    <!-- 执行统计图表 -->
    <el-card class="charts-card" v-if="executionResult && stepResults.length > 0">
      <template #header>
        <h3>执行统计</h3>
      </template>

      <div class="charts-content">
        <el-row :gutter="20">
          <!-- 步骤状态饼图 -->
          <el-col :span="8">
            <div class="chart-container">
              <h4>步骤状态分布</h4>
              <v-chart
                :option="stepStatusChartOption"
                :style="{ height: '300px' }"
                :autoresize="true"
              />
            </div>
          </el-col>

          <!-- 执行时间线图 -->
          <el-col :span="16">
            <div class="chart-container">
              <h4>执行时间趋势</h4>
              <v-chart
                :option="executionTimeChartOption"
                :style="{ height: '300px' }"
                :autoresize="true"
              />
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <!-- HTTP状态码分布 -->
          <el-col :span="12">
            <div class="chart-container">
              <h4>HTTP状态码分布</h4>
              <v-chart
                :option="statusCodeChartOption"
                :style="{ height: '250px' }"
                :autoresize="true"
              />
            </div>
          </el-col>

          <!-- 响应时间分布 -->
          <el-col :span="12">
            <div class="chart-container">
              <h4>响应时间分布</h4>
              <v-chart
                :option="responseTimeChartOption"
                :style="{ height: '250px' }"
                :autoresize="true"
              />
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 执行结果详情 -->
    <el-card class="result-card" v-if="executionResult">
      <template #header>
        <div class="result-header">
          <h3>执行结果</h3>
          <div class="result-actions">
            <el-button size="small" @click="exportReport">
              <el-icon><Download /></el-icon>
              导出报告
            </el-button>
          </div>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(executionResult.status)">
            {{ executionResult.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="总耗时">
          {{ executionResult.duration }}s
        </el-descriptions-item>
        <el-descriptions-item label="开始时间" :span="2">
          {{ formatDate(executionResult.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间" :span="2">
          {{ formatDate(executionResult.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="通过步骤" :span="1">
          <el-tag type="success">{{ passedStepsCount }}/{{ totalStepsCount }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="失败步骤" :span="1">
          <el-tag type="danger">{{ failedStepsCount }}/{{ totalStepsCount }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 详细步骤结果 -->
      <div v-if="stepResults.length > 0" style="margin-top: 20px;">
        <h4>步骤执行详情</h4>
        <el-table :data="stepResults" stripe style="width: 100%">
          <el-table-column prop="step_number" label="步骤" width="80" />
          <el-table-column prop="step_name" label="步骤名称" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStepStatusType(row.status)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="响应状态码" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.response_data?.status_code"
                :type="getStatusCodeType(row.response_data.status_code)"
                size="small">
                {{ row.response_data.status_code }}
              </el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="execution_time" label="耗时" width="100">
            <template #default="{ row }">
              <span v-if="row.execution_time">{{ row.execution_time.toFixed(2) }}s</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click="showStepDetail(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, Delete, Download, CircleCheck, Close, Warning, Loading } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import { executionAPI } from '../api'
import { use } from 'echarts/core'
import { PieChart, LineChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

// 注册 ECharts 组件
use([
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  PieChart,
  LineChart,
  BarChart,
  CanvasRenderer
])

const route = useRoute()
const router = useRouter()
const store = useApiEngineStore()

const caseId = computed(() => Number(route.params.id))

const currentCase = ref<any>(null)
const executing = ref(false)
const executionStatus = ref('pending')
const logs = ref('')
const taskId = ref('')
const executionDuration = ref(0)
const executionResult = ref<any>(null)
const contextJson = ref('{}')
const logsContainerRef = ref<HTMLElement>()

// 新增的响应式变量
const autoScroll = ref(true)
const stepResults = ref<any[]>([])
const currentStep = ref(0)
const totalSteps = ref(0)

let eventSource: EventSource | null = null
let statusCheckTimer: any = null

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger',
    error: 'danger'
  }
  return map[status] || 'info'
}

// 计算进度百分比
const progressPercentage = computed(() => {
  if (totalSteps.value === 0) return 0
  if (executionStatus.value === 'success') return 100
  if (executionStatus.value === 'failed' || executionStatus.value === 'error') return 100
  return Math.round((currentStep.value / totalSteps.value) * 100)
})

// 获取进度条状态
const getProgressStatus = () => {
  if (executionStatus.value === 'success') return 'success'
  if (executionStatus.value === 'failed' || executionStatus.value === 'error') return 'exception'
  if (executing.value) return ''
  return 'warning'
}

// 格式化日志内容
const formattedLogs = computed(() => {
  return logs.value
    .split('\n')
    .map(line => {
      let className = 'log-line'
      let icon = ''

      if (line.includes('✅')) {
        className += ' log-success'
        icon = '<i class="el-icon-success"></i>'
      } else if (line.includes('❌')) {
        className += ' log-error'
        icon = '<i class="el-icon-error"></i>'
      } else if (line.includes('⚠️')) {
        className += ' log-warning'
        icon = '<i class="el-icon-warning"></i>'
      } else if (line.includes('ℹ️')) {
        className += ' log-info'
        icon = '<i class="el-icon-info"></i>'
      } else if (line.includes('开始执行步骤：')) {
        className += ' log-step'
        icon = '<i class="el-icon-arrow-right"></i>'
      } else if (line.includes('=====') || line.includes('========')) {
        className += ' log-separator'
      } else if (line.includes('[INFO]')) {
        className += ' log-system'
        icon = '<i class="el-icon-setting"></i>'
      }

      return `<div class="${className}">${icon} ${line}</div>`
    })
    .join('')
})

// 获取步骤状态类型
const getStepStatusType = (status: string) => {
  const map: Record<string, any> = {
    success: 'success',
    failed: 'danger',
    error: 'danger',
    running: 'warning'
  }
  return map[status] || 'info'
}

// 获取步骤图标
const getStepIcon = (status: string) => {
  const map: Record<string, any> = {
    success: CircleCheck,
    failed: Close,
    error: Close,
    running: Loading
  }
  return map[status] || VideoPlay
}

// 计算步骤统计
const stepStatistics = computed(() => {
  const stats = {
    success: 0,
    failed: 0,
    error: 0,
    unknown: 0
  }

  stepResults.value.forEach(step => {
    if (stats.hasOwnProperty(step.status)) {
      stats[step.status]++
    } else {
      stats.unknown++
    }
  })

  return stats
})

// 计算通过/失败步骤数
const passedStepsCount = computed(() => stepStatistics.value.success)
const failedStepsCount = computed(() => stepStatistics.value.failed + stepStatistics.value.error)
const totalStepsCount = computed(() => stepResults.value.length)

// 步骤状态饼图配置
const stepStatusChartOption = computed(() => ({
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
      name: '步骤状态',
      type: 'pie',
      radius: '50%',
      data: [
        { value: stepStatistics.value.success, name: '成功', itemStyle: { color: '#67c23a' } },
        { value: stepStatistics.value.failed, name: '失败', itemStyle: { color: '#f56c6c' } },
        { value: stepStatistics.value.error, name: '错误', itemStyle: { color: '#e6a23c' } },
        { value: stepStatistics.value.unknown, name: '未知', itemStyle: { color: '#909399' } }
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
}))

// 执行时间线图配置
const executionTimeChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    formatter: '{b}: {c}s'
  },
  xAxis: {
    type: 'category',
    data: stepResults.value.map(step => `步骤${step.step_number}`)
  },
  yAxis: {
    type: 'value',
    name: '耗时(秒)',
    axisLabel: {
      formatter: '{value}s'
    }
  },
  series: [
    {
      name: '执行时间',
      type: 'line',
      data: stepResults.value.map(step => step.execution_time || 0),
      smooth: true,
      itemStyle: {
        color: '#409eff'
      },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ]
        }
      }
    }
  ]
}))

// HTTP状态码分布配置
const statusCodeChartOption = computed(() => {
  const statusCounts: Record<string, number> = {}

  stepResults.value.forEach(step => {
    const code = step.response_data?.status_code
    if (code) {
      const codeCategory = code < 200 ? '1xx' :
                        code < 300 ? '2xx' :
                        code < 400 ? '3xx' :
                        code < 500 ? '4xx' : '5xx'
      statusCounts[codeCategory] = (statusCounts[codeCategory] || 0) + 1
    }
  })

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    xAxis: {
      type: 'category',
      data: Object.keys(statusCounts).sort()
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '状态码数量',
        type: 'bar',
        data: Object.entries(statusCounts).sort(),
        itemStyle: {
          color: (params: any) => {
            const colors = ['#67c23a', '#e6a23c', '#f56c6c', '#409eff', '#909399']
            return colors[params.dataIndex % colors.length]
          }
        }
      }
    ]
  }
}))

// 响应时间分布配置
const responseTimeChartOption = computed(() => {
  const times = stepResults.value
    .filter(step => step.execution_time && step.execution_time > 0)
    .map(step => step.execution_time.toFixed(2))
    .sort((a: any, b: any) => parseFloat(a) - parseFloat(b))

  // 创建时间区间
  const ranges = ['0-0.5s', '0.5-1s', '1-2s', '2-5s', '>5s']
  const rangeCounts = [0, 0, 0, 0, 0]

  times.forEach(time => {
    const t = parseFloat(time)
    if (t <= 0.5) rangeCounts[0]++
    else if (t <= 1) rangeCounts[1]++
    else if (t <= 2) rangeCounts[2]++
    else if (t <= 5) rangeCounts[3]++
    else rangeCounts[4]++
  })

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    xAxis: {
      type: 'category',
      data: ranges
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '请求数量',
        type: 'bar',
        data: rangeCounts,
        itemStyle: {
          color: (params: any) => {
            const colors = ['#67c23a', '#409eff', '#e6a23c', '#f56c6c', '#909399']
            return colors[params.dataIndex % colors.length]
          }
        }
      }
    ]
  }
}))

// 获取状态码类型
const getStatusCodeType = (code: number) => {
  if (code < 200) return 'info'
  if (code < 300) return 'success'
  if (code < 400) return 'warning'
  if (code < 500) return 'danger'
  return 'danger'
}

// 显示步骤详情
const showStepDetail = (step: any) => {
  ElMessageBox.alert(
    `<div style="text-align: left;">
      <h4>步骤 ${step.step_number}: ${step.step_name}</h4>
      <p><strong>状态:</strong> <span class="el-tag el-tag--${getStepStatusType(step.status)}">${step.status}</span></p>
      <p><strong>执行时间:</strong> ${step.execution_time ? step.execution_time.toFixed(2) + 's' : '-'}</p>
      ${step.error_message ? `<p><strong>错误信息:</strong></p><pre style="background: #fef0f0; padding: 10px; border-radius: 4px; color: #f56c6c;">${step.error_message}</pre>` : ''}
      ${step.response_data ? `<p><strong>响应数据:</strong></p><pre style="background: #f5f7fa; padding: 10px; border-radius: 4px; max-height: 300px; overflow-y: auto;">${JSON.stringify(step.response_data, null, 2)}</pre>` : ''}
    </div>`,
    '步骤详情',
    {
      dangerouslyUseHTMLString: true,
      customClass: 'step-detail-dialog'
    }
  )
}

// 导出执行报告
const exportReport = async () => {
  if (!executionResult.value?.execution_id) {
    ElMessage.warning('没有可导出的执行记录')
    return
  }

  try {
    // 显示格式选择对话框
    const { value: format } = await ElMessageBox.prompt(
      '请输入导出格式 (json/pdf/excel)',
      '导出报告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /^(json|pdf|excel)$/,
        inputErrorMessage: '请输入有效的格式: json, pdf 或 excel',
        inputPlaceholder: '例如: json',
        inputValue: 'json'
      }
    )

    if (!format) return

    // 调用导出API
    const response = await executionAPI.exportExecutionReport(
      executionResult.value.execution_id,
      format as 'pdf' | 'excel' | 'json'
    )

    // 从响应头获取文件名，如果没有则生成默认文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = `execution-report-${executionResult.value.execution_id}.${format}`

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }

    // 创建下载链接
    const blob = new Blob([response.data], {
      type: response.headers['content-type'] || 'application/octet-stream'
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    ElMessage.success('报告导出成功')
  } catch (error: any) {
    if (error === 'cancel') {
      return // 用户取消选择
    }
    ElMessage.error(error.message || '报告导出失败')
  }
}

const handleExecute = async () => {
  executing.value = true
  logs.value = ''
  executionResult.value = null
  executionStatus.value = 'pending'
  executionDuration.value = 0

  try {
    // 解析context
    let context = {}
    if (contextJson.value.trim()) {
      try {
        context = JSON.parse(contextJson.value)
      } catch (e) {
        ElMessage.warning('全局变量格式错误,将使用空对象')
      }
    }

    // 发起执行请求
    const res = await store.executeCase(caseId.value, context)
    taskId.value = res.celery_task_id
    executionResult.value = { execution_id: res.execution_id }
    executionStatus.value = 'running'

    logs.value += `[INFO] 任务已创建: ${taskId.value}\n`
    logs.value += `[INFO] 执行记录ID: ${res.execution_id}\n`
    logs.value += `[INFO] 正在执行测试用例...\n\n`

    // 启动SSE日志流
    startLogStream()

    // 启动状态轮询
    startStatusCheck()
  } catch (error: any) {
    ElMessage.error(error.message || '执行失败')
    executionStatus.value = 'error'
    executing.value = false
  }
}

const startLogStream = () => {
  if (!taskId.value) return

  const url = executionAPI.getLogStreamUrl(taskId.value)
  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    if (data.log) {
      logs.value += data.log + '\n'
      scrollToBottom()
    }

    if (data.status) {
      executionStatus.value = data.status
    }
  }

  eventSource.onerror = () => {
    console.error('SSE connection error')
    eventSource?.close()
  }
}

const startStatusCheck = () => {
  statusCheckTimer = setInterval(async () => {
    if (!taskId.value) return

    try {
      const result = await store.getExecutionStatus(taskId.value)
      executionStatus.value = result.status
      executionDuration.value = result.duration || 0

      // 更新步骤信息
      if (result.step_results) {
        stepResults.value = result.step_results
        totalSteps.value = result.step_results.length
        currentStep.value = result.step_results.filter((step: any) =>
          ['success', 'failed', 'error'].includes(step.status)
        ).length
      }

      if (['success', 'failed', 'error'].includes(result.status)) {
        // 执行完成
        executionResult.value = {
          ...result,
          execution_id: result.execution_id || executionResult.value?.execution_id
        }
        executing.value = false
        stopStatusCheck()
        eventSource?.close()

        const statusMessage = result.status === 'success' ? '执行成功' : '执行失败'
        ElMessage({
          message: statusMessage,
          type: result.status === 'success' ? 'success' : 'error'
        })
      }
    } catch (error) {
      console.error('Status check error:', error)
    }
  }, 1500) // 更频繁的检查以获得更好的实时效果
}

const stopStatusCheck = () => {
  if (statusCheckTimer) {
    clearInterval(statusCheckTimer)
    statusCheckTimer = null
  }
}

const clearLogs = () => {
  logs.value = ''
}

const scrollToBottom = () => {
  if (!autoScroll.value) return

  nextTick(() => {
    if (logsContainerRef.value) {
      logsContainerRef.value.scrollTop = logsContainerRef.value.scrollHeight
    }
  })
}

const downloadLogs = () => {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `execution-logs-${caseId.value}-${timestamp}.txt`

  const content = [
    `执行日志 - ${currentCase.value?.name || '未知用例'}`,
    `用例ID: ${caseId.value}`,
    `执行时间: ${new Date().toLocaleString('zh-CN')}`,
    `执行状态: ${executionStatus.value}`,
    `执行耗时: ${executionDuration.value}s`,
    '',
    '=== 日志内容 ===',
    logs.value
  ].join('\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)

  ElMessage.success('日志下载成功')
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const goBack = () => {
  router.go(-1)
}

onMounted(async () => {
  try {
    currentCase.value = await store.fetchCaseById(caseId.value)
  } catch (error: any) {
    ElMessage.error(error.message || '加载用例失败')
    goBack()
  }
})

onUnmounted(() => {
  stopStatusCheck()
  eventSource?.close()
})
</script>

<style scoped lang="scss">
.execution-console-container {
  padding: 20px;

  .case-info-card,
  .execution-controls,
  .logs-card,
  .result-card {
    margin-top: 20px;

    h3, h4 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .execution-controls {
    .control-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
    }

    .context-config {
      h4 {
        font-size: 14px;
        margin-bottom: 12px;
      }
    }
  }

  .progress-card {
    .progress-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .progress-info {
        display: flex;
        gap: 12px;
        align-items: center;

        .duration {
          font-size: 14px;
          color: #666;
        }
      }
    }

    .progress-content {
      .step-progress {
        margin-top: 24px;

        h4 {
          margin: 0 0 16px 0;
          font-size: 16px;
          font-weight: 600;
        }

        .step-content {
          .step-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;

            .step-name {
              font-weight: 600;
              color: #303133;
            }
          }

          .step-error {
            margin-top: 8px;
          }

          .step-response {
            margin-top: 12px;
            .response-data {
              margin: 0;
              background: #f5f7fa;
              padding: 12px;
              border-radius: 4px;
              font-size: 12px;
              overflow-x: auto;
            }
          }
        }
      }
    }
  }

  .logs-card {
    .logs-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .logs-controls {
        display: flex;
        gap: 12px;
        align-items: center;
      }
    }

    .logs-container {
      max-height: 500px;
      overflow-y: auto;
      background: #1e1e1e;
      border-radius: 4px;
      padding: 16px;

      .logs-content {
        .log-line {
          font-family: 'Courier New', monospace;
          font-size: 13px;
          line-height: 1.6;
          margin: 2px 0;
          padding: 2px 4px;
          border-radius: 2px;

          &.log-success {
            color: #67c23a;
            background: rgba(103, 194, 58, 0.1);
          }

          &.log-error {
            color: #f56c6c;
            background: rgba(245, 108, 108, 0.1);
          }

          &.log-warning {
            color: #e6a23c;
            background: rgba(230, 162, 60, 0.1);
          }

          &.log-info {
            color: #909399;
            background: rgba(144, 147, 153, 0.1);
          }

          &.log-step {
            color: #409eff;
            background: rgba(64, 158, 255, 0.1);
            font-weight: 600;
          }

          &.log-separator {
            color: #606266;
            font-weight: 600;
            border-top: 1px solid #414243;
            border-bottom: 1px solid #414243;
            margin: 8px 0;
          }

          &.log-system {
            color: #909399;
            font-style: italic;
          }
        }
      }
    }
  }

  .charts-card {
    .charts-content {
      .chart-container {
        h4 {
          margin: 0 0 16px 0;
          font-size: 16px;
          font-weight: 600;
          color: #303133;
        }
      }
    }
  }

  .result-card {
    .result-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .result-actions {
        display: flex;
        gap: 12px;
      }
    }

    pre {
      margin: 0;
      background: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      font-size: 12px;
      overflow-x: auto;
    }
  }
}

// 步骤详情对话框样式
:global(.step-detail-dialog) {
  .el-message-box {
    max-width: 800px;

    .el-message-box__content {
      max-height: 600px;
      overflow-y: auto;
    }

    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
}
</style>

