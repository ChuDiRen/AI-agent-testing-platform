<template>
  <div class="report-viewer">
    <el-card class="header-card">
      <el-page-header @back="goBack" :content="reportTitle">
        <template #extra>
          <el-space>
            <el-button type="primary" :icon="Download" @click="downloadReport">
              下载报告
            </el-button>
            <el-button :icon="Refresh" @click="refreshReport">
              刷新
            </el-button>
          </el-space>
        </template>
      </el-page-header>
    </el-card>

    <el-card class="report-card" v-loading="loading">
      <div v-if="reportUrl" class="report-container">
        <iframe 
          :src="reportUrl" 
          frameborder="0" 
          class="report-iframe"
          @load="onIframeLoad"
        ></iframe>
      </div>
      <el-empty v-else description="暂无报告数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Refresh } from '@element-plus/icons-vue'
import { queryById } from '~/views/apitest/history/apiHistory'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const reportUrl = ref('')
const reportInfo = ref(null)

const reportTitle = computed(() => {
  return reportInfo.value?.test_name || '测试报告'
})

// 获取报告URL（通过后端API代理）
const getReportUrl = () => {
  const { history_id, execution_uuid, report_path } = route.query
  // 使用后端API地址（开发环境通过代理，生产环境直接访问）
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
  
  if (history_id) {
    return `${apiBase}/ApiReportViewer/view?history_id=${history_id}`
  } else if (execution_uuid) {
    return `${apiBase}/ApiReportViewer/view?execution_uuid=${execution_uuid}`
  } else if (report_path) {
    return `${apiBase}/ApiReportViewer/view?report_path=${report_path}`
  }
  
  return ''
}

// 加载报告
const loadReport = async () => {
  loading.value = true
  try {
    const url = getReportUrl()
    if (!url) {
      ElMessage.warning('缺少报告参数')
      return
    }
    
    reportUrl.value = url
    
    // 获取报告信息
    if (route.query.history_id) {
      const { data } = await queryById(route.query.history_id)
      if (data.code === 200) {
        reportInfo.value = data.data
      }
    }
  } catch (error) {
    ElMessage.error('加载报告失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// iframe加载完成
const onIframeLoad = () => {
  loading.value = false
}

// 下载报告
const downloadReport = async () => {
  try {
    const { history_id, execution_uuid } = route.query
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
    let url = `${apiBase}/ApiReportViewer/download?`
    
    if (history_id) {
      url += `history_id=${history_id}`
    } else if (execution_uuid) {
      url += `execution_uuid=${execution_uuid}`
    }
    
    window.open(url, '_blank')
    ElMessage.success('开始下载报告')
  } catch (error) {
    ElMessage.error('下载失败: ' + error.message)
  }
}

// 刷新报告
const refreshReport = () => {
  loadReport()
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(() => {
  loadReport()
})
</script>

<style scoped>
.report-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-card {
  margin-bottom: 16px;
}

.report-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.report-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.report-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
