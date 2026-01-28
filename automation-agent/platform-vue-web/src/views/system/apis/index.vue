<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <Breadcrumb />
      <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="API名称">
          <el-input v-model="searchForm.name" placeholder="根据API名称筛选" />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button type="warning" @click="onDataForm(-1)">新增API</el-button>
        </el-row>
      </el-form>

      <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="API名称" width="150" />
        <el-table-column prop="path" label="路径" width="200" />
        <el-table-column prop="method" label="方法" width="100" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column fixed="right" label="操作" width="150">
          <template #default="scope">
            <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </div>

    <!-- 表单视图 -->
    <div v-else>
      <Breadcrumb />
      <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="编号" prop="id">
          <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="API名称" prop="name">
          <el-input v-model="ruleForm.name" />
        </el-form-item>
        <el-form-item label="路径" prop="path">
          <el-input v-model="ruleForm.path" />
        </el-form-item>
        <el-form-item label="方法" prop="method">
          <el-select v-model="ruleForm.method" placeholder="选择HTTP方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="ruleForm.is_active" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
          <el-button @click="resetForm(ruleFormRef)">清空</el-button>
          <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import apiApi from '@/api/apiApi'
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

// 视图控制
const currentView = ref('list')

// ========== 列表相关数据 ==========
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ name: "" })

const tableData = ref([])

const loadData = () => {
  let searchData = searchForm
  searchData["page"] = currentPage.value
  searchData["pageSize"] = pageSize.value

  apiApi.queryByPage(searchData).then((res) => {
    tableData.value = res.data.data
    total.value = res.data.total
  })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadData()
}

const onDataForm = (index) => {
  currentView.value = 'form'
  if (index >= 0) {
    loadFormData(tableData.value[index]["id"])
  } else {
    resetForm()
  }
}

const onDelete = async (index) => {
  const apiId = tableData.value[index]["id"]
  const apiName = tableData.value[index]["name"]

  await confirmDelete(
    () => apiApi.deleteData(apiId),
    `确定要删除API "${apiName}" 吗？此操作不可恢复！`,
    'API删除成功',
    loadData
  )
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  id: 0,
  name: '',
  path: '',
  method: '',
  is_active: true
})

const rules = reactive({
  name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  path: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '必填项', trigger: 'change' }
  ]
})

const loadFormData = async (id) => {
  const res = await apiApi.queryById(id)
  ruleForm.id = res.data.data.id
  ruleForm.name = res.data.data.name
  ruleForm.path = res.data.data.path
  ruleForm.method = res.data.data.method
  ruleForm.is_active = res.data.data.is_active
}

const resetForm = () => {
  ruleForm.id = 0
  ruleForm.name = ''
  ruleForm.path = ''
  ruleForm.method = ''
  ruleForm.is_active = true
}

const submitForm = async (form) => {
  if (!form) return
  await form.validate((valid, fields) => {
    if (!valid) return
    
    if (ruleForm.id > 0) {
      apiApi.updateData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('更新成功')
          currentView.value = 'list'
          loadData()
        }
      })
    } else {
      apiApi.insertData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('添加成功')
          currentView.value = 'list'
          loadData()
        }
      })
    }
  })
}

const resetFormFields = (form) => {
  if (!form) return
  form.resetFields()
}

const closeForm = () => {
  currentView.value = 'list'
  loadData()
}

// ========== 初始化 ==========
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
  margin-top: 10px;
}

.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}
</style>
