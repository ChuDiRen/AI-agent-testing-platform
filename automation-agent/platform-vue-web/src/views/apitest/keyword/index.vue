<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <Breadcrumb />
      
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="关键字名称：">
          <el-input v-model="searchForm.name" placeholder="根据关键字名称筛选"/>
        </el-form-item>

        <el-form-item label="操作类型ID：">
          <el-select v-model="searchForm.operation_type_id" placeholder="选择所属类型" clearable>
            <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>     
          </el-select>
        </el-form-item>

        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button type="warning" @click="onDataForm(-1)">新增关键字方法</el-button>
        </el-row>
      </el-form>

      <el-table :data="tableData" style="width: 100%" max-height="500">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" :show-overflow-tooltip="true">
          <template #default="scope" v-if="col.prop === 'is_enabled'">
            {{ scope.row.is_enabled === true ? "是" : scope.row.is_enabled === false ? "否" : "-" }}
          </template>
        </el-table-column>
        
        <el-table-column fixed="right" label="操作">
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
      
      <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px">
        <el-form-item label="关键字编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="关键字名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入关键字名称" />
        </el-form-item>
        <el-form-item label="关键字描述" prop="keyword_desc">
          <el-input v-model="ruleForm.keyword_desc" type="textarea" placeholder="请输入关键字描述" />
        </el-form-item>
        <el-form-item label="操作类型" prop="operation_type_id">
          <el-select v-model="ruleForm.operation_type_id" placeholder="选择操作类型">
            <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>
          </el-select>
        </el-form-item>
        <el-form-item label="是否启用" prop="is_enabled">
          <el-select v-model="ruleForm.is_enabled" placeholder="选择是否启用">
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm()">提交</el-button>
          <el-button @click="resetForm()">重置</el-button>
          <el-button @click="onCancel()">关闭</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData, queryById, insertData, updateData } from '@/api/ApiKeyWord'
import { queryAll } from '@/api/ApiOperationType'
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
const searchForm = reactive({ name: "", operation_type_id: "" })

const columnList = ref([
  { prop: "id", label: '关键字编号' },
  { prop: "name", label: '关键字名称' },
  { prop: "keyword_desc", label: '关键字描述' },
  { prop: "operation_type_id", label: '操作类型' },
  { prop: "is_enabled", label: '是否启用' },
  { prop: "created_at", label: '创建时间' },
  { prop: "updated_at", label: '更新时间' }
])

const tableData = ref([])
const operationTypeList = ref([])

const loadData = () => {
  let searchData = searchForm
  searchData["page"] = currentPage.value
  searchData["pageSize"] = pageSize.value

  queryByPage(searchData).then((res) => {
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
  const keywordId = tableData.value[index]["id"]
  const keywordName = tableData.value[index]["name"]

  await confirmDelete(
    () => deleteData(keywordId),
    `确定要删除关键字 "${keywordName}" 吗？此操作不可恢复！`,
    '关键字删除成功',
    loadData
  )
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  id: 0,
  name: '',
  keyword_desc: '',
  operation_type_id: '',
  is_enabled: true
})

const rules = reactive({
  name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  operation_type_id: [
    { required: true, message: '必填项', trigger: 'change' }
  ]
})

const loadFormData = async (id) => {
  const res = await queryById(id)
  ruleForm.id = res.data.data.id
  ruleForm.name = res.data.data.name
  ruleForm.keyword_desc = res.data.data.keyword_desc
  ruleForm.operation_type_id = res.data.data.operation_type_id
  ruleForm.is_enabled = res.data.data.is_enabled
}

const resetForm = () => {
  ruleForm.id = 0
  ruleForm.name = ''
  ruleForm.keyword_desc = ''
  ruleForm.operation_type_id = ''
  ruleForm.is_enabled = true
}

const submitForm = () => {
  if (!ruleFormRef.value) return
  ruleFormRef.value.validate((valid) => {
    if (!valid) return
    
    if (ruleForm.id > 0) {
      updateData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('更新成功')
          currentView.value = 'list'
          loadData()
        }
      })
    } else {
      insertData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('添加成功')
          currentView.value = 'list'
          loadData()
        }
      })
    }
  })
}

const onCancel = () => {
  currentView.value = 'list'
  loadData()
}

// ========== 初始化 ==========
onMounted(() => {
  loadData()
  // 加载操作类型列表
  queryAll().then((res) => {
    operationTypeList.value = res.data.data
  })
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
