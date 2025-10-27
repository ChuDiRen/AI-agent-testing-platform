<template>
  <div v-if="calls && calls.length > 0" class="tool-calls-container">
    <div class="tool-calls-header">
      <el-icon><Tools /></el-icon>
      <span>工具调用 ({{ calls.length }})</span>
    </div>
    
    <el-collapse v-model="activeNames" class="tool-calls-collapse">
      <el-collapse-item 
        v-for="call in calls" 
        :key="call.id"
        :name="call.id"
      >
        <template #title>
          <div class="tool-call-title">
            <el-tag type="primary" size="small">🔧 {{ call.name }}</el-tag>
            <el-tag v-if="call.status" :type="getStatusType(call.status)" size="small">
              {{ call.status }}
            </el-tag>
          </div>
        </template>
        
        <div class="tool-call-content">
          <!-- 工具参数 -->
          <div v-if="call.args" class="tool-section">
            <div class="section-title">参数：</div>
            <pre class="json-preview">{{ formatJson(call.args) }}</pre>
          </div>

          <!-- 工具结果 -->
          <div v-if="call.result" class="tool-section">
            <div class="section-title">结果：</div>
            <div v-if="typeof call.result === 'object'" class="json-preview">
              <pre>{{ formatJson(call.result) }}</pre>
            </div>
            <div v-else class="text-result">
              {{ call.result }}
            </div>
          </div>

          <!-- 错误信息 -->
          <div v-if="call.error" class="tool-section error-section">
            <div class="section-title">错误：</div>
            <el-alert type="error" :closable="false">
              {{ call.error }}
            </el-alert>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Tools } from '@element-plus/icons-vue'

const props = defineProps({
  calls: {
    type: Array,
    default: () => []
  }
})

const activeNames = ref([])

const getStatusType = (status) => {
  const types = {
    'success': 'success',
    'running': 'warning',
    'error': 'danger',
    'pending': 'info'
  }
  return types[status] || 'info'
}

const formatJson = (obj) => {
  try {
    return JSON.stringify(obj, null, 2)
  } catch (e) {
    return String(obj)
  }
}
</script>

<style scoped>
.tool-calls-container {
  margin: 12px 0;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.tool-calls-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-weight: 600;
  color: #606266;
}

.tool-call-title {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.tool-call-content {
  padding: 8px 0;
}

.tool-section {
  margin-bottom: 12px;
}

.tool-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.json-preview {
  background-color: #fff;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  overflow-x: auto;
  margin: 0;
}

.text-result {
  background-color: #fff;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-section {
  margin-top: 12px;
}

.tool-calls-collapse {
  border: none;
}

.tool-calls-collapse :deep(.el-collapse-item__header) {
  background-color: #fff;
  border-radius: 4px;
  padding: 0 12px;
  border: 1px solid #dcdfe6;
  margin-bottom: 8px;
}

.tool-calls-collapse :deep(.el-collapse-item__wrap) {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-top: none;
  border-radius: 0 0 4px 4px;
  margin-top: -8px;
}

.tool-calls-collapse :deep(.el-collapse-item__content) {
  padding: 12px;
}
</style>

