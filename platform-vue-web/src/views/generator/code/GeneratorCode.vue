<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <span>代码生成</span>
      </template>

      <!-- 表信息 -->
      <el-descriptions v-if="tableInfo" :column="3" border>
        <el-descriptions-item label="表名">{{ tableInfo.table_name }}</el-descriptions-item>
        <el-descriptions-item label="表注释">{{ tableInfo.table_comment }}</el-descriptions-item>
        <el-descriptions-item label="类名">{{ tableInfo.class_name }}</el-descriptions-item>
        <el-descriptions-item label="功能名称">{{ tableInfo.function_name }}</el-descriptions-item>
        <el-descriptions-item label="模板类型">
          <el-tag v-if="tableInfo.tpl_category === 'single'" type="info">单表</el-tag>
          <el-tag v-else-if="tableInfo.tpl_category === 'tree'" type="success">树表</el-tag>
          <el-tag v-else-if="tableInfo.tpl_category === 'main_sub'" type="warning">主子表</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 操作按钮 -->
      <div class="button-group">
        <el-button type="primary" @click="onPreview" :loading="previewLoading">
          <el-icon><View /></el-icon>
          预览代码
        </el-button>
        <el-button type="success" @click="onDownload" :loading="downloadLoading">
          <el-icon><Download /></el-icon>
          下载代码
        </el-button>
        <el-button @click="router.back()">
          <el-icon><Back /></el-icon>
          返回
        </el-button>
      </div>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="showPreviewDialog" title="代码预览" width="80%" top="5vh">
      <el-tabs v-model="activeTab">
        <el-tab-pane v-for="(code, fileName) in previewCode" :key="fileName" :label="fileName" :name="fileName">
          <el-input
            type="textarea"
            :rows="20"
            :model-value="code"
            readonly
            style="font-family: monospace"
          />
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { queryById } from '../table/gentable'
import { previewCode as previewCodeApi, downloadCode as downloadCodeApi } from './generator'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'

const router = useRouter()

const tableId = ref(router.currentRoute.value.query.table_id)
const tableInfo = ref(null)
const showPreviewDialog = ref(false)
const previewCode = ref({})
const activeTab = ref('')
const previewLoading = ref(false)
const downloadLoading = ref(false)

// 加载表信息
const loadTableInfo = async () => {
  if (!tableId.value) {
    ElMessage.error('缺少表ID参数')
    return
  }
  try {
    const res = await queryById(tableId.value)
    if (res.data.code === 200) {
      tableInfo.value = res.data.data.table
    } else {
      ElMessage.error(res.data.msg || '获取表信息失败')
    }
  } catch (error) {
    ElMessage.error('获取表信息失败，请稍后重试')
  }
}

// 预览代码
const onPreview = async () => {
  previewLoading.value = true
  try {
    const res = await previewCodeApi({ table_id: tableId.value })
    if (res.data.code === 200) {
      previewCode.value = res.data.data
      if (Object.keys(previewCode.value).length > 0) {
        activeTab.value = Object.keys(previewCode.value)[0]
        showPreviewDialog.value = true
      } else {
        ElMessage.warning('没有可预览的代码')
      }
    } else {
      ElMessage.error(res.data.msg || '预览失败')
    }
  } catch (error) {
    ElMessage.error('预览失败，请稍后重试')
  } finally {
    previewLoading.value = false
  }
}

// 下载代码
const onDownload = async () => {
  downloadLoading.value = true
  try {
    const res = await downloadCodeApi({ table_id: tableId.value, gen_type: tableInfo.value?.gen_type || '0' })
    if (res) {
      // 创建blob链接
      const blob = new Blob([res], { type: 'application/zip' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${tableInfo.value?.table_name || 'code'}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      ElMessage.success('下载成功')
    } else {
      ElMessage.error('下载失败')
    }
  } catch (error) {
    ElMessage.error('下载失败，请稍后重试')
  } finally {
    downloadLoading.value = false
  }
}

onMounted(() => {
  loadTableInfo()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.button-group {
  margin-top: 20px;
  text-align: center;
}

.button-group .el-button {
  margin: 0 10px;
}
</style>
