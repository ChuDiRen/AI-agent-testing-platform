<template>
  <div class="response-panel">
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>测试执行中...</span>
    </div>

    <div v-else-if="!result || Object.keys(result).length === 0" class="empty-state">
      <el-empty description="暂无测试结果，点击【发送测试】执行接口测试" />
    </div>

    <div v-else class="result-content">
      <!-- 状态信息 -->
      <div class="status-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="状态">
            <el-tag :type="result.status === 'success' ? 'success' : 'danger'">
              {{ result.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态码">
            {{ result.status_code || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="响应时间">
            {{ result.response_time ? `${result.response_time}ms` : 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="完成时间">
            {{ result.finish_time || 'N/A' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 错误信息 -->
      <div v-if="result.error_message" class="error-message">
        <el-alert
          title="错误信息"
          type="error"
          :closable="false"
          :description="result.error_message"
        />
      </div>

      <!-- 响应标签页 -->
      <el-tabs v-model="activeTab" class="response-tabs">
        <!-- 响应体 -->
        <el-tab-pane label="Response Body" name="body">
          <div class="response-body">
            <pre v-if="result.response_body">{{ formatResponseBody(result.response_body) }}</pre>
            <el-empty v-else description="无响应体" />
          </div>
        </el-tab-pane>

        <!-- 响应头 -->
        <el-tab-pane label="Response Headers" name="headers">
          <div class="response-headers">
            <pre v-if="result.response_headers">{{ formatJson(result.response_headers) }}</pre>
            <el-empty v-else description="无响应头" />
          </div>
        </el-tab-pane>

        <!-- Allure报告 -->
        <el-tab-pane label="Allure Report" name="allure" v-if="result.allure_report_path">
          <div class="allure-report">
            <p>报告路径: {{ result.allure_report_path }}</p>
            <el-button type="primary" @click="openAllureReport">查看完整报告</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = defineProps({
  result: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const activeTab = ref('body')

// 格式化响应体
const formatResponseBody = (body) => {
  if (typeof body === 'string') {
    try {
      const obj = JSON.parse(body)
      return JSON.stringify(obj, null, 2)
    } catch {
      return body
    }
  } else if (typeof body === 'object') {
    return JSON.stringify(body, null, 2)
  }
  return body
}

// 格式化JSON
const formatJson = (data) => {
  if (typeof data === 'string') {
    try {
      const obj = JSON.parse(data)
      return JSON.stringify(obj, null, 2)
    } catch {
      return data
    }
  } else if (typeof data === 'object') {
    return JSON.stringify(data, null, 2)
  }
  return data
}

// 打开Allure报告 - 在新窗口打开报告路径
const openAllureReport = () => {
  if (props.result.allure_report_path) {
    window.open(props.result.allure_report_path, '_blank') // 新窗口打开报告
  } else {
    ElMessage.warning('暂无Allure报告')
  }
}
</script>

<style scoped lang="scss">
.response-panel {
  min-height: 400px;

  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 400px;
    gap: 10px;

    .el-icon {
      font-size: 32px;
    }
  }

  .empty-state {
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .result-content {
    .status-info {
      margin-bottom: 20px;
    }

    .error-message {
      margin-bottom: 20px;
    }

    .response-tabs {
      .response-body,
      .response-headers {
        pre {
          background: #f5f5f5;
          padding: 15px;
          border-radius: 4px;
          overflow: auto;
          max-height: 400px;
          font-size: 12px;
          font-family: 'Courier New', monospace;
        }
      }

      .allure-report {
        padding: 20px;

        p {
          margin-bottom: 15px;
          color: #666;
        }
      }
    }
  }
}
</style>

