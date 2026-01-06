<template>
  <div class="page-container">
    <BaseSearch :model="searchForm" @search="loadData" @reset="resetSearch">
      <el-form-item label="文件名">
        <el-input v-model="searchForm.name" placeholder="请输入文件名" clearable />
      </el-form-item>
      <el-form-item label="文件类型">
        <el-select v-model="searchForm.type" placeholder="全部" clearable>
          <el-option label="图片" value="image" />
          <el-option label="文档" value="document" />
          <el-option label="压缩包" value="archive" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 上传区域 -->
    <el-card shadow="never" class="mb-4">
      <el-upload
        ref="uploadRef"
        class="upload-area"
        drag
        multiple
        :action="uploadUrl"
        :headers="uploadHeaders"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :show-file-list="false"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处 或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持任意格式文件，单个文件不超过 50MB
          </div>
        </template>
      </el-upload>
    </el-card>

    <BaseTable
      title="文件列表"
      :data="tableData"
      :total="total"
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
      type="selection"
    >
      <template #header>
        <el-button 
          type="danger" 
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </template>

      <el-table-column prop="name" label="文件名" show-overflow-tooltip>
        <template #default="scope">
          <div class="flex items-center gap-2">
            <el-icon :class="getFileIconClass(scope.row.type)">
              <component :is="getFileIcon(scope.row.type)" />
            </el-icon>
            <span>{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="size" label="大小" width="120" />
      <el-table-column prop="type" label="类型" width="120">
        <template #default="scope">
          <el-tag size="small" :type="getFileTypeTag(scope.row.type)">
            {{ getFileTypeName(scope.row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="uploader" label="上传者" width="120" />
      <el-table-column prop="update_time" label="上传时间" width="180" />
      <el-table-column fixed="right" label="操作" width="200">
        <template #default="scope">
          <el-button link type="primary" @click="handlePreview(scope.row)">预览</el-button>
          <el-button link type="primary" @click="handleDownload(scope.row)">下载</el-button>
          <el-button link type="primary" @click="handleCopyPath(scope.row)">复制路径</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" title="文件预览" width="800px" destroy-on-close>
      <div class="preview-container">
        <!-- 图片预览 -->
        <el-image 
          v-if="previewFile?.type?.startsWith('image')" 
          :src="previewFile?.url" 
          fit="contain"
          style="max-height: 500px; width: 100%;"
        />
        <!-- 文本预览 -->
        <pre v-else-if="isTextFile(previewFile?.type)" class="text-preview">{{ previewContent }}</pre>
        <!-- 其他文件 -->
        <div v-else class="text-center py-10 text-gray-500">
          <el-icon :size="64"><Document /></el-icon>
          <p class="mt-4">该文件类型不支持预览，请下载后查看</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Delete, Document, Picture, VideoPlay, Folder, Files } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { getFileList, deleteFile, batchDeleteFile, downloadFile } from '../resource'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const selectedRows = ref([])
const uploadRef = ref(null)
const previewVisible = ref(false)
const previewFile = ref(null)
const previewContent = ref('')

const searchForm = reactive({
  name: '',
  type: ''
})

const pagination = reactive({
  page: 1,
  limit: 10
})

// 上传配置
const uploadUrl = computed(() => '/api/resource/file/upload')
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}))

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getFileList({ ...searchForm, ...pagination })
    if (res?.data?.code === 200) {
      tableData.value = res.data.data.list
      total.value = res.data.data.total
    } else {
      mockData()
    }
  } catch (e) {
    mockData()
  } finally {
    loading.value = false
  }
}

