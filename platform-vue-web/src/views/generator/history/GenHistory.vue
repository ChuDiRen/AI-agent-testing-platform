<template>
  <div class="page-container">
    <BaseSearch
      :model="searchForm"
      @search="loadData"
      @reset="resetSearch"
    >
      <el-form-item label="表名">
        <el-input v-model="searchForm.table_name" placeholder="根据表名筛选" clearable />
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="代码生成历史"
      :data="tableData"
      :loading="loading"
      :total="total"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="danger" @click="batchDelete" :disabled="selectedRows.length === 0">
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
      </template>

      <!-- 数据列 -->
      <el-table-column type="selection" width="55" @selection-change="handleSelectionChange" />
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="table_name" label="表名" width="150" show-overflow-tooltip />
      <el-table-column prop="table_comment" label="表注释" width="200" show-overflow-tooltip />
      <el-table-column prop="gen_type" label="生成类型" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.gen_type === '0'" type="info">ZIP压缩包</el-tag>
          <el-tag v-else type="warning">自定义路径</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="file_count" label="文件数量" width="100" />
      <el-table-column prop="create_time" label="生成时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="150">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDownload(scope.$index)">
            下载
          </el-button>
          <el-button link type="danger" size="small" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData } from './genhistory'
import { useRouter } from "vue-router";
import { formatDateTime } from '~/utils/timeFormatter'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = reactive({
  page: 1,
  pageSize: 10
})
const total = ref(0)
const loading = ref(false)

// 搜索功能 - 筛选表单
const searchForm = reactive({
  table_name: null
})

// 表格数据
const tableData = ref([])
const selectedRows = ref<any[]>([])

// 加载页面数据
const loadData = () => {
  loading.value = true
  let searchData = { ...searchForm }
  searchData["page"] = pagination.page
  searchData["pageSize"] = pagination.pageSize

  queryByPage(searchData).then((res: { data: { code: number; data: never[]; total: number; msg: string }; }) => {
    if (res.data.code === 200) {
      tableData.value = res.data.data || []
      total.value = res.data.total || 0
    } else {
      ElMessage.error(res.data.msg || '查询失败')
    }
  }).catch(() => {
    ElMessage.error('查询失败，请稍后重试')
  }).finally(() => {
    loading.value = false
  })
}

// 重置搜索
const resetSearch = () => {
  searchForm.table_name = null
  pagination.page = 1
  loadData()
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection
}

// 下载历史代码
const onDownload = (index: number) => {
  const item = tableData.value[index]
  ElMessage.info('下载功能需要后端支持文件存储')
}

// 删除历史记录
const onDelete = (index: number) => {
  const item = tableData.value[index]
  ElMessageBox.confirm(
    `确定要删除"${item.table_name}"的生成历史吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteData(item.id).then((res: { data: { code: number; msg: string } }) => {
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.data.msg || '删除失败')
      }
    }).catch(() => {
      ElMessage.error('删除失败，请稍后重试')
    })
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 批量删除
const batchDelete = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的记录')
    return
  }
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.length} 条记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    const ids = selectedRows.value.map((row: any) => row.id)
    // 这里需要后端支持批量删除接口
    ElMessage.info('批量删除功能需要后端支持')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 页面初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
</style>
