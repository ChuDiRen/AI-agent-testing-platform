<template>
  <div class="batch-execution-container">
    <el-page-header @back="goBack">
      <template #content>
        <span>批量执行</span>
      </template>
    </el-page-header>

    <el-row :gutter="20">
      <!-- 左侧：用例选择 -->
      <el-col :span="14">
        <el-card class="case-selection-card">
          <template #header>
            <div class="card-header">
              <h3>选择测试用例</h3>
              <div class="selection-actions">
                <el-button size="small" @click="selectAllCases">全选</el-button>
                <el-button size="small" @click="clearSelection">清空</el-button>
                <span v-if="selectedCases.length > 0" class="selection-count">
                  已选择 {{ selectedCases.length }} 个用例
                </span>
              </div>
            </div>
          </template>

          <div class="filter-bar">
            <el-select v-model="filters.suite_id" placeholder="选择套件" clearable style="width: 200px">
              <el-option
                v-for="suite in store.suites"
                :key="suite.suite_id"
                :label="suite.name"
                :value="suite.suite_id"
              />
            </el-select>
            <el-input
              v-model="filters.keyword"
              placeholder="搜索用例名称"
              style="width: 200px"
              clearable
            />
            <el-select v-model="filters.status" placeholder="用例状态" clearable style="width: 120px">
              <el-option label="草稿" value="draft" />
              <el-option label="激活" value="active" />
              <el-option label="已弃用" value="deprecated" />
            </el-select>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </div>

          <div class="case-list">
            <el-table
              ref="caseTableRef"
              :data="store.cases"
              row-key="case_id"
              @selection-change="handleSelectionChange"
              max-height="500"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="case_id" label="ID" width="60" />
              <el-table-column label="用例名称" min-width="200">
                <template #default="{ row }">
                  <div class="case-name">
                    {{ row.name }}
                    <el-tag v-if="row.priority" size="small" :type="getPriorityType(row.priority)">
                      {{ row.priority }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="套件" width="150">
                <template #default="{ row }">
                  {{ getSuiteName(row.suite_id) }}
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="80">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)" size="small">
                    {{ getStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="配置模式" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.config_mode === 'form' ? 'success' : 'info'" size="small">
                    {{ row.config_mode === 'form' ? '表单' : 'YAML' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination">
              <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.page_size"
                :total="store.casesTotal"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSearch"
                @current-change="handleSearch"
              />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：执行配置和监控 -->
      <el-col :span="10">
        <el-card class="execution-config-card">
          <template #header>
            <h3>执行配置</h3>
          </template>

          <el-form ref="configFormRef" :model="executionConfig" label-width="100px">
            <el-form-item label="执行模式">
              <el-radio-group v-model="executionConfig.execution_mode">
                <el-radio label="parallel">并行执行</el-radio>
                <el-radio label="sequential">顺序执行</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="并发数量" v-if="executionConfig.execution_mode === 'parallel'">
              <el-input-number
                v-model="executionConfig.max_concurrent"
                :min="1"
                :max="20"
                placeholder="最大并发数"
              />
            </el-form-item>

            <el-form-item label="全局变量">
              <el-input
                v-model="contextJson"
                type="textarea"
                :rows="4"
                placeholder='{"key": "value"}'
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="executing"
                :disabled="selectedCases.length === 0"
                @click="handleBatchExecute"
              >
                <el-icon><VideoPlay /></el-icon>
                {{ executing ? '执行中...' : '开始批量执行' }}
              </el-button>
              <el-button @click="clearResults" :disabled="!batchResults">
                清空结果
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 执行结果 -->
        <el-card class="execution-results-card" v-if="batchResults || executing">
          <template #header>
            <div class="results-header">
              <h3>执行结果</h3>
              <el-tag :type="getBatchStatusType(batchResults?.overall_status)">
                {{ batchResults?.overall_status || '执行中' }}
              </el-tag>
            </div>
          </template>

          <div v-if="executing && !batchResults" class="executing-info">
            <el-progress :percentage="0" status="active" :duration="5" />
            <p>正在提交批量执行任务...</p>
          </div>

          <div v-else-if="batchResults" class="batch-results">
            <!-- 进度概览 -->
            <div class="progress-overview">
              <el-progress
                :percentage="batchResults.progress"
                :status="getProgressStatus(batchResults.overall_status)"
                :stroke-width="8"
              />
              <div class="progress-stats">
                <span>总用例: {{ batchResults.total_cases }}</span>
                <span>已完成: {{ batchResults.completed_cases }}</span>
                <span>成功率: {{ batchResults.success_rate?.toFixed(1) }}%</span>
                <span>总耗时: {{ batchResults.total_duration?.toFixed(2) }}s</span>
              </div>
            </div>

            <!-- 状态统计 -->
            <div class="status-stats">
              <el-row :gutter="12">
                <el-col :span="6" v-for="(count, status) in batchResults.status_counts" :key="status">
                  <div class="stat-item">
                    <div class="stat-count">{{ count }}</div>
                    <div class="stat-label">{{ getStatusLabel(status) }}</div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 详细结果 -->
            <div class="execution-details">
              <h4>执行详情</h4>
              <el-table :data="batchResults.execution_details" size="small" max-height="300">
                <el-table-column prop="case_id" label="用例ID" width="70" />
                <el-table-column label="用例名称" min-width="150">
                  <template #default="{ row }">
                    {{ getCaseName(row.case_id) }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ getStatusLabel(row.status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="duration" label="耗时" width="70">
                  <template #default="{ row }">
                    {{ row.duration?.toFixed(2) || '-' }}s
                  </template>
                </el-table-column>
                <el-table-column label="步骤" width="80">
                  <template #default="{ row }">
                    {{ row.steps_passed || 0 }}/{{ row.steps_total || 0 }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template #default="{ row }">
                    <el-button size="small" @click="viewExecutionDetail(row)">
                      详情
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import { executionAPI } from '../api'

const router = useRouter()
const store = useApiEngineStore()

const caseTableRef = ref()
const configFormRef = ref()
const executing = ref(false)
const selectedCases = ref<any[]>([])
const batchResults = ref<any>(null)
const contextJson = ref('{}')

const filters = reactive({
  suite_id: undefined,
  keyword: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20
})

const executionConfig = reactive({
  execution_mode: 'parallel',
  max_concurrent: 5
})

let batchStatusTimer: any = null

const getSuiteName = (suiteId: number) => {
  const suite = store.suites.find(s => s.suite_id === suiteId)
  return suite?.name || `套件${suiteId}`
}

const getCaseName = (caseId: number) => {
  const caseItem = store.cases.find(c => c.case_id === caseId)
  return caseItem?.name || `用例${caseId}`
}

const getPriorityType = (priority: string) => {
  const map: Record<string, any> = {
    P0: 'danger',
    P1: 'warning',
    P2: 'primary',
    P3: 'info'
  }
  return map[priority] || 'info'
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger',
    error: 'danger',
    draft: 'info',
    active: 'success',
    deprecated: 'danger'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待中',
    running: '执行中',
    success: '成功',
    failed: '失败',
    error: '错误',
    draft: '草稿',
    active: '激活',
    deprecated: '已弃用'
  }
  return map[status] || status
}

const getBatchStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    success: 'success',
    failed: 'danger',
    error: 'danger'
  }
  return map[status] || 'info'
}

const getProgressStatus = (status: string) => {
  if (status === 'success') return 'success'
  if (status === 'failed' || status === 'error') return 'exception'
  return ''
}

const handleSearch = () => {
  store.fetchCases({
    page: pagination.page,
    page_size: pagination.page_size,
    suite_id: filters.suite_id,
    keyword: filters.keyword,
    status: filters.status
  })
}

const handleSelectionChange = (selection: any[]) => {
  selectedCases.value = selection
}

const selectAllCases = () => {
  caseTableRef.value?.toggleAllSelection()
}

const clearSelection = () => {
  caseTableRef.value?.clearSelection()
}

const handleBatchExecute = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请选择要执行的用例')
    return
  }

  try {
    // 解析全局变量
    let context = {}
    if (contextJson.value.trim()) {
      try {
        context = JSON.parse(contextJson.value)
      } catch (e) {
        ElMessage.warning('全局变量格式错误,将使用空对象')
      }
    }

    executing.value = true
    batchResults.value = null

    const caseIds = selectedCases.value.map(c => c.case_id)
    const response = await executionAPI.executeBatch(
      caseIds,
      context,
      executionConfig.execution_mode as 'parallel' | 'sequential',
      executionConfig.max_concurrent
    )

    ElMessage.success('批量执行已启动')

    // 开始轮询批量执行状态
    startBatchStatusPolling(response.data.batch_execution_id)
  } catch (error: any) {
    ElMessage.error(error.message || '批量执行失败')
    executing.value = false
  }
}

const startBatchStatusPolling = (batchExecutionId: string) => {
  const pollStatus = async () => {
    try {
      const response = await executionAPI.getBatchExecutionStatus(batchExecutionId)
      batchResults.value = response.data

      // 如果执行完成，停止轮询
      if (['success', 'failed'].includes(response.data.overall_status)) {
        executing.value = false
        stopBatchStatusPolling()

        const statusMessage = response.data.overall_status === 'success' ? '批量执行完成' : '批量执行完成，部分用例失败'
        ElMessage({
          message: statusMessage,
          type: response.data.overall_status === 'success' ? 'success' : 'warning'
        })
      }
    } catch (error) {
      console.error('批量执行状态查询失败:', error)
    }
  }

  // 立即查询一次
  pollStatus()

  // 每2秒查询一次
  batchStatusTimer = setInterval(pollStatus, 2000)
}

const stopBatchStatusPolling = () => {
  if (batchStatusTimer) {
    clearInterval(batchStatusTimer)
    batchStatusTimer = null
  }
}

const clearResults = () => {
  batchResults.value = null
}

const viewExecutionDetail = (execution: any) => {
  // 跳转到执行控制台页面
  router.push(`/plugin/api-engine/executions/${execution.execution_id}`)
}

const goBack = () => {
  router.go(-1)
}

onMounted(async () => {
  await store.fetchSuites()
  handleSearch()
})
</script>

<style scoped lang="scss">
.batch-execution-container {
  padding: 20px;

  .case-selection-card,
  .execution-config-card,
  .execution-results-card {
    margin-bottom: 20px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .selection-actions {
        display: flex;
        gap: 8px;
        align-items: center;

        .selection-count {
          font-size: 14px;
          color: #409eff;
          font-weight: 600;
        }
      }
    }

    h3, h4 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
    }
  }
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.case-list {
  .case-name {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 16px;
  }
}

.execution-results-card {
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .executing-info {
    text-align: center;
    padding: 20px;

    p {
      margin-top: 16px;
      color: #666;
    }
  }

  .batch-results {
    .progress-overview {
      margin-bottom: 20px;

      .progress-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 12px;
        font-size: 14px;
        color: #666;
      }
    }

    .status-stats {
      margin-bottom: 20px;

      .stat-item {
        text-align: center;
        padding: 12px;
        background: #f5f7fa;
        border-radius: 6px;

        .stat-count {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
          line-height: 1;
        }

        .stat-label {
          font-size: 12px;
          color: #909399;
          margin-top: 4px;
        }
      }
    }

    .execution-details {
      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
      }
    }
  }
}
</style>