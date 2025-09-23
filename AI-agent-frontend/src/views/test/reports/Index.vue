<!-- 测试报告详情页面 -->
<template>
  <div class="test-report-detail">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>
              <router-link to="/test/reports">测试报告</router-link>
            </el-breadcrumb-item>
            <el-breadcrumb-item>报告详情</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="title-section">
          <h1>{{ reportDetail?.title || '报告详情' }}</h1>
          <div class="report-meta">
            <el-tag :type="testReportUtils.formatStatus(reportDetail?.status || '').type">
              {{ testReportUtils.formatStatus(reportDetail?.status || '').text }}
            </el-tag>
            <el-tag type="info">{{ testReportUtils.formatTestType(reportDetail?.test_type || '').text }}</el-tag>
            <span class="create-time">{{ formatDateTime(reportDetail?.created_at) }}</span>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport" :loading="exporting">
          <el-icon><Download /></el-icon>
          导出报告
        </el-button>
        <el-button 
          v-if="reportDetail?.status === 'completed' || reportDetail?.status === 'failed'"
          type="primary" 
          @click="handleRerun"
          :loading="rerunning"
        >
          <el-icon><Refresh /></el-icon>
          重新运行
        </el-button>
        <el-button 
          v-if="reportDetail?.status === 'running'"
          type="danger" 
          @click="handleStop"
          :loading="stopping"
        >
          <el-icon><Close /></el-icon>
          停止执行
        </el-button>
      </div>
    </div>

    <!-- 报告概览 -->
    <div class="report-overview" v-loading="loading">
      <el-row :gutter="24">
        <!-- 执行统计 -->
        <el-col :span="18">
          <el-card class="overview-card">
            <template #header>
              <h3>执行概览</h3>
            </template>
            
            <div class="overview-content">
              <div class="stats-grid">
                <div class="stat-item total">
                  <div class="stat-icon">
                    <el-icon><Document /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ reportDetail?.total_cases || 0 }}</div>
                    <div class="stat-label">总用例数</div>
                  </div>
                </div>
                
                <div class="stat-item passed">
                  <div class="stat-icon">
                    <el-icon><SuccessFilled /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ reportDetail?.passed_cases || 0 }}</div>
                    <div class="stat-label">通过</div>
                  </div>
                </div>
                
                <div class="stat-item failed">
                  <div class="stat-icon">
                    <el-icon><CircleCloseFilled /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ reportDetail?.failed_cases || 0 }}</div>
                    <div class="stat-label">失败</div>
                  </div>
                </div>
                
                <div class="stat-item skipped">
                  <div class="stat-icon">
                    <el-icon><WarningFilled /></el-icon>
                  </div>
                  <div class="stat-content">
                    <div class="stat-number">{{ reportDetail?.skipped_cases || 0 }}</div>
                    <div class="stat-label">跳过</div>
                  </div>
                </div>
              </div>
              
              <div class="success-rate-section">
                <div class="rate-display">
                  <el-progress 
                    type="circle" 
                    :percentage="reportDetail?.success_rate || 0"
                    :width="120"
                    :stroke-width="8"
                    :color="getSuccessRateColor(reportDetail?.success_rate || 0)"
                  >
                    <template #default="{ percentage }">
                      <span class="rate-text">{{ percentage }}%</span>
                    </template>
                  </el-progress>
                </div>
                <div class="rate-info">
                  <h4>成功率</h4>
                  <p>执行时间: {{ testReportUtils.formatDuration(reportDetail?.execution_time || 0) }}</p>
                  <p>开始时间: {{ formatDateTime(reportDetail?.start_time) }}</p>
                  <p v-if="reportDetail?.end_time">结束时间: {{ formatDateTime(reportDetail.end_time) }}</p>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 快速信息 -->
        <el-col :span="6">
          <el-card class="info-card">
            <template #header>
              <h3>基本信息</h3>
            </template>
            
            <div class="info-content">
              <div class="info-item">
                <span class="label">报告ID:</span>
                <span class="value">{{ reportDetail?.id }}</span>
              </div>
              
              <div class="info-item">
                <span class="label">优先级:</span>
                <el-tag 
                  v-if="reportDetail?.priority"
                  :type="testReportUtils.formatPriority(reportDetail.priority).type" 
                  size="small"
                >
                  {{ testReportUtils.formatPriority(reportDetail.priority).text }}
                </el-tag>
              </div>
              
              <div class="info-item">
                <span class="label">执行代理:</span>
                <span class="value">{{ reportDetail?.agent_name || '系统默认' }}</span>
              </div>
              
              <div class="info-item">
                <span class="label">创建人:</span>
                <span class="value">{{ reportDetail?.creator_name || '-' }}</span>
              </div>
              
              <div v-if="reportDetail?.description" class="info-item description">
                <span class="label">描述:</span>
                <p class="value">{{ reportDetail.description }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 详细内容 -->
    <div class="report-content">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <!-- 测试结果 -->
        <el-tab-pane label="测试结果" name="results">
          <div class="results-content">
            <!-- 结果筛选 -->
            <div class="results-filter">
              <el-row :gutter="16">
                <el-col :span="6">
          <el-input
                    v-model="resultFilter.keyword"
                    placeholder="搜索用例名称"
            clearable
                    @clear="loadTestResults"
                    @keyup.enter="loadTestResults"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-col>
                <el-col :span="4">
                  <el-select v-model="resultFilter.status" placeholder="状态" clearable @change="loadTestResults">
            <el-option label="通过" value="passed" />
            <el-option label="失败" value="failed" />
                    <el-option label="跳过" value="skipped" />
                    <el-option label="错误" value="error" />
          </el-select>
                </el-col>
                <el-col :span="6">
                  <el-select v-model="resultFilter.sort" placeholder="排序方式" @change="loadTestResults">
                    <el-option label="执行时间 (升序)" value="execution_time_asc" />
                    <el-option label="执行时间 (降序)" value="execution_time_desc" />
                    <el-option label="用例名称 (A-Z)" value="name_asc" />
                    <el-option label="用例名称 (Z-A)" value="name_desc" />
                  </el-select>
                </el-col>
                <el-col :span="8">
                  <el-button type="primary" @click="loadTestResults">搜索</el-button>
                  <el-button @click="resetResultFilter">重置</el-button>
                </el-col>
              </el-row>
    </div>

            <!-- 结果列表 -->
      <el-table
              :data="testResults" 
              v-loading="resultsLoading"
              @row-click="viewResultDetail"
              class="results-table"
            >
              <el-table-column prop="test_case_name" label="用例名称" min-width="200" />
              <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
                  <el-tag :type="getResultStatusType(row.status)">
                    {{ getResultStatusText(row.status) }}
                  </el-tag>
          </template>
        </el-table-column>
              <el-table-column prop="execution_time" label="执行时间" width="120">
          <template #default="{ row }">
                  {{ testReportUtils.formatDuration(row.execution_time) }}
          </template>
        </el-table-column>
              <el-table-column label="性能指标" width="150">
          <template #default="{ row }">
                  <div v-if="row.metrics" class="metrics-info">
                    <div v-if="row.metrics.response_time">
                      响应: {{ row.metrics.response_time }}ms
                    </div>
                    <div v-if="row.metrics.memory_usage">
                      内存: {{ (row.metrics.memory_usage / 1024 / 1024).toFixed(1) }}MB
                    </div>
                  </div>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="start_time" label="开始时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.start_time) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="viewResultDetail(row)">
                    详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
            <div class="results-pagination">
        <el-pagination
                v-model:current-page="resultPagination.page"
                v-model:page-size="resultPagination.page_size"
                :total="resultPagination.total"
                layout="total, sizes, prev, pager, next"
                @size-change="loadTestResults"
                @current-change="loadTestResults"
        />
      </div>
    </div>
        </el-tab-pane>
        
        <!-- 性能指标 -->
        <el-tab-pane label="性能指标" name="metrics" v-if="reportDetail?.test_type === 'performance'">
          <div class="metrics-content" v-loading="metricsLoading">
            <el-row :gutter="24" v-if="performanceMetrics">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <h3>响应时间统计</h3>
                  </template>
                  <div class="metric-grid">
                    <div class="metric-item">
                      <span class="metric-label">最小值:</span>
                      <span class="metric-value">{{ performanceMetrics.response_times.min }}ms</span>
  </div>
                    <div class="metric-item">
                      <span class="metric-label">最大值:</span>
                      <span class="metric-value">{{ performanceMetrics.response_times.max }}ms</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">平均值:</span>
                      <span class="metric-value">{{ performanceMetrics.response_times.avg }}ms</span>
                    </div>
                    <div class="metric-item">
                      <span class="metric-label">P95:</span>
                      <span class="metric-value">{{ performanceMetrics.response_times.p95 }}ms</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <h3>资源使用率</h3>
                  </template>
                  <div class="resource-usage">
                    <div class="usage-item">
                      <span class="usage-label">CPU使用率:</span>
                      <el-progress 
                        :percentage="performanceMetrics.resource_usage.cpu_usage" 
                        :color="getUsageColor(performanceMetrics.resource_usage.cpu_usage)"
                      />
                    </div>
                    <div class="usage-item">
                      <span class="usage-label">内存使用率:</span>
                      <el-progress 
                        :percentage="performanceMetrics.resource_usage.memory_usage"
                        :color="getUsageColor(performanceMetrics.resource_usage.memory_usage)"
                      />
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
        
        <!-- 错误日志 -->
        <el-tab-pane label="错误日志" name="logs">
          <div class="logs-content" v-loading="logsLoading">
            <!-- 日志筛选 -->
            <div class="logs-filter">
              <el-row :gutter="16">
                <el-col :span="4">
                  <el-select v-model="logFilter.level" placeholder="日志级别" clearable @change="loadErrorLogs">
                    <el-option label="错误" value="error" />
                    <el-option label="警告" value="warning" />
                    <el-option label="信息" value="info" />
                    <el-option label="调试" value="debug" />
                  </el-select>
                </el-col>
                <el-col :span="6">
                  <el-input
                    v-model="logFilter.keyword"
                    placeholder="搜索日志内容"
                    clearable
                    @clear="loadErrorLogs"
                    @keyup.enter="loadErrorLogs"
                  >
                    <template #prefix>
                      <el-icon><Search /></el-icon>
                    </template>
                  </el-input>
                </el-col>
                <el-col :span="6">
                  <el-button type="primary" @click="loadErrorLogs">搜索</el-button>
                  <el-button @click="resetLogFilter">重置</el-button>
                </el-col>
              </el-row>
            </div>
            
            <!-- 日志列表 -->
            <div class="logs-list">
              <div v-if="errorLogs.length === 0" class="empty-logs">
                <el-empty description="暂无错误日志" />
              </div>
              
              <div v-else>
                <div 
                  v-for="log in errorLogs" 
                  :key="log.id" 
                  class="log-item"
                  :class="log.level"
                >
                  <div class="log-header">
                    <el-tag :type="getLogLevelType(log.level)" size="small">
                      {{ log.level.toUpperCase() }}
                    </el-tag>
                    <span class="log-time">{{ formatDateTime(log.timestamp) }}</span>
                    <span class="log-source">{{ log.source }}</span>
                  </div>
                  
                  <div class="log-content">
                    <p class="log-message">{{ log.message }}</p>
                    
                    <div v-if="log.stack_trace" class="log-stack">
                      <el-collapse>
                        <el-collapse-item title="查看堆栈信息">
                          <pre class="stack-trace">{{ log.stack_trace }}</pre>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                    
                    <div v-if="log.context" class="log-context">
                      <el-collapse>
                        <el-collapse-item title="上下文信息">
                          <pre class="context-info">{{ JSON.stringify(log.context, null, 2) }}</pre>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 日志分页 -->
            <div class="logs-pagination">
              <el-pagination
                v-model:current-page="logPagination.page"
                v-model:page-size="logPagination.page_size"
                :total="logPagination.total"
                layout="total, sizes, prev, pager, next"
                @size-change="loadErrorLogs"
                @current-change="loadErrorLogs"
              />
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 附件 -->
        <el-tab-pane label="附件" name="attachments">
          <div class="attachments-content" v-loading="attachmentsLoading">
            <!-- 上传区域 -->
            <div class="upload-section">
              <el-upload
                ref="uploadRef"
                :action="uploadUrl"
                :headers="uploadHeaders"
                :on-success="handleUploadSuccess"
                :on-error="handleUploadError"
                :before-upload="beforeUpload"
                drag
                multiple
              >
                <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖拽到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">
                    支持 jpg/png/pdf/txt 等格式，单个文件不超过 10MB
                  </div>
                </template>
              </el-upload>
            </div>
            
            <!-- 附件列表 -->
            <div class="attachments-list">
              <div v-if="attachments.length === 0" class="empty-attachments">
                <el-empty description="暂无附件" />
              </div>
              
              <div v-else class="attachment-grid">
                <div 
                  v-for="attachment in attachments" 
                  :key="attachment.id" 
                  class="attachment-item"
                >
                  <div class="attachment-icon">
                    <el-icon>
                      <component :is="getAttachmentIcon(attachment.type)" />
                    </el-icon>
                  </div>
                  
                  <div class="attachment-info">
                    <div class="attachment-name">{{ attachment.name }}</div>
                    <div class="attachment-meta">
                      <span class="file-size">{{ testReportUtils.formatFileSize(attachment.size) }}</span>
                      <span class="upload-time">{{ formatDateTime(attachment.created_at) }}</span>
                    </div>
                  </div>
                  
                  <div class="attachment-actions">
                    <el-button size="small" @click="downloadAttachment(attachment)">
                      <el-icon><Download /></el-icon>
                    </el-button>
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="deleteAttachment(attachment)"
                    >
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <!-- 测试结果详情对话框 -->
    <el-dialog
      v-model="showResultDetail"
      title="测试结果详情"
      width="80%"
      :close-on-click-modal="false"
    >
      <div v-if="currentResult" class="result-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="用例名称">
              {{ currentResult.test_case_name }}
            </el-descriptions-item>
            <el-descriptions-item label="执行状态">
              <el-tag :type="getResultStatusType(currentResult.status)">
                {{ getResultStatusText(currentResult.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="开始时间">
              {{ formatDateTime(currentResult.start_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="结束时间">
              {{ formatDateTime(currentResult.end_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="执行时长">
              {{ testReportUtils.formatDuration(currentResult.execution_time) }}
            </el-descriptions-item>
            <el-descriptions-item label="性能指标" v-if="currentResult.metrics">
              响应时间: {{ currentResult.metrics.response_time || 0 }}ms
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- 错误信息 -->
        <div v-if="currentResult.error_message" class="detail-section">
          <h4>错误信息</h4>
          <el-alert type="error" :closable="false">
            <template #title>
              {{ currentResult.error_message }}
            </template>
            <pre v-if="currentResult.stack_trace" class="stack-trace">{{ currentResult.stack_trace }}</pre>
          </el-alert>
        </div>
        
        <!-- 执行步骤 -->
        <div v-if="currentResult.steps" class="detail-section">
          <h4>执行步骤</h4>
          <el-timeline>
            <el-timeline-item
              v-for="step in currentResult.steps"
              :key="step.step_number"
              :type="getStepStatusType(step.status)"
            >
              <div class="step-content">
                <div class="step-header">
                  <span class="step-number">步骤 {{ step.step_number }}</span>
                  <el-tag :type="getStepStatusType(step.status)" size="small">
                    {{ getStepStatusText(step.status) }}
                  </el-tag>
                </div>
                <p class="step-description">{{ step.description }}</p>
                <div v-if="step.error_message" class="step-error">
                  <el-text type="danger">{{ step.error_message }}</el-text>
                </div>
                <div v-if="step.screenshot" class="step-screenshot">
                  <el-image 
                    :src="step.screenshot" 
                    :preview-src-list="[step.screenshot]"
                    style="width: 200px; height: 150px"
                    fit="cover"
                  />
                </div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
        
        <!-- 截图 -->
        <div v-if="currentResult.screenshots && currentResult.screenshots.length" class="detail-section">
          <h4>截图</h4>
          <div class="screenshots-grid">
            <el-image
              v-for="(screenshot, index) in currentResult.screenshots"
              :key="index"
              :src="screenshot"
              :preview-src-list="currentResult.screenshots"
              style="width: 200px; height: 150px"
              fit="cover"
            />
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download,
  Refresh,
  Close,
  Document,
  SuccessFilled,
  CircleCloseFilled,
  WarningFilled,
  Search,
  UploadFilled,
  Delete
} from '@element-plus/icons-vue'
import { testReportApi, testReportUtils, type TestReportDetail, type TestCaseResult, type PerformanceMetrics, type ErrorLog } from '@/api/modules/testreport'
import { formatDateTime } from '@/utils/dateFormat'
import { getToken } from '@/utils/auth'

const route = useRoute()
const router = useRouter()

// 响应式数据
const loading = ref(true)
const exporting = ref(false)
const rerunning = ref(false)
const stopping = ref(false)
const resultsLoading = ref(false)
const metricsLoading = ref(false)
const logsLoading = ref(false)
const attachmentsLoading = ref(false)

const reportDetail = ref<TestReportDetail | null>(null)
const testResults = ref<TestCaseResult[]>([])
const performanceMetrics = ref<PerformanceMetrics | null>(null)
const errorLogs = ref<ErrorLog[]>([])
const attachments = ref([])

const activeTab = ref('results')
const showResultDetail = ref(false)
const currentResult = ref<TestCaseResult | null>(null)

// 筛选条件
const resultFilter = reactive({
  keyword: '',
  status: '',
  sort: 'execution_time_desc'
})

const logFilter = reactive({
  level: '',
  keyword: ''
})

// 分页
const resultPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const logPagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 上传配置
const uploadRef = ref()
const uploadUrl = computed(() => `/api/v1/test-reports/${reportId.value}/attachments`)
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${getToken()}`
}))

// 计算属性
const reportId = computed(() => {
  return Number(route.params.id)
})

// 生命周期
onMounted(() => {
  loadReportDetail()
})

// 方法定义
const loadReportDetail = async () => {
  if (!reportId.value) return
  
  loading.value = true
  try {
    const response = await testReportApi.getTestReportDetail(reportId.value)
    if (response.data.success) {
      reportDetail.value = response.data.data
      
      // 根据测试类型加载相应的数据
      if (activeTab.value === 'results') {
        loadTestResults()
      } else if (activeTab.value === 'metrics' && reportDetail.value.test_type === 'performance') {
        loadPerformanceMetrics()
      } else if (activeTab.value === 'logs') {
        loadErrorLogs()
      } else if (activeTab.value === 'attachments') {
        loadAttachments()
      }
    }
  } catch (error) {
    console.error('加载报告详情失败:', error)
    ElMessage.error('加载报告详情失败')
  } finally {
    loading.value = false
  }
}

const loadTestResults = async () => {
  if (!reportId.value) return
  
  resultsLoading.value = true
  try {
    // 这里需要根据实际API调整
    const params = {
      ...resultPagination,
      ...resultFilter
    }
    
    // 从报告详情中获取测试结果
    if (reportDetail.value?.test_results) {
      let results = [...reportDetail.value.test_results]
      
      // 应用筛选
      if (resultFilter.keyword) {
        results = results.filter(r => 
          r.test_case_name.toLowerCase().includes(resultFilter.keyword.toLowerCase())
        )
      }
      
      if (resultFilter.status) {
        results = results.filter(r => r.status === resultFilter.status)
      }
      
      // 应用排序
      if (resultFilter.sort) {
        const [field, order] = resultFilter.sort.split('_')
        results.sort((a, b) => {
          let aVal = a[field as keyof TestCaseResult]
          let bVal = b[field as keyof TestCaseResult]
          
          if (field === 'name') {
            aVal = a.test_case_name
            bVal = b.test_case_name
          }
          
          if (typeof aVal === 'string' && typeof bVal === 'string') {
            return order === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
          } else {
            return order === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
          }
        })
      }
      
      // 应用分页
      const start = (resultPagination.page - 1) * resultPagination.page_size
      const end = start + resultPagination.page_size
      
      testResults.value = results.slice(start, end)
      resultPagination.total = results.length
    }
  } catch (error) {
    console.error('加载测试结果失败:', error)
    ElMessage.error('加载测试结果失败')
  } finally {
    resultsLoading.value = false
  }
}

const loadPerformanceMetrics = async () => {
  if (!reportId.value) return
  
  metricsLoading.value = true
  try {
    const response = await testReportApi.getReportMetrics(reportId.value)
    if (response.data.success) {
      performanceMetrics.value = response.data.data
    }
  } catch (error) {
    console.error('加载性能指标失败:', error)
    ElMessage.error('加载性能指标失败')
  } finally {
    metricsLoading.value = false
  }
}

const loadErrorLogs = async () => {
  if (!reportId.value) return
  
  logsLoading.value = true
  try {
    const params = {
      ...logPagination,
      ...logFilter
    }
    const response = await testReportApi.getReportLogs(reportId.value, params)
    if (response.data.success) {
      errorLogs.value = response.data.data.logs
      logPagination.total = response.data.data.total
    }
  } catch (error) {
    console.error('加载错误日志失败:', error)
    ElMessage.error('加载错误日志失败')
  } finally {
    logsLoading.value = false
  }
}

const loadAttachments = async () => {
  if (!reportId.value) return
  
  attachmentsLoading.value = true
  try {
    const response = await testReportApi.getReportAttachments(reportId.value)
    if (response.data.success) {
      attachments.value = response.data.data
    }
  } catch (error) {
    console.error('加载附件失败:', error)
    ElMessage.error('加载附件失败')
  } finally {
    attachmentsLoading.value = false
  }
}

const handleTabChange = (tabName: string) => {
  activeTab.value = tabName
  
  switch (tabName) {
    case 'results':
      loadTestResults()
      break
    case 'metrics':
      if (reportDetail.value?.test_type === 'performance') {
        loadPerformanceMetrics()
      }
      break
    case 'logs':
      loadErrorLogs()
      break
    case 'attachments':
      loadAttachments()
      break
  }
}

const handleExport = async () => {
  if (!reportId.value) return
  
  exporting.value = true
  try {
    const blob = await testReportApi.exportReport(reportId.value, {
      format: 'pdf',
      include_screenshots: true,
      include_logs: true,
      include_metrics: true
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = testReportUtils.generateExportFileName(reportDetail.value!, 'pdf')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('报告导出成功')
  } catch (error) {
    console.error('导出报告失败:', error)
    ElMessage.error('导出报告失败')
  } finally {
    exporting.value = false
  }
}

const handleRerun = async () => {
  if (!reportId.value) return
  
  try {
    await ElMessageBox.confirm(
      '确定要重新运行此测试报告吗？',
      '确认重跑',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      type: 'warning'
      }
    )
    
    rerunning.value = true
    const response = await testReportApi.rerunReport(reportId.value)
    if (response.data.success) {
      ElMessage.success('报告重跑已启动')
      loadReportDetail()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('重跑报告失败:', error)
      ElMessage.error('重跑报告失败')
    }
  } finally {
    rerunning.value = false
  }
}

const handleStop = async () => {
  if (!reportId.value) return
  
  try {
    await ElMessageBox.confirm(
      '确定要停止此测试报告的执行吗？',
      '确认停止',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
      type: 'warning'
      }
    )
    
    stopping.value = true
    const response = await testReportApi.stopExecution(reportId.value)
    if (response.data.success) {
      ElMessage.success('已停止执行')
      loadReportDetail()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止执行失败:', error)
      ElMessage.error('停止执行失败')
    }
  } finally {
    stopping.value = false
  }
}

const resetResultFilter = () => {
  Object.assign(resultFilter, {
    keyword: '',
    status: '',
    sort: 'execution_time_desc'
  })
  loadTestResults()
}

const resetLogFilter = () => {
  Object.assign(logFilter, {
    level: '',
    keyword: ''
  })
  loadErrorLogs()
}

const viewResultDetail = (result: TestCaseResult) => {
  currentResult.value = result
  showResultDetail.value = true
}

// 工具方法
const getSuccessRateColor = (rate: number) => {
  if (rate >= 90) return '#67c23a'
  if (rate >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getUsageColor = (usage: number) => {
  if (usage >= 80) return '#f56c6c'
  if (usage >= 60) return '#e6a23c'
  return '#67c23a'
}

const getResultStatusType = (status: string) => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    skipped: 'warning',
    error: 'danger'
  }
  return typeMap[status as keyof typeof typeMap] || 'info'
}

const getResultStatusText = (status: string) => {
  const textMap = {
    passed: '通过',
    failed: '失败',
    skipped: '跳过',
    error: '错误'
  }
  return textMap[status as keyof typeof textMap] || status
}

const getLogLevelType = (level: string) => {
  const typeMap = {
    error: 'danger',
    warning: 'warning',
    info: 'primary',
    debug: 'info'
  }
  return typeMap[level as keyof typeof typeMap] || 'info'
}

const getStepStatusType = (status: string) => {
  const typeMap = {
    passed: 'success',
    failed: 'danger',
    skipped: 'warning'
  }
  return typeMap[status as keyof typeof typeMap] || 'primary'
}

const getStepStatusText = (status: string) => {
  const textMap = {
    passed: '通过',
    failed: '失败',
    skipped: '跳过'
  }
  return textMap[status as keyof typeof textMap] || status
}

const getAttachmentIcon = (type: string) => {
  const iconMap = {
    screenshot: 'Picture',
    video: 'VideoPlay',
    log: 'Document',
    report: 'Document',
    other: 'Document'
  }
  return iconMap[type as keyof typeof iconMap] || 'Document'
}

// 上传相关方法
const beforeUpload = (file: File) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB!')
  }
  return isLt10M
}

const handleUploadSuccess = (response: any) => {
  ElMessage.success('文件上传成功')
  loadAttachments()
}

const handleUploadError = () => {
  ElMessage.error('文件上传失败')
}

const downloadAttachment = (attachment: any) => {
  window.open(attachment.url, '_blank')
}

const deleteAttachment = async (attachment: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除附件"${attachment.name}"吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await testReportApi.deleteAttachment(reportId.value, attachment.id)
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadAttachments()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除附件失败:', error)
      ElMessage.error('删除附件失败')
    }
  }
}
</script>

<style scoped lang="scss">
.test-report-detail {
  padding: 20px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
    
    .header-content {
      .breadcrumb {
        margin-bottom: 8px;
      }
      
      .title-section {
        h1 {
      margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          color: #1f2329;
        }
        
        .report-meta {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .create-time {
            font-size: 14px;
            color: #646a73;
          }
        }
      }
    }
    
    .header-actions {
      display: flex;
      gap: 12px;
    }
  }
  
  .report-overview {
    margin-bottom: 24px;
    
    .overview-card {
      .overview-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        .stats-grid {
          display: flex;
          gap: 24px;
          
          .stat-item {
            display: flex;
            align-items: center;
            gap: 12px;
            
            .stat-icon {
              width: 48px;
              height: 48px;
              border-radius: 8px;
              display: flex;
              align-items: center;
              justify-content: center;
              font-size: 24px;
              
              &.total {
                background: #e6f4ff;
                color: #1890ff;
              }
              
              &.passed {
                background: #f6ffed;
                color: #52c41a;
              }
              
              &.failed {
                background: #fff2f0;
                color: #ff4d4f;
              }
              
              &.skipped {
                background: #fff7e6;
                color: #fa8c16;
              }
            }
            
            .stat-content {
              .stat-number {
                font-size: 24px;
                font-weight: 600;
                color: #1f2329;
                line-height: 1;
              }
              
              .stat-label {
                font-size: 14px;
                color: #646a73;
                margin-top: 4px;
              }
            }
          }
        }
        
        .success-rate-section {
          display: flex;
          align-items: center;
          gap: 24px;
          
          .rate-display {
            .rate-text {
              font-size: 18px;
              font-weight: 600;
            }
          }
          
          .rate-info {
            h4 {
              margin: 0 0 8px 0;
              font-size: 16px;
              font-weight: 600;
            }
            
            p {
              margin: 4px 0;
      font-size: 14px;
              color: #646a73;
            }
          }
        }
      }
    }
    
    .info-card {
      .info-content {
        .info-item {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 8px 0;
          border-bottom: 1px solid #f0f0f0;
          
          &:last-child {
            border-bottom: none;
          }
          
          &.description {
            flex-direction: column;
            align-items: flex-start;
            
            .value {
              margin-top: 4px;
              line-height: 1.5;
            }
          }
          
          .label {
            font-size: 14px;
            color: #646a73;
            min-width: 80px;
          }
          
          .value {
            font-size: 14px;
            color: #1f2329;
            font-weight: 500;
            text-align: right;
            flex: 1;
          }
        }
      }
    }
  }
  
  .report-content {
    .results-content {
      .results-filter {
        background: white;
    padding: 20px;
        border-radius: 8px;
        margin-bottom: 16px;
      }
      
      .results-table {
        .metrics-info {
          font-size: 12px;
          line-height: 1.4;
        }
      }
      
      .results-pagination {
        display: flex;
        justify-content: center;
        margin-top: 20px;
      }
    }
    
    .metrics-content {
      .metric-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        
        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #f0f0f0;
          
          &:last-child {
            border-bottom: none;
          }
          
          .metric-label {
            font-size: 14px;
            color: #646a73;
          }
          
          .metric-value {
            font-size: 16px;
            color: #1f2329;
            font-weight: 600;
          }
        }
      }
      
      .resource-usage {
        .usage-item {
          margin-bottom: 16px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .usage-label {
            display: inline-block;
            font-size: 14px;
            color: #646a73;
            margin-bottom: 8px;
            min-width: 100px;
          }
        }
      }
    }
    
    .logs-content {
      .logs-filter {
        background: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 16px;
      }
      
      .logs-list {
        .empty-logs {
          text-align: center;
          padding: 40px;
        }
        
        .log-item {
          background: white;
          border: 1px solid #f0f0f0;
          border-radius: 8px;
          margin-bottom: 12px;
          padding: 16px;
          
          &.error {
            border-left: 4px solid #f56c6c;
          }
          
          &.warning {
            border-left: 4px solid #e6a23c;
          }
          
          .log-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 8px;
            
            .log-time {
              font-size: 12px;
              color: #909399;
            }
            
            .log-source {
              font-size: 12px;
              color: #606266;
              background: #f5f7fa;
              padding: 2px 6px;
    border-radius: 4px;
            }
          }
          
          .log-content {
            .log-message {
              margin: 0 0 8px 0;
              font-size: 14px;
              line-height: 1.5;
            }
            
            .log-stack,
            .log-context {
              margin-top: 8px;
              
              .stack-trace,
              .context-info {
                margin: 0;
                padding: 12px;
                background: #f5f7fa;
    border-radius: 4px;
                font-size: 12px;
                line-height: 1.4;
                overflow-x: auto;
              }
            }
          }
        }
      }
      
      .logs-pagination {
        display: flex;
        justify-content: center;
        margin-top: 20px;
      }
    }
    
    .attachments-content {
      .upload-section {
        margin-bottom: 24px;
      }
      
      .attachments-list {
        .empty-attachments {
          text-align: center;
          padding: 40px;
        }
        
        .attachment-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 16px;
          
          .attachment-item {
            display: flex;
            align-items: center;
            padding: 16px;
            background: white;
            border: 1px solid #f0f0f0;
            border-radius: 8px;
            
            .attachment-icon {
              width: 40px;
              height: 40px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: #f5f7fa;
              border-radius: 6px;
              margin-right: 12px;
              font-size: 20px;
              color: #606266;
            }
            
            .attachment-info {
              flex: 1;
              
              .attachment-name {
                font-size: 14px;
                color: #1f2329;
                font-weight: 500;
                margin-bottom: 4px;
              }
              
              .attachment-meta {
                font-size: 12px;
                color: #909399;
                
                .file-size {
                  margin-right: 12px;
                }
              }
            }
            
            .attachment-actions {
              display: flex;
              gap: 8px;
            }
          }
        }
      }
    }
  }
  
  .result-detail {
    .detail-section {
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: #1f2329;
      }
      
      .step-content {
        .step-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          
          .step-number {
            font-weight: 500;
          }
        }
        
        .step-description {
          margin: 0 0 8px 0;
          font-size: 14px;
          line-height: 1.5;
        }
        
        .step-error {
          margin-bottom: 8px;
        }
        
        .step-screenshot {
          margin-top: 8px;
        }
      }
      
      .screenshots-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
      }
      
      .stack-trace {
        margin: 8px 0 0 0;
        padding: 12px;
        background: #f5f7fa;
        border-radius: 4px;
        font-size: 12px;
        line-height: 1.4;
        overflow-x: auto;
      }
    }
  }
}
</style>