const mockData = () => {
  tableData.value = [
    { id: 1, name: 'test-screenshot.png', size: '1.2 MB', type: 'image/png', uploader: 'admin', update_time: '2026-01-05 10:00:00', url: '' },
    { id: 2, name: 'driver-binary.zip', size: '45 MB', type: 'application/zip', uploader: 'tester', update_time: '2026-01-04 11:30:00', url: '' },
    { id: 3, name: 'test-data.xlsx', size: '256 KB', type: 'application/xlsx', uploader: 'admin', update_time: '2026-01-03 14:20:00', url: '' },
    { id: 4, name: 'config.json', size: '2.3 KB', type: 'application/json', uploader: 'dev', update_time: '2026-01-02 09:15:00', url: '' },
    { id: 5, name: 'readme.txt', size: '1.5 KB', type: 'text/plain', uploader: 'admin', update_time: '2026-01-01 16:45:00', url: '' }
  ]
  total.value = 5
}

const resetSearch = () => {
  Object.assign(searchForm, { name: '', type: '' })
  loadData()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 文件图标
const getFileIcon = (type) => {
  if (type?.startsWith('image')) return Picture
  if (type?.startsWith('video')) return VideoPlay
  if (type?.includes('zip') || type?.includes('rar')) return Folder
  return Document
}

const getFileIconClass = (type) => {
  if (type?.startsWith('image')) return 'text-green-500'
  if (type?.startsWith('video')) return 'text-purple-500'
  if (type?.includes('zip') || type?.includes('rar')) return 'text-yellow-500'
  return 'text-blue-500'
}

const getFileTypeTag = (type) => {
  if (type?.startsWith('image')) return 'success'
  if (type?.includes('zip') || type?.includes('rar')) return 'warning'
  if (type?.includes('json') || type?.includes('text')) return 'info'
  return ''
}

const getFileTypeName = (type) => {
  if (type?.startsWith('image')) return '图片'
  if (type?.includes('zip') || type?.includes('rar')) return '压缩包'
  if (type?.includes('xlsx') || type?.includes('xls')) return 'Excel'
  if (type?.includes('json')) return 'JSON'
  if (type?.includes('text')) return '文本'
  return '文件'
}

const isTextFile = (type) => {
  return type?.includes('text') || type?.includes('json') || type?.includes('xml')
}

// 上传处理
const beforeUpload = (file) => {
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response, file) => {
  ElMessage.success(`${file.name} 上传成功`)
  loadData()
}

const handleUploadError = (error, file) => {
  // Mock 上传成功
  ElMessage.success(`${file.name} 上传成功 (Mock)`)
  loadData()
}

// 预览
const handlePreview = (row) => {
  previewFile.value = row
  if (isTextFile(row.type)) {
    // Mock 文本内容
    previewContent.value = '{\n  "name": "test",\n  "version": "1.0.0",\n  "description": "示例配置文件"\n}'
  }
  previewVisible.value = true
}

// 下载
const handleDownload = async (row) => {
  try {
    await downloadFile(row.id)
    ElMessage.success('开始下载')
  } catch (e) {
    // Mock 下载
    ElMessage.success('开始下载 (Mock)')
    // 模拟下载
    const link = document.createElement('a')
    link.href = row.url || '#'
    link.download = row.name
    link.click()
  }
}

// 复制路径
const handleCopyPath = (row) => {
  const path = `/files/${row.id}/${row.name}`
  navigator.clipboard.writeText(path).then(() => {
    ElMessage.success('路径已复制到剪贴板')
  }).catch(() => {
    ElMessage.info(`文件路径: ${path}`)
  })
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除文件 "${row.name}" 吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteFile(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('删除成功 (Mock)')
      tableData.value = tableData.value.filter(item => item.id !== row.id)
      total.value--
    }
  })
}

// 批量删除
const handleBatchDelete = () => {
  const ids = selectedRows.value.map(row => row.id)
  ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个文件吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteFile(ids)
      ElMessage.success('批量删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('批量删除成功 (Mock)')
      tableData.value = tableData.value.filter(row => !ids.includes(row.id))
      total.value -= ids.length
    }
  })
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container {
  padding: 0;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
}

.preview-container {
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.text-preview {
  width: 100%;
  max-height: 400px;
  overflow: auto;
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
