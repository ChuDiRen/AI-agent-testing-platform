<template>
  <div class="case-list-container">
    <div class="header">
      <h2>用例管理</h2>
      <el-button type="primary" @click="router.push('/plugin/api-engine/cases/create')">
        <el-icon><Plus /></el-icon>
        创建用例
      </el-button>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="filters.name"
        placeholder="搜索用例名称"
        clearable
        style="width: 200px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="filters.suite_id" placeholder="选择套件" clearable style="width: 200px">
        <el-option
          v-for="suite in store.suites"
          :key="suite.suite_id"
          :label="suite.name"
          :value="suite.suite_id"
        />
      </el-select>
      <el-select v-model="filters.status" placeholder="状态" clearable style="width: 150px">
        <el-option label="草稿" value="draft" />
        <el-option label="激活" value="active" />
        <el-option label="已弃用" value="deprecated" />
      </el-select>
      <el-select v-model="filters.priority" placeholder="优先级" clearable style="width: 150px">
        <el-option label="P0" value="P0" />
        <el-option label="P1" value="P1" />
        <el-option label="P2" value="P2" />
        <el-option label="P3" value="P3" />
      </el-select>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <el-table
      v-loading="store.casesLoading"
      :data="store.cases"
      border
      style="width: 100%"
    >
      <el-table-column prop="case_id" label="ID" width="80" />
      <el-table-column prop="name" label="用例名称" min-width="200" />
      <el-table-column prop="config_mode" label="配置模式" width="100">
        <template #default="{ row }">
          <el-tag :type="row.config_mode === 'form' ? 'success' : 'info'">
            {{ row.config_mode === 'form' ? '表单' : 'YAML' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="{ row }">{{ formatDate(row.create_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleExecute(row.case_id)">
            <el-icon><VideoPlay /></el-icon>
            执行
          </el-button>
          <el-button size="small" @click="handleEdit(row.case_id)">编辑</el-button>
          <el-button size="small" @click="handleClone(row.case_id)">克隆</el-button>
          <el-popconfirm
            title="确定要删除这个用例吗?"
            @confirm="handleDelete(row.case_id)"
          >
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="store.casesTotal"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search, VideoPlay } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'

const router = useRouter()
const store = useApiEngineStore()

const filters = reactive({
  name: '',
  suite_id: undefined,
  status: '',
  priority: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20
})

const handleSearch = () => {
  store.fetchCases({
    page: pagination.page,
    page_size: pagination.page_size,
    name: filters.name || undefined,
    suite_id: filters.suite_id,
    status: filters.status || undefined,
    priority: filters.priority || undefined
  })
}

const handleExecute = (caseId?: number) => {
  if (!caseId) return
  router.push(`/plugin/api-engine/executions/${caseId}`)
}

const handleEdit = (caseId?: number) => {
  if (!caseId) return
  router.push(`/plugin/api-engine/cases/${caseId}/edit`)
}

const handleClone = async (caseId?: number) => {
  if (!caseId) return
  try {
    await store.cloneCase(caseId)
    ElMessage.success('克隆成功')
    handleSearch()
  } catch (error: any) {
    ElMessage.error(error.message || '克隆失败')
  }
}

const handleDelete = async (caseId?: number) => {
  if (!caseId) return
  try {
    await store.deleteCase(caseId)
    ElMessage.success('删除成功')
    handleSearch()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    draft: 'info',
    active: 'success',
    deprecated: 'warning'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(async () => {
  await store.fetchSuites()
  handleSearch()
})
</script>

<style scoped lang="scss">
.case-list-container {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

