<template>
  <el-dialog
    v-model="dialogVisible"
    title="用例执行结果"
    width="900px"
    @close="handleClose"
  >
    <!-- 执行状态概览 -->
    <div class="result-header">
      <div class="status-badge" :class="statusClass">
        <el-icon :size="24">
          <SuccessFilled v-if="isSuccess" />
          <CircleCloseFilled v-else-if="isFailed" />
          <Loading v-else />
        </el-icon>
        <span class="status-text">{{ statusText }}</span>
      </div>
      <div class="meta-info">
        <div class="meta-item">
          <span class="label">测试名称：</span>
          <span class="value">{{ resultData.test_name || '-' }}</span>
        </div>
        <div class="meta-item">
          <span class="label">测试ID：</span>
          <span class="value">{{ resultData.test_id || '-' }}</span>
        </div>
        <div class="meta-item">
          <span class="label">开始时间：</span>
          <span class="value">{{ resultData.create_time || '-' }}</span>
        </div>
        <div class="meta-item">
          <span class="label">结束时间：</span>
          <span class="value">{{ resultData.finish_time || '-' }}</span>
        </div>
        <div class="meta-item" v-if="duration">
          <span class="label">耗时：</span>
          <span class="value">{{ duration }}</span>
        </div>
      </div>
    </div>

    <!-- 错误信息 -->
    <el-alert
      v-if="resultData.error_message"
      :title="resultData.error_message"
      type="error"
      show-icon
      :closable="false"
      style="margin-bottom: 16px"
    />

    <!-- 结果详情 Tabs -->
    <el-tabs v-model="activeTab" type="border-card">
      <!-- 响应数据 Tab -->
      <el-tab-pane label="执行结果" name="response">
        <JsonViewer v-if="parsedResponseData" :data="parsedResponseData" :default-expanded="true" />
        <el-empty v-else description="暂无响应数据" />
      </el-tab-pane>

      <!-- YAML 内容 Tab -->
      <el-tab-pane label="YAML 用例" name="yaml">
        <YamlViewer v-if="parsedYamlContent" :content="parsedYamlContent" title="测试用例" />
        <el-empty v-else description="暂无YAML内容" />
      </el-tab-pane>

      <!-- 请求响应 Tab -->
      <el-tab-pane label="请求/响应" name="request">
        <div v-if="requestInfo.url" class="request-response">
          <div class="section">
            <div class="section-title">请求信息</div>
            <div class="info-row">
              <span class="method-badge" :class="requestInfo.method?.toLowerCase()">{{ requestInfo.method }}</span>
              <span class="url">{{ requestInfo.url }}</span>
            </div>
            <div class="sub-section" v-if="requestInfo.headers && Object.keys(requestInfo.headers).length">
              <div class="sub-title">Headers</div>
              <JsonViewer :data="requestInfo.headers" :default-expanded="true" :show-toolbar="true" />
            </div>
            <div class="sub-section" v-if="requestInfo.body">
              <div class="sub-title">Body</div>
              <JsonViewer :data="requestInfo.body" :default-expanded="true" :show-toolbar="true" />
            </div>
          </div>
          <div class="section">
            <div class="section-title">响应信息</div>
            <div class="info-row">
              <span class="status-code" :class="responseInfo.status_code >= 200 && responseInfo.status_code < 300 ? 'success' : 'error'">
                {{ responseInfo.status_code }}
              </span>
            </div>
            <div class="sub-section" v-if="responseInfo.body">
              <div class="sub-title">Body</div>
              <JsonViewer :data="responseInfo.body" :default-expanded="true" :show-toolbar="true" />
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无请求/响应数据" />
      </el-tab-pane>

      <!-- 测试用例结果 Tab -->
      <el-tab-pane label="测试用例" name="cases">
        <div v-if="testCases.length > 0">
          <el-table :data="testCases" border stripe>
            <el-table-column prop="name" label="用例名称" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="120" align="center">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'PASSED' ? 'success' : 'danger'" size="small">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div class="summary-bar" v-if="summary.total > 0">
            <span class="summary-item">
              总计: <strong>{{ summary.total }}</strong>
            </span>
            <span class="summary-item passed">
              通过: <strong>{{ summary.passed }}</strong>
            </span>
            <span class="summary-item failed" v-if="summary.failed > 0">
              失败: <strong>{{ summary.failed }}</strong>
            </span>
          </div>
        </div>
        <el-empty v-else description="暂无测试用例结果" />
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
      <el-button type="primary" @click="handleCopyResult">复制结果</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { SuccessFilled, CircleCloseFilled, Loading } from '@element-plus/icons-vue'
import JsonViewer from '~/components/JsonViewer.vue'
import YamlViewer from '~/components/YamlViewer.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  resultData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const dialogVisible = ref(false)
const activeTab = ref('response')

// 状态判断
const isSuccess = computed(() => ['completed', 'passed'].includes(props.resultData.status))
const isFailed = computed(() => ['failed', 'error'].includes(props.resultData.status))

