<template>
  <div class="documents-page">
    <div class="page-header">
      <h2>文档管理</h2>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传文档
      </el-button>
    </div>

    <!-- 文档列表 -->
    <el-card class="documents-card">
      <DocumentList 
        @view="handleViewDocument"
        @refresh="loadDocuments"
        ref="documentListRef"
      />
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog
      v-model="showUploadDialog"
      title="上传文档"
      width="600px"
      :close-on-click-modal="false"
    >
      <DocumentUpload
        @success="handleUploadSuccess"
        @error="handleUploadError"
        ref="documentUploadRef"
      />
      
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
      </template>
    </el-dialog>

    <!-- 文档详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="currentDocument?.title || '文档详情'"
      width="800px"
    >
      <div v-if="currentDocument" class="document-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="文档标题">
            {{ currentDocument.title }}
          </el-descriptions-item>
          <el-descriptions-item label="文件名">
            {{ currentDocument.file_name }}
          </el-descriptions-item>
          <el-descriptions-item label="文件大小">
            {{ formatFileSize(currentDocument.file_size) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentDocument.status)">
              {{ getStatusText(currentDocument.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="权限">
            <el-tag :type="currentDocument.permission === 'public' ? 'success' : 'info'">
              {{ currentDocument.permission === 'public' ? '公开' : '私有' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentDocument.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" v-if="currentDocument.updated_at">
            {{ formatDate(currentDocument.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="创建者">
            {{ currentDocument.created_by }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="document-description" v-if="currentDocument.description">
          <h4>文档描述</h4>
          <p>{{ currentDocument.description }}</p>
        </div>

        <div class="document-tags" v-if="currentDocument.tags?.length">
          <h4>标签</h4>
          <div class="tags-list">
            <el-tag
              v-for="tag in currentDocument.tags"
              :key="tag"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>

        <div class="document-actions">
          <el-button
            v-if="currentDocument.status === 'uploaded'"
            type="success"
            @click="handleIndexDocument"
            :loading="indexing"
          >
            <el-icon><Search /></el-icon>
            建立索引
          </el-button>
          
          <el-button
            v-if="currentDocument.status === 'completed'"
            type="warning"
            @click="handleReindexDocument"
            :loading="indexing"
          >
            <el-icon><Refresh /></el-icon>
            重建索引
          </el-button>
          
          <el-button
            type="primary"
            @click="handleDownloadDocument"
            :loading="downloading"
          >
            <el-icon><Download /></el-icon>
            下载文档
          </el-button>
          
          <el-button
            type="danger"
            @click="handleDeleteDocument"
            :loading="deleting"
          >
            <el-icon><Delete /></el-icon>
            删除文档
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Upload,
  Search,
  Refresh,
  Download,
  Delete
} from '@element-plus/icons-vue'
import DocumentList from '../../components/DocumentList.vue'
import DocumentUpload from '../../components/DocumentUpload.vue'
import { 
  getDocument, 
  deleteDocument as deleteDocApi,
  indexDocument as indexDocApi,
  reindexDocument as reindexDocApi
} from '../../api/document'

const documentListRef = ref()
const documentUploadRef = ref()

const showUploadDialog = ref(false)
const showDetailDialog = ref(false)
const currentDocument = ref(null)

const indexing = ref(false)
const downloading = ref(false)
const deleting = ref(false)

const loadDocuments = () => {
  if (documentListRef.value) {
    documentListRef.value.loadDocuments()
  }
}

const handleViewDocument = async (document) => {
  try {
    const response = await getDocument(document.id)
    if (response.success) {
      currentDocument.value = response.data
      showDetailDialog.value = true
    } else {
      ElMessage.error('获取文档详情失败')
    }
  } catch (error) {
    ElMessage.error('获取文档详情失败')
  }
}

const handleUploadSuccess = (document) => {
  ElMessage.success('文档上传成功')
  showUploadDialog.value = false
  loadDocuments()
  
  if (documentUploadRef.value) {
    documentUploadRef.value.resetForm()
  }
}

const handleUploadError = (error) => {
  ElMessage.error('文档上传失败')
}

const handleIndexDocument = async () => {
  if (!currentDocument.value) return

  try {
    indexing.value = true
    await indexDocApi(currentDocument.value.id)
    ElMessage.success('文档索引开始')
    loadDocuments()
    
    // 更新当前文档状态
    currentDocument.value.status = 'indexing'
  } catch (error) {
    ElMessage.error('文档索引失败')
  } finally {
    indexing.value = false
  }
}

const handleReindexDocument = async () => {
  if (!currentDocument.value) return

  try {
    indexing.value = true
    await reindexDocApi(currentDocument.value.id)
    ElMessage.success('文档重建索引开始')
    loadDocuments()
  } catch (error) {
    ElMessage.error('文档重建索引失败')
  } finally {
    indexing.value = false
  }
}

const handleDownloadDocument = async () => {
  if (!currentDocument.value) return

  try {
    downloading.value = true
    // 这里应该调用下载API
    ElMessage.success('文档下载开始')
  } catch (error) {
    ElMessage.error('文档下载失败')
  } finally {
    downloading.value = false
  }
}

const handleDeleteDocument = async () => {
  if (!currentDocument.value) return

  try {
    await ElMessageBox.confirm(
      `确定要删除文档 "${currentDocument.value.title}" 吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    deleting.value = true
    await deleteDocApi(currentDocument.value.id)
    ElMessage.success('文档删除成功')
    
    showDetailDialog.value = false
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('文档删除失败')
    }
  } finally {
    deleting.value = false
  }
}

const formatFileSize = (size) => {
  if (!size) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let unitIndex = 0
  let fileSize = size
  
  while (fileSize >= 1024 && unitIndex < units.length - 1) {
    fileSize /= 1024
    unitIndex++
  }
  
  return `${fileSize.toFixed(1)} ${units[unitIndex]}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    uploaded: 'info',
    indexing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    uploaded: '已上传',
    indexing: '索引中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.documents-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.documents-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.document-detail {
  padding: 20px 0;
}

.document-description,
.document-tags {
  margin-top: 24px;
}

.document-description h4,
.document-tags h4 {
  margin: 0 0 12px 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.document-description p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.tags-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-item {
  margin: 0;
}

.document-actions {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .documents-page {
    padding: 0;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .page-header .el-button {
    width: 100%;
  }
  
  .document-actions {
    flex-direction: column;
  }
  
  .document-actions .el-button {
    width: 100%;
  }
}
</style>
