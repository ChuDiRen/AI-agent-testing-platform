<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <!-- 面包屑导航 -->
      <Breadcrumb />
      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="根据用户名筛选" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="根据邮箱筛选" />
        </el-form-item>
        <el-form-item label="部门">
          <el-tree-select v-model="searchForm.dept_id" :data="deptOptions" :props="{ label: 'name', value: 'id' }"
            placeholder="选择部门" clearable check-strictly />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" style="width: 100%;" max-height="500" v-loading="loading" element-loading-text="加载中...">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="alias" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="角色" width="200">
          <template #default="scope">
            <el-tag v-for="role in scope.row.roles" :key="role.id" type="info" style="margin: 2px">
              {{ role.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="部门" width="150">
          <template #default="scope">
            {{ scope.row.dept?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="超级用户" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_superuser ? 'success' : 'info'">
              {{ scope.row.is_superuser ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用状态" width="100" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
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

      <!-- 分页 -->
      <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </div>

    <!-- 表单视图 -->
    <div v-else>
      <!-- 面包屑导航 -->
      <Breadcrumb />
      <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="编号" prop="id">
          <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="ruleForm.username" />
        </el-form-item>
        <el-form-item label="姓名" prop="alias">
          <el-input v-model="ruleForm.alias" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="ruleForm.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="ruleForm.phone" />
        </el-form-item>
        <el-form-item v-if="ruleForm.id === 0" label="密码" prop="password">
          <el-input v-model="ruleForm.password" type="password" show-password placeholder="新增用户时必填" />
        </el-form-item>
        <el-form-item label="角色" prop="role_ids">
          <el-checkbox-group v-model="ruleForm.role_ids">
            <el-checkbox v-for="role in roleOptions" :key="role.id" :value="role.id">
              {{ role.name }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="部门" prop="dept_id">
          <el-tree-select v-model="ruleForm.dept_id" :data="deptOptions" :props="{ label: 'name', value: 'id' }"
            placeholder="请选择部门" clearable check-strictly />
        </el-form-item>
        <el-form-item label="超级用户">
          <el-switch v-model="ruleForm.is_superuser" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="ruleForm.is_active" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">
            提交
          </el-button>
          <el-button @click="resetForm(ruleFormRef)">清空</el-button>
          <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import userApi from '@/api/userApi'
import roleApi from '@/api/roleApi'
import deptApi from '@/api/deptApi'
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
const loading = ref(false)
const searchForm = reactive({ username: "", email: "", dept_id: "" })

const tableData = ref([])
const deptOptions = ref([])
const roleOptions = ref([])

const loadData = () => {
  loading.value = true
  let searchData = searchForm
  searchData["page"] = currentPage.value
  searchData["pageSize"] = pageSize.value

  userApi.queryByPage(searchData).then((res) => {
    tableData.value = res.data.data
    total.value = res.data.total
    loading.value = false
  }).catch(() => {
    loading.value = false
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
  const userId = tableData.value[index]["id"]
  const username = tableData.value[index]["username"]

  await confirmDelete(
    () => userApi.deleteData(userId),
    `确定要删除用户 "${username}" 吗？此操作不可恢复！`,
    '用户删除成功',
    loadData
  )
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  id: 0,
  username: '',
  alias: '',
  email: '',
  phone: '',
  password: '',
  role_ids: [],
  dept_id: '',
  is_superuser: false,
  is_active: true
})

const rules = reactive({
  username: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  alias: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '必填项', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '必填项', trigger: 'blur' }
  ]
})

const loadFormData = async (id) => {
  const res = await userApi.queryById(id)
  ruleForm.id = res.data.data.id
  ruleForm.username = res.data.data.username
  ruleForm.alias = res.data.data.alias
  ruleForm.email = res.data.data.email
  ruleForm.phone = res.data.data.phone
  ruleForm.role_ids = res.data.data.role_ids || []
  ruleForm.dept_id = res.data.data.dept_id
  ruleForm.is_superuser = res.data.data.is_superuser
  ruleForm.is_active = res.data.data.is_active
}

const resetForm = () => {
  ruleForm.id = 0
  ruleForm.username = ''
  ruleForm.alias = ''
  ruleForm.email = ''
  ruleForm.phone = ''
  ruleForm.password = ''
  ruleForm.role_ids = []
  ruleForm.dept_id = ''
  ruleForm.is_superuser = false
  ruleForm.is_active = true
}

const submitForm = async (form) => {
  if (!form) return
  await form.validate((valid, fields) => {
    if (!valid) return
    
    if (ruleForm.id > 0) {
      userApi.updateData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('更新成功')
          currentView.value = 'list'
          loadData()
        }
      })
    } else {
      userApi.insertData(ruleForm).then((res) => {
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
  // 加载角色列表
  roleApi.queryAll().then((res) => {
    roleOptions.value = res.data.data
  })
  // 加载部门列表
  deptApi.queryAll().then((res) => {
    deptOptions.value = res.data.data
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
