<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="queryForm" :loading="loading" @search="loadData" @reset="resetQuery">
      <el-form-item label="项目" prop="project_id">
        <el-select v-model="queryForm.project_id" clearable placeholder="选择项目" style="width: 180px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>
        </el-select>
      </el-form-item>
      <el-form-item label="计划名称" prop="plan_name">
        <el-input v-model="queryForm.plan_name" clearable placeholder="请输入计划名称" style="width: 180px" />
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增计划
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="测试计划管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="plan_name" label="计划名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="plan_desc" label="计划描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="case_count" label="用例数量" width="100" align="center" />
      <el-table-column prop="create_time" label="创建时间" width="160" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="success" @click="handleExecute(row)">执行</el-button>
          <el-button link type="info" @click="handleViewHistory(row)">历史</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 执行历史对话框 -->
    <el-dialog v-model="historyDialogVisible" title="执行历史" width="80%">
      <el-table :data="historyData" border>
        <el-table-column prop="test_name" label="测试名称" min-width="150" />
        <el-table-column prop="test_status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.test_status === 'success' ? 'success' : row.test_status === 'failed' ? 'danger' : 'warning'">
              {{ row.test_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_uuid" label="执行批次" width="120" show-overflow-tooltip />
        <el-table-column prop="create_time" label="开始时间" width="160" />
        <el-table-column prop="finish_time" label="结束时间" width="160" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, executePlan, queryHistoryByPlanId } from './apiCollectionInfo'
import { queryAllProject } from '../project/apiProject.js'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 查询表单
const queryForm = reactive({
  project_id: null,
  plan_name: ''
})

// 表格数据
const tableData = ref([])

// 项目列表
const projectList = ref([])

// 历史对话框
const historyDialogVisible = ref(false)
const historyData = ref([])

// 加载项目列表
const loadProjectList = async () => {
  try {
    const res = await queryAllProject()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({
      ...queryForm,
      page: pagination.value.page,
      pageSize: pagination.value.limit
    })
    if (res.code === 20000) {
      tableData.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 重置查询
const resetQuery = () => {
  queryForm.project_id = null
  queryForm.plan_name = ''
  pagination.value.page = 1
  loadData()
}

// 新增
const handleAdd = () => {
  router.push('/ApiCollectionInfoForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({ path: '/ApiCollectionInfoForm', query: { id: row.id } })
}

// 执行测试计划
const handleExecute = async (row) => {
  try {
    await ElMessageBox.confirm(`确定执行测试计划【${row.plan_name}】吗？`, '提示', {
      type: 'warning'
    })
    
    const res = await executePlan({ plan_id: row.id })
    if (res.code === 20000) {
      ElMessage.success(`测试计划已开始执行，执行批次: ${res.data.execution_uuid}`)
      // 可以跳转到执行历史页面
    } else {
      ElMessage.error(res.msg || '执行失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败: ' + error.message)
    }
  }
}

// 查看执行历史
const handleViewHistory = async (row) => {
  try {
    const res = await queryHistoryByPlanId(row.id)
    if (res.code === 20000) {
      historyData.value = res.data || []
      historyDialogVisible.value = true
    }
  } catch (error) {
    ElMessage.error('加载历史失败: ' + error.message)
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除测试计划【${row.plan_name}】吗？`, '警告', {
      type: 'warning'
    })
    
    const res = await deleteData(row.id)
    if (res.code === 20000) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

onMounted(() => {
  loadProjectList()
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>

