<template>
  <div class="document-list">
    <div class="list-header">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文档..."
          :prefix-icon="Search"
          @input="handleSearch"
          clearable
        />
      </div>
      <div class="filters">
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          @change="handleFilter"
          clearable
        >
          <el-option label="全部" value="" />
          <el-option label="已上传" value="uploaded" />
          <el-option label="索引中" value="indexing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
        
        <el-select
          v-model="permissionFilter"
          placeholder="权限筛选"
          @change="handleFilter"
          clearable
        >
          <el-option label="全部" value="" />
          <el-option label="私有" value="private" />
          <el-option label="公开" value="public" />
        </el-select>
      </div>
    </div>

    <el-table
      :data="filteredDocuments"
      v-loading="loading"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="title" label="文档标题" min-width="200">
        <template #default="{ row }">
          <div class="doc-title">
            <el-link type="primary" @click="viewDocument(row)">
              {{ row.title }}
            </el-link>
            <div class="doc-tags" v-if="row.tags?.length">
              <el-tag
                v-for="tag in row.tags"
                :key="tag"
                size="small"
                class="tag-item"
              >
                {{ tag }}
              </el-tag>
            </div>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      
      <el-table-column prop="file_name" label="文件名" min-width="120" show-overflow-tooltip />
      
      <el-table-column prop="file_size" label="大小" width="80">
        <template #default="{ row }">
          {{ formatFileSize(row.file_size) }}
        </template>
      </el-table-column>
      
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="permission" label="权限" width="80">
        <template #default="{ row }">
          <el-tag :type="row.permission === 'public' ? 'success' : 'info'" size="small">
            {{ row.permission === 'public' ? '公开' : '私有' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column prop="created_at" label="创建时间" width="150">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            @click="viewDocument(row)"
            :icon="View"
          >
            查看
          </el-button>
          
          <el-button
            v-if="row.status === 'uploaded'"
            size="small"
            type="success"
            @click="indexDocument(row)"
            :loading="row.indexing"
            :icon="Search"
          >
            索引
          </el-button>
          
          <el-button
            v-if="row.status === 'completed'"
            size="small"
            type="warning"
            @click="reindexDocument(row)"
            :loading="row.indexing"
            :icon="Refresh"
          >
            重建
          </el-button>
          
          <el-popconfirm
            title="确定要删除这个文档吗？"
            @confirm="deleteDocument(row)"
          >
            <template #reference>
              <el-button
                size="small"
                type="danger"
                :icon="Delete"
              >
                删除
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, View, Delete, Refresh } from '@element-plus/icons-vue'
import { getDocuments, deleteDocument as deleteDocApi, indexDocument as indexDocApi, reindexDocument as reindexDocApi } from '../api/document'

const emit = defineEmits(['view', 'refresh'])

const loading = ref(false)
const documents = ref([])
const searchQuery = ref('')
const statusFilter = ref('')
const permissionFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const filteredDocuments = computed(() => {
  let filtered = documents.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(doc => 
      doc.title.toLowerCase().includes(query) ||
      doc.description.toLowerCase().includes(query) ||
      doc.file_name.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(doc => doc.status === statusFilter.value)
  }

  if (permissionFilter.value) {
    filtered = filtered.filter(doc => doc.permission === permissionFilter.value)
  }

  return filtered
})

const loadDocuments = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await getDocuments(params)
    documents.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    ElMessage.error('加载文档列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索时重置到第一页
  currentPage.value = 1
}

const handleFilter = () => {
  // 筛选时重置到第一页
  currentPage.value = 1
}

const handleSizeChange = (size) => {
  pageSize.value = size
  loadDocuments()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadDocuments()
}

const viewDocument = (doc) => {
  emit('view', doc)
}

const indexDocument = async (doc) => {
  doc.indexing = true
  try {
    await indexDocApi(doc.id)
    ElMessage.success('文档索引开始')
    loadDocuments()
  } catch (error) {
    ElMessage.error('文档索引失败')
  } finally {
    doc.indexing = false
  }
}

const reindexDocument = async (doc) => {
  doc.indexing = true
  try {
    await reindexDocApi(doc.id)
    ElMessage.success('文档重建索引开始')
    loadDocuments()
  } catch (error) {
    ElMessage.error('文档重建索引失败')
  } finally {
    doc.indexing = false
  }
}

const deleteDocument = async (doc) => {
  try {
    await deleteDocApi(doc.id)
    ElMessage.success('文档删除成功')
    loadDocuments()
    emit('refresh')
  } catch (error) {
    ElMessage.error('文档删除失败')
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
  return new Date(dateStr).toLocaleDateString('zh-CN')
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

// 暴露方法
defineExpose({
  loadDocuments,
  refresh: loadDocuments
})

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.document-list {
  background: white;
  border-radius: 8px;
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 16px;
}

.search-box {
  flex: 1;
  max-width: 300px;
}

.filters {
  display: flex;
  gap: 12px;
}

.doc-title {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doc-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tag-item {
  font-size: 11px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
