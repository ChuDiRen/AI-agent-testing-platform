<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>用例管理</h3>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新增用例
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="queryForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="queryForm.project_id" placeholder="选择项目" clearable filterable>
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用例名称">
          <el-input v-model="queryForm.case_name" placeholder="用例名称" clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="case_name" label="用例名称" show-overflow-tooltip />
        <el-table-column prop="case_desc" label="用例描述" show-overflow-tooltip />
        <el-table-column prop="project_id" label="项目" width="120">
          <template #default="scope">
            {{ getProjectName(scope.row.project_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="success" size="small" @click="handleExecute(scope.row)">执行</el-button>
            <el-button type="info" size="small" @click="handleGenerateYaml(scope.row)">生成YAML</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryForm.page"
        v-model:page-size="queryForm.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleQuery"
        @current-change="handleQuery"
        class="pagination"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, generateYaml, executeCase } from './apiCase.js'
import { queryAll as queryProjects } from '../project/apiProject.js'
import { useRouter } from 'vue-router'

const router = useRouter()

// 查询表单
const queryForm = ref({
  project_id: null,
  case_name: '',
  page: 1,
  pageSize: 10
})

// 表格数据
const tableData = ref([])
const total = ref(0)
const loading = ref(false)

// 项目列表
const projectList = ref([])

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryProjects()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 获取项目名称
const getProjectName = (projectId) => {
  const project = projectList.value.find(p => p.id === projectId)
  return project ? project.project_name : '-'
}

// 查询数据
const handleQuery = async () => {
  loading.value = true
  try {
    const res = await queryByPage(queryForm.value)
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.data.msg || '查询失败')
    }
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置
const handleReset = () => {
  queryForm.value = {
    project_id: null,
    case_name: '',
    page: 1,
    pageSize: 10
  }
  handleQuery()
}

// 新增
const handleCreate = () => {
  router.push('/ApiCaseForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({
    path: '/ApiCaseForm',
    query: { id: row.id }
  })
}

// 执行用例
const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm(`确定执行用例 "${row.case_name}" 吗？`, '提示', {
      type: 'warning'
    })

    const res = await executeCase({
      case_id: row.id,
      test_name: `${row.case_name}_${new Date().getTime()}`
    })

    if (res.data.code === 200) {
      ElMessage.success('用例已开始执行，请到测试历史查看结果')
    } else {
      ElMessage.error(res.data.msg || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('执行失败:', error)
      ElMessage.error('执行失败，请稍后重试')
    }
  }
}

// 生成YAML
const handleGenerateYaml = async (row) => {
  try {
    const res = await generateYaml({
      case_id: row.id
    })

    if (res.data.code === 200) {
      ElMessage.success('YAML生成成功')
      // 显示YAML内容
      ElMessageBox.alert(res.data.data.yaml_content, 'YAML内容', {
        confirmButtonText: '确定',
        customStyle: { width: '80%' }
      })
    } else {
      ElMessage.error(res.data.msg || '生成失败')
    }
  } catch (error) {
    console.error('生成YAML失败:', error)
    ElMessage.error('生成YAML失败，请稍后重试')
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除用例 "${row.case_name}" 吗？`, '提示', {
      type: 'warning'
    })

    const res = await deleteData(row.id)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      handleQuery()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }
}

onMounted(() => {
  loadProjects()
  handleQuery()
})
</script>

<style scoped>
@import '@/styles/common-list.css';
</style>

