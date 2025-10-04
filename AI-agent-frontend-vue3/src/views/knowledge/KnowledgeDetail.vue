<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="knowledge-detail-container">
    <!-- 头部 -->
    <el-page-header @back="goBack" :title="knowledgeBase?.name || '知识库详情'">
      <template #content>
        <div class="header-content">
          <span>{{ knowledgeBase?.name }}</span>
          <el-tag size="small" style="margin-left: 10px">
            {{ knowledgeBase?.document_count || 0 }} 文档
          </el-tag>
        </div>
      </template>
      <template #extra>
        <el-button type="primary" @click="showUploadDialog">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
      </template>
    </el-page-header>
    
    <!-- 搜索区域 -->
    <el-card class="search-card" style="margin-top: 20px">
      <el-input
        v-model="searchQuery"
        placeholder="搜索知识库内容..."
        size="large"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button :icon="Search" @click="handleSearch" :loading="searching">
            搜索
          </el-button>
        </template>
      </el-input>
      
      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <div class="results-header">
          <span>找到 {{ searchResults.length }} 条结果 (耗时 {{ searchTime }}s)</span>
        </div>
        <div
          v-for="result in searchResults"
          :key="result.chunk_id"
          class="result-item"
        >
          <div class="result-header">
            <span class="result-doc">📄 {{ result.doc_name }}</span>
            <el-tag size="small" type="success">
              相似度: {{ (result.score * 100).toFixed(1) }}%
            </el-tag>
          </div>
          <div class="result-content">{{ result.content }}</div>
        </div>
      </div>
    </el-card>
    
    <!-- 文档列表 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span>📑 文档列表</span>
      </template>
      
      <el-table :data="documents" style="width: 100%">
        <el-table-column prop="name" label="文档名称" min-width="200" />
        <el-table-column prop="file_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.file_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="getStatusType(row.status)"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link size="small" @click="viewDocument(row)">
              查看
            </el-button>
            <el-button link size="small" type="danger" @click="deleteDocument(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文档" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :limit="1"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、Word、TXT、Markdown 等格式
          </div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload" :loading="uploading">
          上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 任务进度提示 -->
    <el-dialog
      v-model="uploadTaskId"
      title="文档处理中"
      width="400px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="task-progress">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadProgress === 100 ? 'success' : undefined"
        />
        <div class="task-status">{{ uploadStatus }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, UploadFilled } from '@element-plus/icons-vue'
import {
  getKnowledgeBaseAPI,
  uploadDocumentAPI,
  deleteDocumentAPI,
  searchKnowledgeBaseAPI,
  type KnowledgeBase,
  type Document,
  type SearchResult
} from '@/api/knowledge'

const route = useRoute()
const router = useRouter()

// 状态
const kbId = ref(Number(route.params.kbId))
const knowledgeBase = ref<KnowledgeBase>()
const documents = ref<Document[]>([])
const searchQuery = ref('')
const searchResults = ref<SearchResult[]>([])
const searchTime = ref(0)
const searching = ref(false)
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref()
const selectedFile = ref<File>()
const uploadTaskId = ref('')
const uploadProgress = ref(0)
const uploadStatus = ref('')

// 加载知识库信息
const loadKnowledgeBase = async () => {
  try {
    const response = await getKnowledgeBaseAPI(kbId.value)
    if (response.data) {
      knowledgeBase.value = response.data
      // TODO: 加载文档列表
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  }
}

// 搜索
const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }
  
  searching.value = true
  try {
    const response = await searchKnowledgeBaseAPI({
      query: searchQuery.value,
      kb_id: kbId.value,
      top_k: 10,
      score_threshold: 0.3
    })
    
    if (response.data) {
      searchResults.value = response.data.results
      searchTime.value = response.data.search_time
    }
  } catch (error: any) {
    ElMessage.error(error.message || '搜索失败')
  } finally {
    searching.value = false
  }
}

// 显示上传对话框
const showUploadDialog = () => {
  uploadDialogVisible.value = true
  selectedFile.value = undefined
}

// 文件选择
const handleFileChange = (file: any) => {
  selectedFile.value = file.raw
}

// 上传文档
const handleUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = '上传中...'

  try {
    const response = await uploadDocumentAPI(kbId.value, selectedFile.value, true)

    if (response.data && response.data.task_id) {
      // 异步处理,轮询任务状态
      uploadTaskId.value = response.data.task_id
      ElMessage.success('文档已上传,正在后台处理')
      uploadDialogVisible.value = false

      // 开始轮询任务状态
      pollTaskStatus(response.data.task_id)
    } else {
      // 同步处理完成
      ElMessage.success('上传并处理成功')
      uploadDialogVisible.value = false
      loadKnowledgeBase()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 轮询任务状态
const pollTaskStatus = async (taskId: string) => {
  const maxAttempts = 60 // 最多轮询60次(5分钟)
  let attempts = 0

  const poll = async () => {
    try {
      const { getTaskStatusAPI } = await import('@/api/knowledge')
      const response = await getTaskStatusAPI(taskId)

      if (response.data) {
        const status = response.data
        uploadProgress.value = status.current || 0
        uploadStatus.value = status.status || ''

        if (status.state === 'SUCCESS') {
          ElMessage.success('文档处理完成')
          uploadTaskId.value = ''
          loadKnowledgeBase()
          return
        } else if (status.state === 'FAILURE') {
          ElMessage.error(`处理失败: ${status.error || '未知错误'}`)
          uploadTaskId.value = ''
          return
        } else if (status.state === 'PROCESSING' || status.state === 'PENDING') {
          // 继续轮询
          attempts++
          if (attempts < maxAttempts) {
            setTimeout(poll, 5000) // 5秒后再次查询
          } else {
            ElMessage.warning('任务处理超时,请稍后刷新查看')
            uploadTaskId.value = ''
          }
        }
      }
    } catch (error: any) {
      console.error('查询任务状态失败:', error)
      attempts++
      if (attempts < maxAttempts) {
        setTimeout(poll, 5000)
      }
    }
  }

  poll()
}

// 删除文档
const deleteDocument = async (doc: Document) => {
  try {
    await ElMessageBox.confirm(`确定要删除文档"${doc.name}"吗?`, '警告', {
      type: 'warning'
    })
    
    await deleteDocumentAPI(doc.doc_id)
    ElMessage.success('删除成功')
    loadKnowledgeBase()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 查看文档
const viewDocument = (doc: Document) => {
  // TODO: 实现文档查看
  ElMessage.info('文档查看功能开发中')
}

// 返回
const goBack = () => {
  router.back()
}

// 工具函数
const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    error: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    error: '失败'
  }
  return texts[status] || status
}

// 初始化
onMounted(() => {
  loadKnowledgeBase()
})
</script>

<style scoped lang="scss">
.knowledge-detail-container {
  padding: 20px;

  .header-content {
    display: flex;
    align-items: center;
  }

  .search-card {
    .search-results {
      margin-top: 20px;

      .results-header {
        padding: 10px 0;
        font-weight: 600;
        border-bottom: 1px solid #ebeef5;
      }

      .result-item {
        padding: 15px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .result-doc {
            font-weight: 600;
            color: #409eff;
          }
        }

        .result-content {
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }

  .task-progress {
    padding: 20px 0;

    .task-status {
      margin-top: 15px;
      text-align: center;
      color: #606266;
      font-size: 14px;
    }
  }
}
</style>