const statusClass = computed(() => ({
  'status-success': isSuccess.value,
  'status-failed': isFailed.value,
  'status-running': !isSuccess.value && !isFailed.value
}))

const statusText = computed(() => {
  const map = {
    'completed': '执行完成',
    'passed': '测试通过',
    'failed': '测试失败',
    'error': '执行错误',
    'running': '执行中...'
  }
  return map[props.resultData.status] || props.resultData.status || '未知状态'
})

// 计算耗时
const duration = computed(() => {
  if (!props.resultData.create_time || !props.resultData.finish_time) return ''
  try {
    const start = new Date(props.resultData.create_time)
    const end = new Date(props.resultData.finish_time)
    const diff = end - start
    if (diff < 1000) return `${diff}ms`
    if (diff < 60000) return `${(diff / 1000).toFixed(2)}s`
    return `${Math.floor(diff / 60000)}m ${Math.floor((diff % 60000) / 1000)}s`
  } catch {
    return ''
  }
})

// 解析响应数据
const parsedResponseData = computed(() => {
  if (!props.resultData.response_data) return null
  try {
    return JSON.parse(props.resultData.response_data)
  } catch {
    return null
  }
})

const responseData = computed(() => {
  if (!parsedResponseData.value) return null
  return JSON.stringify(parsedResponseData.value, null, 2)
})

// 请求信息
const requestInfo = computed(() => {
  const data = parsedResponseData.value
  if (!data || !data.request) return {}
  return data.request
})

// 响应信息
const responseInfo = computed(() => {
  const data = parsedResponseData.value
  if (!data || !data.response) return {}
  return data.response
})

// 测试用例列表
const testCases = computed(() => {
  const data = parsedResponseData.value
  if (!data || !Array.isArray(data.test_cases)) return []
  return data.test_cases
})

// 汇总信息
const summary = computed(() => {
  const data = parsedResponseData.value
  if (!data || !data.summary) return { total: 0, passed: 0, failed: 0 }
  return {
    total: data.summary.total || 0,
    passed: data.summary.passed || 0,
    failed: data.summary.failed || 0
  }
})

// 解析 YAML 内容（实际上是JSON）
const parsedYamlContent = computed(() => {
  if (!props.resultData.yaml_content) return null
  try {
    // 尝试解析 JSON 字符串
    return JSON.parse(props.resultData.yaml_content)
  } catch {
    // 如果不是 JSON，返回原字符串（JsonViewer也支持字符串）
    return props.resultData.yaml_content
  }
})

// 监听 modelValue 变化
watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    activeTab.value = 'response'
  }
})

const handleClose = () => {
  emit('update:modelValue', false)
}

const handleCopyResult = () => {
  const text = JSON.stringify(props.resultData, null, 2)
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('结果已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.result-header {
  display: flex;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.status-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 24px;
  border-radius: 8px;
  min-width: 100px;
}

.status-badge.status-success {
  background: #f0f9eb;
  color: #67c23a;
}

.status-badge.status-failed {
  background: #fef0f0;
  color: #f56c6c;
}

.status-badge.status-running {
  background: #ecf5ff;
  color: #409eff;
}

.status-text {
  font-size: 14px;
  font-weight: 600;
}

.meta-info {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-item .label {
  color: #909399;
  font-size: 13px;
  white-space: nowrap;
}

.meta-item .value {
  color: #303133;
  font-size: 13px;
  word-break: break-all;
}

.code-block {
  background: #1e1e1e;
  border-radius: 4px;
  padding: 16px;
  max-height: 400px;
  overflow: auto;
}

.code-block pre {
  margin: 0;
  color: #d4d4d4;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.code-block.yaml pre {
  color: #ce9178;
}

:deep(.el-tabs__content) {
  padding: 16px;
}

/* 请求响应样式 */
.request-response {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.section-title {
  background: #f5f7fa;
  padding: 10px 16px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
}

.info-row {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.method-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
}

.method-badge.get { background: #e6f7ff; color: #1890ff; }
.method-badge.post { background: #f6ffed; color: #52c41a; }
.method-badge.put { background: #fff7e6; color: #fa8c16; }
.method-badge.delete { background: #fff1f0; color: #f5222d; }
.method-badge.patch { background: #f9f0ff; color: #722ed1; }

.url {
  font-family: monospace;
  color: #606266;
  word-break: break-all;
}

.status-code {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: 600;
}

.status-code.success { background: #f6ffed; color: #52c41a; }
.status-code.error { background: #fff1f0; color: #f5222d; }

.sub-section {
  padding: 0 16px 16px;
}

.sub-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.code-block.small {
  max-height: 200px;
}

/* 汇总栏样式 */
.summary-bar {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  gap: 24px;
}

.summary-item {
  font-size: 14px;
  color: #606266;
}

.summary-item.passed strong { color: #67c23a; }
.summary-item.failed strong { color: #f56c6c; }
</style>
