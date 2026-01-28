<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <Breadcrumb />
      
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="管理名称：">
          <el-input v-model="searchForm.name" placeholder="根据管理名称筛选" />
        </el-form-item>

        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button type="warning" @click="onDataForm(-1)">新增管理</el-button>
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
        <el-form-item label="管理编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="管理名称" prop="name">
          <el-input v-model="ruleForm.name" placeholder="请输入管理名称" />
        </el-form-item>
        <el-form-item label="管理描述" prop="desc">
          <el-input v-model="ruleForm.desc" type="textarea" placeholder="请输入管理描述" />
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
import { queryByPage, deleteData, queryById, insertData, updateData } from '@/api/ApiMateManage'
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

const columnList = ref([
  { prop: "id", label: '管理编号' },
  { prop: "name", label: '管理名称' },
  { prop: "desc", label: '管理描述' },
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
  const manageId = tableData.value[index]["id"]
  const manageName = tableData.value[index]["name"]

  await confirmDelete(
    () => deleteData(manageId),
    `确定要删除管理 "${manageName}" 吗？此操作不可恢复！`,
    '管理删除成功',
    loadData
  )
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  id: 0,
  name: '',
  desc: ''
})

const rules = reactive({
  name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ]
})

const loadFormData = async (id) => {
  const res = await queryById(id)
  ruleForm.id = res.data.data.id
  ruleForm.name = res.data.data.name
  ruleForm.desc = res.data.data.desc
}

const resetForm = () => {
  ruleForm.id = 0
  ruleForm.name = ''
  ruleForm.desc = ''
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
