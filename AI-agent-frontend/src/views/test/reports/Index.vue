# Copyright (c) 2025 左岚. All rights reserved.
<template>
  <div class="test-reports-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>测试报告</h2>
      <p>查看和分析AI代理测试报告</p>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :model="searchForm" inline>
        <el-form-item label="报告名称">
          <el-input
            v-model="searchForm.reportName"
            placeholder="请输入报告名称"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="测试结果">
          <el-select
            v-model="searchForm.result"
            placeholder="请选择测试结果"
            clearable
            style="width: 150px"
          >
            <el-option label="通过" value="passed" />
            <el-option label="失败" value="failed" />
            <el-option label="部分通过" value="partial" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
          />
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
      <el-button type="success" @click="handleExportAll">
        <el-icon><Download /></el-icon>
        导出全部
      </el-button>
      <el-button type="danger" @click="handleBatchDelete" :disabled="!selectedReports.length">
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
        <el-table-column prop="reportName" label="报告名称" min-width="200" />
        <el-table-column prop="testCases" label="测试用例数" width="120" />
        <el-table-column prop="passedCases" label="通过数" width="100" />
        <el-table-column prop="failedCases" label="失败数" width="100" />
        <el-table-column prop="passRate" label="通过率" width="100">
          <template #default="{ row }">
            <el-progress
              :percentage="row.passRate"
              :color="getProgressColor(row.passRate)"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column prop="result" label="测试结果" width="100">
          <template #default="{ row }">
            <el-tag :type="getResultType(row.result)">
              {{ getResultText(row.result) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="执行时长" width="120" />
        <el-table-column prop="createTime" label="生成时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="success" size="small" @click="handleExport(row)">
              导出
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
          v-model:page-size="pagination.size"
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
import { Search, Refresh, Download, Delete } from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const selectedReports = ref([])

// 搜索表单
const searchForm = reactive({
  reportName: '',
  result: '',
  dateRange: null
})

// 分页数据
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 获取进度条颜色
const getProgressColor = (percentage: number) => {
  if (percentage >= 90) return '#67c23a'
  if (percentage >= 70) return '#e6a23c'
  return '#f56c6c'
}

// 获取结果类型
const getResultType = (result: string) => {
  const typeMap: Record<string, string> = {
    passed: 'success',
    failed: 'danger',
    partial: 'warning'
  }
  return typeMap[result] || 'info'
}

// 获取结果文本
const getResultText = (result: string) => {
  const textMap: Record<string, string> = {
    passed: '通过',
    failed: '失败',
    partial: '部分通过'
  }
  return textMap[result] || '未知'
}

// 加载测试报告列表
const loadTestReports = async () => {
  try {
    loading.value = true
    // TODO: 调用API获取测试报告数据
    // 模拟数据
    tableData.value = [
      {
        id: 1,
        reportName: '用户功能测试报告_20250913',
        testCases: 25,
        passedCases: 23,
        failedCases: 2,
        passRate: 92,
        result: 'partial',
        duration: '15分30秒',
        createTime: '2025-09-13 14:30:00'
      },
      {
        id: 2,
        reportName: 'AI代理性能测试报告_20250913',
        testCases: 10,
        passedCases: 10,
        failedCases: 0,
        passRate: 100,
        result: 'passed',
        duration: '8分45秒',
        createTime: '2025-09-13 16:15:00'
      }
    ]
    pagination.total = 2
  } catch (error) {
    console.error('加载测试报告失败:', error)
    ElMessage.error('加载测试报告失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadTestReports()
}

// 重置
const handleReset = () => {
  Object.assign(searchForm, {
    reportName: '',
    result: '',
    dateRange: null
  })
  handleSearch()
}

// 查看报告
const handleView = (row: any) => {
  ElMessage.info(`查看报告: ${row.reportName}`)
}

// 导出报告
const handleExport = (row: any) => {
  ElMessage.info(`导出报告: ${row.reportName}`)
}

// 导出全部
const handleExportAll = () => {
  ElMessage.info('导出全部报告功能开发中...')
}

// 删除报告
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除报告"${row.reportName}"吗？`, '确认删除', {
      type: 'warning'
    })
    ElMessage.success('删除成功')
    loadTestReports()
  } catch {
    // 用户取消删除
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedReports.value.length} 个报告吗？`, '确认删除', {
      type: 'warning'
    })
    ElMessage.success('批量删除成功')
    loadTestReports()
  } catch {
    // 用户取消删除
  }
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedReports.value = selection
}

// 分页大小变化
const handleSizeChange = (size: number) => {
  pagination.size = size
  loadTestReports()
}

// 当前页变化
const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadTestReports()
}

// 初始化
onMounted(() => {
  loadTestReports()
})
</script>

<style scoped lang="scss">
.test-reports-container {
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
