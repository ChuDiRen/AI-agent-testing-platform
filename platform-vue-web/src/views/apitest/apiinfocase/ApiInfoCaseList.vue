<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="handleQuery" @reset="handleReset">
      <el-form-item label="项目" prop="project_id">
        <el-select v-model="queryForm.project_id" placeholder="选择项目" clearable filterable style="width: 180px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="用例名称" prop="case_name">
        <el-input v-model="queryForm.case_name" placeholder="用例名称" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item label="执行器" prop="executor">
        <el-select v-model="currentExecutorCode" placeholder="选择执行器" clearable style="width: 200px">
          <el-option
            v-for="exe in executorList"
            :key="exe.plugin_code"
            :label="exe.plugin_name"
            :value="exe.plugin_code"
          />
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>
          新增用例
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="用例管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="handleQuery"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="case_name" label="用例名称" show-overflow-tooltip />
      <el-table-column prop="case_desc" label="用例描述" show-overflow-tooltip />
      <el-table-column prop="project_id" label="项目" width="120">
        <template #default="scope">
          {{ getProjectName(scope.row.project_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="170" />
      <el-table-column label="操作" width="260" fixed="right">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="success" @click="handleExecute(scope.row)">执行</el-button>
          <el-button link type="info" @click="handleGenerateYaml(scope.row)">生成YAML</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, generateYaml, executeCase } from './apiInfoCase.js'
import { queryAll as queryProjects } from '../project/apiProject.js'
import { useRouter } from 'vue-router'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { listExecutors } from '../task/apiTask.js'

const router = useRouter()

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 查询表单
const queryForm = reactive({
  project_id: null,
  case_name: ''
})

// 执行器列表与当前选择
const executorList = ref([])
const currentExecutorCode = ref('')

// 表格数据
const tableData = ref([])

// 项目列表
const projectList = ref([])

// 加载执行器列表
const loadExecutors = async () => {
  try {
    const res = await listExecutors()
    if (res.data.code === 200) {
      executorList.value = res.data.data || []
      // 如未选择且有可用执行器，默认选第一个
      if (!currentExecutorCode.value && executorList.value.length > 0) {
        currentExecutorCode.value = executorList.value[0].plugin_code
      }
    } else {
      ElMessage.error(res.data.msg || '加载执行器列表失败')
    }
  } catch (error) {
    console.error('加载执行器列表失败:', error)
    ElMessage.error('加载执行器列表失败，请稍后重试')
  }
}

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
    const res = await queryByPage({
      ...queryForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit
    })
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
  queryForm.project_id = null
  queryForm.case_name = ''
  pagination.value.page = 1
  handleQuery()
}

// 新增
const handleCreate = () => {
  router.push('/ApiInfoCaseForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({
    path: '/ApiInfoCaseForm',
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
      test_name: `${row.case_name}_${new Date().getTime()}`,
      executor_code: currentExecutorCode.value || undefined
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
  loadExecutors()
  handleQuery()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>

