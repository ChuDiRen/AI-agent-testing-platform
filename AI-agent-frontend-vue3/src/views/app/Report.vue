<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="report-container">
    <el-card>
      <template #header>
        <div class="header">
          <h3>APP测试报告</h3>
          <div>
            <el-dropdown split-button type="success" @click="handleExportExcel" style="margin-right: 10px">
              导出 Excel
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="handleExportExcel">导出 Excel</el-dropdown-item>
                  <el-dropdown-item @click="handleExportPDF">导出 PDF</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button type="primary" @click="handleCreate">生成报告</el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input v-model="searchParams.keyword" placeholder="搜索报告名称" clearable style="width: 300px" @clear="handleSearch" />
        <el-select v-model="searchParams.status" placeholder="报告状态" clearable style="width: 150px; margin-left: 10px">
          <el-option label="全部" value="" />
          <el-option label="生成中" value="generating" />
          <el-option label="已完成" value="completed" />
          <el-option label="生成失败" value="failed" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-button type="primary" @click="handleSearch" style="margin-left: 10px">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 报告表格 -->
      <el-table :data="reportStore.reports" v-loading="reportStore.loading" stripe style="width: 100%; margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="报告名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'generating'" type="warning">生成中</el-tag>
            <el-tag v-else-if="row.status === 'completed'" type="success">已完成</el-tag>
            <el-tag v-else-if="row.status === 'failed'" type="danger">失败</el-tag>
            <el-tag v-else type="info">已归档</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_cases" label="总用例数" width="100" />
        <el-table-column prop="passed_cases" label="通过" width="80" />
        <el-table-column prop="failed_cases" label="失败" width="80" />
        <el-table-column prop="pass_rate" label="通过率" width="100">
          <template #default="{ row }">
            <span>{{ row.pass_rate }}%</span>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时(秒)" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="reportStore.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="报告名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入报告名称" />
        </el-form-item>
        <el-form-item label="报告描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入报告描述" />
        </el-form-item>
        <el-form-item label="报告类型" prop="report_type">
          <el-select v-model="formData.report_type" placeholder="请选择报告类型">
            <el-option label="执行报告" value="execution" />
            <el-option label="汇总报告" value="summary" />
            <el-option label="详细报告" value="detailed" />
            <el-option label="自定义报告" value="custom" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="reportStore.loading">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="报告详情" width="800px">
      <div v-if="reportStore.currentReport">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="报告名称">{{ reportStore.currentReport.name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag v-if="reportStore.currentReport.status === 'generating'" type="warning">生成中</el-tag>
            <el-tag v-else-if="reportStore.currentReport.status === 'completed'" type="success">已完成</el-tag>
            <el-tag v-else-if="reportStore.currentReport.status === 'failed'" type="danger">失败</el-tag>
            <el-tag v-else type="info">已归档</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="总用例数">{{ reportStore.currentReport.total_cases }}</el-descriptions-item>
          <el-descriptions-item label="通过用例">{{ reportStore.currentReport.passed_cases }}</el-descriptions-item>
          <el-descriptions-item label="失败用例">{{ reportStore.currentReport.failed_cases }}</el-descriptions-item>
          <el-descriptions-item label="跳过用例">{{ reportStore.currentReport.skipped_cases }}</el-descriptions-item>
          <el-descriptions-item label="通过率">{{ reportStore.currentReport.pass_rate }}%</el-descriptions-item>
          <el-descriptions-item label="执行率">{{ reportStore.currentReport.execution_rate }}%</el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ reportStore.currentReport.start_time }}</el-descriptions-item>
          <el-descriptions-item label="结束时间">{{ reportStore.currentReport.end_time }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ reportStore.currentReport.duration }}秒</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ reportStore.currentReport.created_at }}</el-descriptions-item>
          <el-descriptions-item label="报告描述" :span="2">{{ reportStore.currentReport.description }}</el-descriptions-item>
          <el-descriptions-item label="报告摘要" :span="2">{{ reportStore.currentReport.summary }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { useReportStore } from '@/store/report'
import type { ReportCreateData, TestReport } from '@/api/report'
import { exportReportToExcel, exportReportToPDF } from '@/utils/export'

const reportStore = useReportStore()

const searchParams = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
  status: ''
})

const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('创建报告')
const isEdit = ref(false)
const currentId = ref<number>()

const formRef = ref<FormInstance>()
const formData = reactive<ReportCreateData>({
  name: '',
  description: '',
  report_type: 'execution'
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入报告名称', trigger: 'blur' }],
  report_type: [{ required: true, message: '请选择报告类型', trigger: 'change' }]
}

const handleSearch = () => {
  reportStore.fetchReports(searchParams)
}

const handleReset = () => {
  searchParams.keyword = ''
  searchParams.status = ''
  searchParams.page = 1
  handleSearch()
}

const handleCreate = () => {
  dialogTitle.value = '生成报告'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: TestReport) => {
  dialogTitle.value = '编辑报告'
  isEdit.value = true
  currentId.value = row.id
  formData.name = row.name
  formData.description = row.description
  formData.report_type = row.report_type
  dialogVisible.value = true
}

const handleView = async (row: TestReport) => {
  const success = await reportStore.fetchReportDetail(row.id)
  if (success) {
    viewDialogVisible.value = true
  } else {
    ElMessage.error('获取报告详情失败')
  }
}

const handleDelete = (row: TestReport) => {
  ElMessageBox.confirm('确定要删除这个报告吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const success = await reportStore.removeReport(row.id)
    if (success) {
      ElMessage.success('删除成功')
      handleSearch()
    } else {
      ElMessage.error('删除失败')
    }
  })
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      let success = false
      if (isEdit.value && currentId.value) {
        success = await reportStore.modifyReport(currentId.value, formData)
      } else {
        success = await reportStore.addReport(formData)
      }

      if (success) {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        handleSearch()
      } else {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.report_type = 'execution'
  formRef.value?.clearValidate()
}

// 导出 Excel
const handleExportExcel = () => {
  if (reportStore.reports.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  const success = exportReportToExcel(reportStore.reports, 'APP测试报告')
  if (success) {
    ElMessage.success('导出成功')
  } else {
    ElMessage.error('导出失败')
  }
}

// 导出 PDF
const handleExportPDF = () => {
  if (reportStore.reports.length === 0) {
    ElMessage.warning('暂无数据可导出')
    return
  }
  
  const success = exportReportToPDF(reportStore.reports, 'APP测试报告')
  if (success) {
    ElMessage.success('导出成功')
  } else {
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped>
.report-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h3 {
  margin: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>


