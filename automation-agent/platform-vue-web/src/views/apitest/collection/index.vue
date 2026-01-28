<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <Breadcrumb />
      
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="集合名称：">
          <el-input v-model="searchForm.collection_name" placeholder="根据集合名称筛选" />
        </el-form-item>

        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button type="warning" @click="onDataForm(-1)">新增集合</el-button>
        </el-row>
      </el-form>

      <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
          :show-overflow-tooltip="true" />
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
        <el-form-item label="集合编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="集合名称" prop="collection_name">
          <el-input v-model="ruleForm.collection_name" placeholder="请输入集合名称" />
        </el-form-item>
        <el-form-item label="集合描述" prop="collection_desc">
          <el-input v-model="ruleForm.collection_desc" type="textarea" placeholder="请输入集合描述" />
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
import { queryByPage, deleteData, queryById, insertData, updateData } from '@/api/ApiCollectionInfo'
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
const searchForm = reactive({ collection_name: "" })

const columnList = ref([
  { prop: "id", label: '集合编号' },
  { prop: "collection_name", label: '集合名称' },
  { prop: "collection_desc", label: '集合描述' },
  { prop: "created_at", label: '创建时间' },
  { prop: "updated_at", label: '更新时间' }
])

const tableData = ref([])

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
  const collectionId = tableData.value[index]["id"]
  const collectionName = tableData.value[index]["collection_name"]

  await confirmDelete(
    () => deleteData(collectionId),
    `确定要删除集合 "${collectionName}" 吗？此操作不可恢复！`,
    '集合删除成功',
    loadData
  )
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  id: 0,
  collection_name: '',
  collection_desc: ''
})

const rules = reactive({
  collection_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ]
})

const loadFormData = async (id) => {
  const res = await queryById(id)
  ruleForm.id = res.data.data.id
  ruleForm.collection_name = res.data.data.collection_name
  ruleForm.collection_desc = res.data.data.collection_desc
}

const resetForm = () => {
  ruleForm.id = 0
  ruleForm.collection_name = ''
  ruleForm.collection_desc = ''
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
