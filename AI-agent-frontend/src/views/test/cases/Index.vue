<template>
  <div class="test-cases-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>测试用例管理</span>
          <el-button type="primary" @click="handleAddCase">新增用例</el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="category" label="分类" />
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="success" @click="handleRun(scope.row)">执行</el-button>
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
    name: '登录功能测试',
    description: '验证用户登录功能是否正常',
    category: '功能测试',
    status: '通过',
    createTime: '2025-08-20 10:00:00'
  },
  {
    id: 2,
    name: '用户管理测试',
    description: '验证用户增删改查功能',
    category: '功能测试',
    status: '失败',
    createTime: '2025-08-20 11:30:00'
  },
  {
    id: 3,
    name: '权限验证测试',
    description: '验证RBAC权限控制是否生效',
    category: '安全测试',
    status: '待执行',
    createTime: '2025-08-21 09:15:00'
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
    case '通过':
      return 'success'
    case '失败':
      return 'danger'
    case '待执行':
      return 'info'
    default:
      return ''
  }
}

// 处理新增用例
const handleAddCase = () => {
  ElMessage.info('新增用例功能待实现')
}

// 处理编辑
const handleEdit = (row: any) => {
  ElMessage.info(`编辑用例: ${row.name}`)
}

// 处理执行
const handleRun = (row: any) => {
  ElMessage.success(`开始执行用例: ${row.name}`)
}

// 处理删除
const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除用例 "${row.name}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success(`删除用例: ${row.name}`)
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
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
.test-cases-container {
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