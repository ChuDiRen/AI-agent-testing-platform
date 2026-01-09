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
      <el-form-item label="表注释">
        <el-input v-model="searchForm.table_comment" placeholder="根据表注释筛选" clearable />
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="代码生成-表配置"
      :data="tableData"
      :loading="loading"
      :total="total"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" v-permission="'generator:table:import'" @click="openImportDialog">
          <el-icon><Plus /></el-icon>
          导入表
        </el-button>
        <el-button type="success" v-permission="'generator:table:import'" @click="batchImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="warning" v-permission="'generator:table:import'" @click="showUploadDialog = true">
          <el-icon><Document /></el-icon>
          上传SQL文件
        </el-button>
      </template>

      <!-- 数据列 -->
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="table_name" label="表名" width="150" show-overflow-tooltip />
      <el-table-column prop="table_comment" label="表注释" width="200" show-overflow-tooltip />
      <el-table-column prop="class_name" label="类名" width="120" />
      <el-table-column prop="function_name" label="功能名称" width="150" show-overflow-tooltip />
      <el-table-column prop="tpl_category" label="模板类型" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.tpl_category === 'tree'" type="success">树表</el-tag>
          <el-tag v-else-if="scope.row.tpl_category === 'main_sub'" type="warning">主子表</el-tag>
          <el-tag v-else type="info">单表</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="导入时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="300">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDataView(scope.$index)">
            查看
          </el-button>
          <el-button link type="success" size="small" v-permission="'generator:code:generate'" @click.prevent="onGenerateCode(scope.$index)">
            生成代码
          </el-button>
          <el-button link type="warning" size="small" v-permission="'generator:table:edit'" @click.prevent="onDataEdit(scope.$index)">
            编辑
          </el-button>
          <el-button link type="danger" size="small" v-permission="'generator:table:delete'" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 导入表对话框 -->
    <el-dialog v-model="showDbTablesDialog" title="导入表配置" width="60%">
      <el-table
        :data="dbTables"
        style="width: 100%; max-height: 400px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="table_name" label="表名" />
        <el-table-column prop="table_comment" label="表注释" />
      </el-table>
      <template #footer>
        <el-button @click="showDbTablesDialog = false">取消</el-button>
        <el-button type="primary" @click="importTables" :loading="importLoading">
          导入选中表
        </el-button>
      </template>
    </el-dialog>

    <!-- 上传SQL文件对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传SQL文件" width="500px">
      <div class="upload-container">
        <el-upload
          ref="uploadRef"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".sql"
          :on-change="handleFileChange"
          :on-exceed="handleExceed"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            拖拽 SQL 文件到此处，或 <em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 .sql 文件，自动解析 CREATE TABLE 语句
            </div>
          </template>
        </el-upload>
      </div>
      <template #footer>
        <el-button @click="closeUploadDialog">取消</el-button>
        <el-button type="primary" @click="submitUpload" :loading="uploadLoading" :disabled="!selectedFile">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData, getDbTables, importTables as importTablesApi, uploadSqlFile } from './gentable.js'
import { useRouter } from "vue-router";
import { formatDateTime } from '~/utils/timeFormatter'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
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
  table_name: null,
  table_comment: null
})

// 表格数据
const tableData = ref([])

// 导入表对话框
const showDbTablesDialog = ref(false)
const dbTables = ref([])
const selectedTables = ref([])
const importLoading = ref(false)

// 上传SQL文件对话框
const showUploadDialog = ref(false)
const uploadLoading = ref(false)
const selectedFile = ref(null)
const uploadRef = ref()

// 加载页面数据
const loadData = () => {
  loading.value = true
  let searchData = { ...searchForm }
  searchData["page"] = pagination.page
  searchData["pageSize"] = pagination.pageSize

  queryByPage(searchData).then((res) => {
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
  searchForm.table_comment = null
  pagination.page = 1
  loadData()
}

// 页面初始化
onMounted(() => {
  loadData()
})

// 查看表配置详情
const onDataView = (index) => {
  const item = tableData.value[index]
  router.push({
    path: '/GenTableForm',
    query: {
      id: item.id,
      view: 'true'
    }
  })
}

// 编辑表配置
const onDataEdit = (index) => {
  const item = tableData.value[index]
  router.push({
    path: '/GenTableForm',
    query: {
      id: item.id
    }
  })
}

// 生成代码
const onGenerateCode = (index) => {
  const item = tableData.value[index]
  router.push({
    path: 'GeneratorCode',
    query: {
      table_id: item.id
    }
  })
}

// 删除表配置
const onDelete = (index) => {
  const item = tableData.value[index]
  ElMessageBox.confirm(
    `确定要删除表配置"${item.table_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteData(item.id).then((res) => {
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

// 加载数据库表列表
const loadDbTables = async () => {
  try {
    const res = await getDbTables()
    if (res.data.code === 200) {
      dbTables.value = res.data.data || []
    }
  } catch (error) {
    ElMessage.error('获取数据库表列表失败')
  }
}

// 选择表变化
const handleSelectionChange = (selection) => {
  selectedTables.value = selection
}

// 导入选中的表
const importTables = async () => {
  if (selectedTables.value.length === 0) {
    ElMessage.warning('请先选择要导入的表')
    return
  }
  importLoading.value = true
  try {
    const tableNames = selectedTables.value.map((item) => item.table_name)
    const res = await importTablesApi(tableNames)
    if (res.data.code === 200) {
      ElMessage.success(`成功导入 ${res.data.data} 个表`)
      showDbTablesDialog.value = false
      loadData()
    } else {
      ElMessage.error(res.data.msg || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败，请稍后重试')
  } finally {
    importLoading.value = false
  }
}

// 批量导入
const batchImport = () => {
  showDbTablesDialog.value = true
  loadDbTables()
}

// 打开导入对话框
const openImportDialog = () => {
  showDbTablesDialog.value = true
  loadDbTables()
}

// 处理文件选择变化
const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

// 处理超出文件数量限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件，请先移除已选文件')
}

// 关闭上传对话框
const closeUploadDialog = () => {
  showUploadDialog.value = false
  selectedFile.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 提交上传
const submitUpload = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择SQL文件')
    return
  }
  
  uploadLoading.value = true
  try {
    const res = await uploadSqlFile(selectedFile.value)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '导入成功')
      closeUploadDialog()
      loadData()
    } else {
      ElMessage.error(res.data.msg || '导入失败')
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.msg || '上传失败，请稍后重试')
  } finally {
    uploadLoading.value = false
  }
}
</script>

<style scoped>
.upload-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.upload-container :deep(.el-upload-dragger) {
  width: 400px;
}
</style>
