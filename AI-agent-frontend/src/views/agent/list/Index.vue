<template>
  <div class="agent-list-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>AI代理列表</span>
          <el-button type="primary" @click="handleAddAgent">新增代理</el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="代理名称" />
        <el-table-column prop="type" label="代理类型" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="success" @click="handleStart(scope.row)" v-if="scope.row.status === '停止'">启动</el-button>
            <el-button size="small" type="warning" @click="handleStop(scope.row)" v-else>停止</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 表格数据
const tableData = ref([
  {
    id: 1,
    name: '客服助手',
    type: '对话型',
    description: '处理客户咨询的智能客服',
    status: '运行中',
    createTime: '2025-08-15 09:00:00'
  },
  {
    id: 2,
    name: '数据分析师',
    type: '分析型',
    description: '自动分析业务数据并生成报告',
    status: '停止',
    createTime: '2025-08-16 14:30:00'
  },
  {
    id: 3,
    name: '代码助手',
    type: '开发型',
    description: '辅助开发人员编写代码',
    status: '运行中',
    createTime: '2025-08-18 11:15:00'
  }
])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(3)
const loading = ref(false)

// 获取状态对应的类型
const getStatusType = (status: string) => {
  switch (status) {
    case '运行中':
      return 'success'
    case '停止':
      return 'info'
    case '异常':
      return 'danger'
    default:
      return ''
  }
}

// 处理新增代理
const handleAddAgent = () => {
  ElMessage.info('新增代理功能待实现')
}

// 处理编辑
const handleEdit = (row: any) => {
  ElMessage.info(`编辑代理: ${row.name}`)
}

// 处理启动
const handleStart = (row: any) => {
  ElMessageBox.confirm(`确定要启动代理 "${row.name}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'info'
  }).then(() => {
    row.status = '运行中'
    ElMessage.success(`已启动代理: ${row.name}`)
  }).catch(() => {
    ElMessage.info('已取消操作')
  })
}

// 处理停止
const handleStop = (row: any) => {
  ElMessageBox.confirm(`确定要停止代理 "${row.name}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    row.status = '停止'
    ElMessage.success(`已停止代理: ${row.name}`)
  }).catch(() => {
    ElMessage.info('已取消操作')
  })
}

// 处理删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定要删除代理 "${row.name}" 吗?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // TODO: 调用实际的删除API
    // await AgentApi.deleteAgent(row.id)
    ElMessage.success(`删除代理: ${row.name}`)
    // TODO: 刷新代理列表
    // loadAgentList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除代理失败:', error)
      // 检查是否是代理不存在的错误
      if (error?.response?.status === 404 || error?.response?.data?.detail?.includes('代理不存在')) {
        ElMessage.warning('代理已不存在，将刷新列表')
        // TODO: 刷新代理列表
        // loadAgentList()
      } else {
        // 显示具体的错误信息，兼容 FastAPI 的 detail 字段
        const errorMessage = error?.response?.data?.detail || error?.response?.data?.message || error?.message || '删除代理失败'
        ElMessage.error(errorMessage)
      }
    } else {
      ElMessage.info('已取消删除')
    }
  }
}

// 处理页码变化
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  // 加载数据
}

// 处理每页条数变化
const handleSizeChange = (val: number) => {
  pageSize.value = val
  // 加载数据
}

onMounted(() => {
  // 初始加载数据
})
</script>

<style scoped>
.agent-list-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>