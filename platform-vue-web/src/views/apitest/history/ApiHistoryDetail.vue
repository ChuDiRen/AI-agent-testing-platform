<template>
  <div class="history-detail">
    <el-page-header @back="goBack" :content="pageTitle">
      <template #extra>
        <el-space>
          <el-button type="primary" :icon="View" @click="viewReport" v-if="detail.allure_report_path">
            查看报告
          </el-button>
          <el-button :icon="Download" @click="downloadReport" v-if="detail.allure_report_path">
            下载报告
          </el-button>
        </el-space>
      </template>
    </el-page-header>

    <el-card style="margin-top: 16px" v-loading="loading">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="测试ID">{{ detail.id }}</el-descriptions-item>
        <el-descriptions-item label="测试名称">{{ detail.test_name }}</el-descriptions-item>
        
        <el-descriptions-item label="测试状态">
          <el-tag :type="getStatusType(detail.test_status)">
            {{ getStatusText(detail.test_status) }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="执行UUID">{{ detail.execution_uuid }}</el-descriptions-item>
        
        <el-descriptions-item label="项目ID">{{ detail.project_id }}</el-descriptions-item>
        <el-descriptions-item label="用例ID">{{ detail.case_info_id }}</el-descriptions-item>
        
        <el-descriptions-item label="请求URL">{{ detail.request_url }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">
          <el-tag>{{ detail.request_method }}</el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="状态码">
          <el-tag :type="detail.status_code === 200 ? 'success' : 'danger'">
            {{ detail.status_code }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="响应时间">{{ detail.response_time }}ms</el-descriptions-item>
        
        <el-descriptions-item label="开始时间">{{ detail.create_time }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ detail.finish_time }}</el-descriptions-item>
        
        <el-descriptions-item label="报告路径" :span="2">
          {{ detail.allure_report_path || '无' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">请求详情</el-divider>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="请求头">
          <pre>{{ formatJson(detail.request_headers) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="请求参数">
          <pre>{{ formatJson(detail.request_params) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="请求体">
          <pre>{{ formatJson(detail.request_body) }}</pre>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">响应详情</el-divider>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="响应头">
          <pre>{{ formatJson(detail.response_headers) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="响应体">
          <pre>{{ formatJson(detail.response_body) }}</pre>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left" v-if="detail.error_message">错误信息</el-divider>
      <el-alert 
        v-if="detail.error_message"
        type="error" 
        :title="detail.error_message"
        :closable="false"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Download } from '@element-plus/icons-vue'
import axios from '@/axios'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const detail = ref({})

const pageTitle = computed(() => {
  return detail.value.test_name || '测试详情'
})

const loadDetail = async () => {
  loading.value = true
  try {
    const { data } = await axios.get(`/ApiHistory/queryById?id=${route.params.id}`)
    if (data.code === 200) {
      detail.value = data.data
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const map = {
    'success': 'success',
    'failed': 'danger',
    'running': 'warning',
    'pending': 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    'success': '成功',
    'failed': '失败',
    'running': '执行中',
    'pending': '待执行'
  }
  return map[status] || status
}

const formatJson = (str) => {
  if (!str) return ''
  try {
    return JSON.stringify(JSON.parse(str), null, 2)
  } catch {
    return str
  }
}

const viewReport = () => {
  router.push({
    path: '/apitest/report/viewer',
    query: { history_id: detail.value.id }
  })
}

const downloadReport = () => {
  window.open(`/ApiReportViewer/download?history_id=${detail.value.id}`, '_blank')
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadDetail()
})
</script>

<style scoped>
pre {
  margin: 0;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
}
</style>
