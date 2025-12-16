<template>
  <div class="page-container">
    <!-- 表格区域 -->
    <BaseTable 
      title="数据库配置"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增配置
        </el-button>
      </template>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="配置名称" show-overflow-tooltip />
      <el-table-column prop="ref_name" label="引用名称" width="120" show-overflow-tooltip />
      <el-table-column prop="db_type" label="数据库类型" width="120">
        <template #default="{ row }">
          <el-tag>{{ row.db_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_enabled" label="状态" width="100">
        <template #default="{ row }">
          <el-switch 
            v-model="row.is_enabled" 
            active-value="1" 
            inactive-value="0"
            @change="handleToggleEnabled(row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="project_name" label="所属项目" show-overflow-tooltip />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleTest(row)">测试连接</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <ApiDbBaseForm :id="currentId" @success="handleSuccess" @cancel="dialogVisible = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { queryByPage, deleteData, testConnection, toggleEnabled } from '../project/dbBase'
import ApiDbBaseForm from './ApiDbBaseForm.vue'
import BaseTable from '~/components/BaseTable/index.vue'

// 分页参数
const pagination = ref({ page: 1, limit: 10 })
const total = ref(0)
const loading = ref(false)

// 表格数据
const tableData = ref([])

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('')
const currentId = ref(null)

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await queryByPage({
      page: pagination.value.page,
      pageSize: pagination.value.limit
    })
    if (data.code === 200) {
      tableData.value = data.data.list || data.data || []
      total.value = data.data.total || data.total || 0
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
    const { data } = await testConnection({ id: row.id })
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
      const { data } = await deleteData(row.id)
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

const handleToggleEnabled = async (row) => {
  try {
    const { data } = await toggleEnabled(row.id, row.is_enabled)
    if (data.code === 200) {
      ElMessage.success(data.msg || '操作成功')
    } else {
      ElMessage.error(data.msg || '操作失败')
      // 恢复原状态
      row.is_enabled = row.is_enabled === '1' ? '0' : '1'
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
    row.is_enabled = row.is_enabled === '1' ? '0' : '1'
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>
