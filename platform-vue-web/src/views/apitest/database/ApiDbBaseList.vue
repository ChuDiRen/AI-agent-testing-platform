<template>
  <div class="db-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据库配置</span>
          <el-button type="primary" @click="handleAdd">新增配置</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="配置名称" />
        <el-table-column prop="db_type" label="数据库类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.db_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="所属项目" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleTest(row)">测试连接</el-button>
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        @current-change="loadData"
        layout="total, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <ApiDbBaseForm :id="currentId" @success="handleSuccess" @cancel="dialogVisible = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from '@/axios'
import ApiDbBaseForm from './ApiDbBaseForm.vue'

const loading = ref(false)
const tableData = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentId = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await axios.post('/ApiDbBase/queryByPage', {
      page: page.value,
      pageSize: pageSize.value
    })
    if (data.code === 200) {
      tableData.value = data.data.list
      total.value = data.data.total
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增数据库配置'
  currentId.value = null
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑数据库配置'
  currentId.value = row.id
  dialogVisible.value = true
}

const handleTest = async (row) => {
  try {
    const { data } = await axios.post('/ApiDbBase/testConnection', { id: row.id })
    if (data.code === 200) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error('连接失败: ' + data.msg)
    }
  } catch (error) {
    ElMessage.error('测试失败: ' + error.message)
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定删除该配置吗?', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      const { data } = await axios.delete(`/ApiDbBase/delete?id=${row.id}`)
      if (data.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      }
    } catch (error) {
      ElMessage.error('删除失败: ' + error.message)
    }
  })
}

const handleSuccess = () => {
  dialogVisible.value = false
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
