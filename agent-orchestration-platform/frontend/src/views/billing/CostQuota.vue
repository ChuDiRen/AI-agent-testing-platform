<template>
  <div class="cost-quota-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>成本配额管理</span>
          <el-button type="primary" @click="showCreateDialog">新建配额</el-button>
        </div>
      </template>

      <el-table
        :data="quotas"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="agent_name" label="Agent" width="150" />
        <el-table-column prop="user_name" label="用户" width="150" />
        <el-table-column prop="monthly_limit" label="每月限额（元）" width="150" />
        <el-table-column prop="current_usage" label="当月已用（元）" width="150">
          <template #default="{ row }">
            <span :class="{ 'warning-text': row.current_usage >= row.monthly_limit * 0.8 }">
              {{ row.current_usage.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="current_percent" label="使用率" width="120">
          <template #default="{ row }">
            <el-progress
              :percentage="row.current_percent"
              :status="getProgressStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="alert_threshold" label="预警阈值（%）" width="120" />
        <el-table-column prop="alert_enabled" label="预警启用" width="100">
          <template #default="{ row }">
            <el-tag :type="row.alert_enabled ? 'success' : 'info'">
              {{ row.alert_enabled ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="overage_enabled" label="超额扣费" width="100">
          <template #default="{ row }">
            <el-tag :type="row.overage_enabled ? 'success' : 'info'">
              {{ row.overage_enabled ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="showEditDialog(row)">编辑</el-button>
            <el-button
              size="small"
              type="danger"
              @click="handleDelete(row)"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建配额' : '编辑配额'"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="Agent" prop="agent_id">
          <el-select v-model="form.agent_id" placeholder="选择 Agent">
            <el-option
              v-for="agent in agents"
              :key="agent.id"
              :label="agent.name"
              :value="agent.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用户" prop="user_id">
          <el-select v-model="form.user_id" placeholder="选择用户（可选）" clearable>
            <el-option
              v-for="user in users"
              :key="user.id"
              :label="user.full_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="每月限额" prop="monthly_limit">
          <el-input-number
            v-model="form.monthly_limit"
            :min="0"
            :precision="2"
            :step="10"
          />
          <span style="margin-left: 10px">元</span>
        </el-form-item>

        <el-form-item label="重置日期" prop="reset_day">
          <el-input-number
            v-model="form.reset_day"
            :min="1"
            :max="31"
          />
          <span style="margin-left: 10px">日</span>
        </el-form-item>

        <el-form-item label="预警阈值" prop="alert_threshold">
          <el-slider
            v-model="form.alert_threshold"
            :min="0"
            :max="1"
            :step="0.05"
            :marks="{ 0.8: '80%', 0.9: '90%', 1.0: '100%' }"
            show-tooltip
          />
        </el-form-item>

        <el-form-item label="启用预警">
          <el-switch v-model="form.alert_enabled" />
        </el-form-item>

        <el-form-item label="启用超额">
          <el-switch v-model="form.overage_enabled" />
        </el-form-item>

        <el-form-item label="超额费率" prop="overage_rate">
          <el-input-number
            v-model="form.overage_rate"
            :min="1"
            :precision="1"
            :step="0.1"
          />
          <span style="margin-left: 10px">倍</span>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCostQuotas, createCostQuota, updateCostQuota, deleteCostQuota } from '@/api'

const quotas = ref([])
const agents = ref([])
const users = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref('create')
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  agent_id: null,
  user_id: null,
  monthly_limit: 100,
  reset_day: 1,
  alert_threshold: 0.8,
  alert_enabled: true,
  overage_enabled: false,
  overage_rate: 1.5
})

const rules = {
  agent_id: [{ required: true, message: '请选择 Agent', trigger: 'change' }],
  monthly_limit: [
    { required: true, message: '请输入每月限额', trigger: 'blur' },
    { type: 'number', min: 0, message: '限额不能小于 0', trigger: 'blur' }
  ],
  alert_threshold: [
    { required: true, message: '请输入预警阈值', trigger: 'blur' },
    { type: 'number', min: 0, max: 1, message: '阈值在 0 到 1 之间', trigger: 'blur' }
  ],
  overage_rate: [
    { required: true, message: '请输入超额费率', trigger: 'blur' },
    { type: 'number', min: 1, message: '费率不能小于 1', trigger: 'blur' }
  ]
}

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const loadQuotas = async () => {
  loading.value = true
  try {
    const response = await getCostQuotas({
      page: pagination.page,
      page_size: pagination.pageSize
    })

    if (response.code === 200) {
      quotas.value = response.data.list.map(quota => ({
        ...quota,
        agent_name: quota.agent?.name || '-',
        user_name: quota.user?.full_name || quota.user?.username || '-',
        current_percent: Math.round((quota.current_usage / quota.monthly_limit) * 100)
      }))
      pagination.total = response.data.total
    }
  } catch (error) {
    console.error('加载配额失败:', error)
    ElMessage.error('加载配额失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const showEditDialog = (row) => {
  dialogMode.value = 'edit'
  Object.assign(form, row)
  dialogVisible.value = true
}

const resetForm = () => {
  Object.assign(form, {
    id: null,
    agent_id: null,
    user_id: null,
    monthly_limit: 100,
    reset_day: 1,
    alert_threshold: 0.8,
    alert_enabled: true,
    overage_enabled: false,
    overage_rate: 1.5
  })
  formRef.value?.resetFields()
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    submitting.value = true
    const data = { ...form }

    if (dialogMode.value === 'create') {
      await createCostQuota(data)
      ElMessage.success('创建成功')
    } else {
      await updateCostQuota(form.id, data)
      ElMessage.success('更新成功')
    }

    dialogVisible.value = false
    loadQuotas()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除此配额吗？', '确认删除', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteCostQuota(row.id)
      ElMessage.success('删除成功')
      loadQuotas()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadQuotas()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadQuotas()
}

const getProgressStatus = (row) => {
  if (row.current_percent >= 100) return 'exception'
  if (row.current_percent >= 80) return 'warning'
  return 'success'
}

onMounted(() => {
  loadQuotas()
})
</script>

<style scoped>
.cost-quota-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.warning-text {
  color: #e6a23c;
  font-weight: bold;
}
</style>
