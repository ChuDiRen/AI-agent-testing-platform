# Copyright (c) 2025 左岚. All rights reserved.
<template>
  <div class="test-cases-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>测试用例</h2>
      <p>管理和执行AI代理测试用例</p>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :model="searchForm" inline>
        <el-form-item label="用例名称">
          <el-input
            v-model="searchForm.caseName"
            placeholder="请输入用例名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="待执行" value="pending" />
            <el-option label="执行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增用例
      </el-button>
      <el-button type="success" @click="handleBatchRun" :disabled="!selectedCases.length">
        <el-icon><VideoPlay /></el-icon>
        批量执行
      </el-button>
      <el-button type="danger" @click="handleBatchDelete" :disabled="!selectedCases.length">
        <el-icon><Delete /></el-icon>
        批量删除
      </el-button>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table
        v-loading="loading"
        :data="tableData"
        @selection-change="handleSelectionChange"
        stripe
        border
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="caseName" label="用例名称" min-width="200" />
        <el-table-column prop="description" label="描述" min-width="250" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column prop="lastRunTime" label="最后执行时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="success" size="small" @click="handleRun(row)">
              执行
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, VideoPlay, Delete } from '@element-plus/icons-vue'
import { testCaseApi } from '@/api/modules/testcase'

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const selectedCases = ref([])

// 搜索表单
const searchForm = reactive({
  caseName: '',
  status: ''
})

// 分页数据
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 获取状态类型
const getStatusType = (status: string) => {
  const typeMap: Record<string, string> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const textMap: Record<string, string> = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败'
  }
  return textMap[status] || '未知'
}

// 加载测试用例列表
const loadTestCases = async () => {
  try {
    loading.value = true
    
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      case_name: searchForm.caseName || undefined,
      status: searchForm.status || undefined
    }
    
    const response = await testCaseApi.getTestCases(params)
    
    if (response.data.success) {
      tableData.value = response.data.data.test_cases || []
      pagination.total = response.data.data.total || 0
    }
  } catch (error) {
    console.error('加载测试用例失败:', error)
    ElMessage.error('加载测试用例失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadTestCases()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    caseName: '',
    status: ''
  })
  handleSearch()
}

// 新增用例
const handleAdd = () => {
  ElMessage.info('新增用例功能开发中...')
}

// 编辑用例
const handleEdit = (row: any) => {
  ElMessage.info(`编辑用例: ${row.caseName}`)
}

// 执行用例
const handleRun = (row: any) => {
  ElMessage.info(`执行用例: ${row.caseName}`)
}

// 删除用例
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除用例"${row.caseName}"吗？`, '确认删除', {
      type: 'warning'
    })
    const response = await testCaseApi.deleteTestCase(row.id)
    
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadTestCases()
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除用例失败:', error)
      ElMessage.error('删除用例失败')
    }
  }
}

// 批量执行
const handleBatchRun = () => {
  ElMessage.info(`批量执行 ${selectedCases.value.length} 个用例`)
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedCases.value.length} 个用例吗？`, '确认删除', {
      type: 'warning'
    })
    ElMessage.success('批量删除成功')
    loadTestCases()
  } catch {
    // 用户取消删除
  }
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedCases.value = selection
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.page = 1
  loadTestCases()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadTestCases()
}

// 初始化
onMounted(() => {
  loadTestCases()
})
</script>

<style scoped lang="scss">
.test-cases-container {
  padding: 20px;
  
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      margin: 0 0 8px 0;
      color: #303133;
    }
    
    p {
      margin: 0;
      color: #606266;
      font-size: 14px;
    }
  }
  
  .search-form {
    background: #fff;
    padding: 20px;
    border-radius: 4px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .action-buttons {
    margin-bottom: 20px;
  }
  
  .table-container {
    background: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    
    .pagination {
      padding: 20px;
      text-align: right;
    }
  }
}
</style>
