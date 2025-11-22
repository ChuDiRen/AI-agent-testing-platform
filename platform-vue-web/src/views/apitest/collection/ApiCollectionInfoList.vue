<template>
  <div class="api-test-plan-list">
    <el-card>
      <!-- 查询条件 -->
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="项目">
          <el-select v-model="queryForm.project_id" clearable placeholder="选择项目" style="width: 200px">
            <!-- 这里可以从store或API获取项目列表 -->
          </el-select>
        </el-form-item>
        <el-form-item label="计划名称">
          <el-input v-model="queryForm.plan_name" clearable placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
          <el-button type="success" @click="handleAdd">新增计划</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="plan_name" label="计划名称" min-width="150" />
        <el-table-column prop="plan_desc" label="计划描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="case_count" label="用例数量" width="100" align="center" />
        <el-table-column prop="create_time" label="创建时间" width="160" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button size="small" type="success" @click="handleExecute(row)">执行</el-button>
            <el-button size="small" type="info" @click="handleViewHistory(row)">历史</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; text-align: right"
      />
    </el-card>

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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, deleteData, executePlan, queryHistoryByPlanId } from './apiCollectionInfo'

const router = useRouter()

// 查询表单
const queryForm = ref({
  page: 1,
  pageSize: 10,
  project_id: null,
  plan_name: ''
})

// 表格数据
const tableData = ref([])
const total = ref(0)

// 历史对话框
const historyDialogVisible = ref(false)
const historyData = ref([])

// 加载数据
const loadData = async () => {
  try {
    const res = await queryByPage(queryForm.value)
    if (res.code === 20000) {
      tableData.value = res.data.list || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  }
}

// 重置查询
const resetQuery = () => {
  queryForm.value = {
    page: 1,
    pageSize: 10,
    project_id: null,
    plan_name: ''
  }
  loadData()
}

// 新增
const handleAdd = () => {
  router.push('/ApiTestPlanForm')
}

// 编辑
const handleEdit = (row) => {
  router.push({ path: '/ApiTestPlanForm', query: { id: row.id } })
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
  loadData()
})
</script>

<style scoped>
.api-test-plan-list {
  padding: 20px;
}
</style>

