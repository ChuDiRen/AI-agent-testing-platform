<template>
  <div class="test-reports-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>测试报告管理</span>
          <el-button type="primary" @click="handleGenerateReport">生成报告</el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="报告名称" />
        <el-table-column prop="testCase" label="关联用例" />
        <el-table-column prop="passRate" label="通过率">
          <template #default="scope">
            <el-progress :percentage="scope.row.passRate" :status="getPassRateStatus(scope.row.passRate)" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleView(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="handleExport(scope.row)">导出</el-button>
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
    name: '登录功能测试报告',
    testCase: '登录功能测试',
    passRate: 100,
    status: '已完成',
    createTime: '2025-08-20 10:30:00'
  },
  {
    id: 2,
    name: '用户管理测试报告',
    testCase: '用户管理测试',
    passRate: 75,
    status: '已完成',
    createTime: '2025-08-20 12:00:00'
  },
  {
    id: 3,
    name: '权限验证测试报告',
    testCase: '权限验证测试',
    passRate: 0,
    status: '生成中',
    createTime: '2025-08-21 09:30:00'
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
    case '已完成':
      return 'success'
    case '生成中':
      return 'info'
    case '失败':
      return 'danger'
    default:
      return ''
  }
}

// 获取通过率对应的状态
const getPassRateStatus = (passRate: number) => {
  if (passRate >= 90) {
    return 'success'
  } else if (passRate >= 60) {
    return 'warning'
  } else {
    return 'exception'
  }
}

// 处理生成报告
const handleGenerateReport = () => {
  ElMessage.info('生成报告功能待实现')
}

// 处理查看
const handleView = (row: any) => {
  ElMessage.info(`查看报告: ${row.name}`)
}

// 处理导出
const handleExport = (row: any) => {
  ElMessage.success(`导出报告: ${row.name}`)
}

// 处理删除
const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除报告 "${row.name}" 吗?`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ElMessage.success(`删除报告: ${row.name}`)
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
.test-reports-container {
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