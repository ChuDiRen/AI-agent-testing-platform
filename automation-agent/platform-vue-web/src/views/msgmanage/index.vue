<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <Breadcrumb />
      <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="消息类型">
          <el-select v-model="searchForm.msg_type" placeholder="选择消息类型" clearable>
            <el-option label="钉钉" value="dingding" />
            <el-option label="飞书" value="feishu" />
            <el-option label="微信" value="wechat" />
          </el-select>
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button type="warning" @click="onDataForm(-1)">新增消息</el-button>
        </el-row>
      </el-form>

      <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="msg_name" label="消息名称" width="150" />
        <el-table-column prop="msg_type" label="消息类型" width="100">
          <template #default="scope">
            <el-tag :type="getMsgTypeTag(scope.row.msg_type)">
              {{ getMsgTypeText(scope.row.msg_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="webhook_url" label="Webhook地址" show-overflow-tooltip />
        <el-table-column label="状态" width="100" align="center">
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

      <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
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
        <el-form-item label="消息名称" prop="msg_name">
          <el-input v-model="ruleForm.msg_name" />
        </el-form-item>
        <el-form-item label="消息类型" prop="msg_type">
          <el-select v-model="ruleForm.msg_type" placeholder="选择消息类型">
            <el-option label="钉钉" value="dingding" />
            <el-option label="飞书" value="feishu" />
            <el-option label="微信" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="Webhook地址" prop="webhook_url">
          <el-input v-model="ruleForm.webhook_url" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="密钥" prop="secret">
          <el-input v-model="ruleForm.secret" type="password" show-password />
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
import { queryByPage, deleteData, queryById, insertData, updateData } from '@/api/ApiRobotMsg'
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

// 视图控制
const currentView = ref('list')

// ========== 列表相关数据 ==========
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ msg_type: "" })

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
  const msgId = tableData.value[index]["id"]
  const msgName = tableData.value[index]["msg_name"]

  await confirmDelete(
    () => deleteData(msgId),
    `确定要删除消息 "${msgName}" 吗？此操作不可恢复！`,
    '消息删除成功',
    loadData
  )
}

const getMsgTypeTag = (type) => {
  const tagMap = {
    'dingding': 'primary',
    'feishu': 'success',
    'wechat': 'warning'
  }
  return tagMap[type] || 'info'
}

const getMsgTypeText = (type) => {
  const textMap = {
    'dingding': '钉钉',
    'feishu': '飞书',
    'wechat': '微信'
  }
  return textMap[type] || type
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  id: 0,
  msg_name: '',
  msg_type: '',
  webhook_url: '',
  secret: '',
  is_active: true
})

const rules = reactive({
  msg_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  msg_type: [
    { required: true, message: '必填项', trigger: 'change' }
  ],
  webhook_url: [
    { required: true, message: '必填项', trigger: 'blur' },
    { type: 'url', message: '请输入正确的URL地址', trigger: 'blur' }
  ]
})

const loadFormData = async (id) => {
  const res = await queryById(id)
  ruleForm.id = res.data.data.id
  ruleForm.msg_name = res.data.data.msg_name
  ruleForm.msg_type = res.data.data.msg_type
  ruleForm.webhook_url = res.data.data.webhook_url
  ruleForm.secret = res.data.data.secret
  ruleForm.is_active = res.data.data.is_active
}

const resetForm = () => {
  ruleForm.id = 0
  ruleForm.msg_name = ''
  ruleForm.msg_type = ''
  ruleForm.webhook_url = ''
  ruleForm.secret = ''
  ruleForm.is_active = true
}

const submitForm = async (form) => {
  if (!form) return
  await form.validate((valid, fields) => {
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
