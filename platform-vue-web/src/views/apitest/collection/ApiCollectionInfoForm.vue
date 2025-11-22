<template>
  <div class="api-test-plan-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ formTitle }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- 基本信息表单 -->
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="计划名称" prop="plan_name">
          <el-input v-model="formData.plan_name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="计划描述">
          <el-input v-model="formData.plan_desc" type="textarea" :rows="3" placeholder="请输入计划描述" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存计划</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用例关联（仅编辑模式） -->
    <el-card v-if="formData.id" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>关联用例</span>
          <el-button type="success" size="small" @click="handleAddCase">添加用例</el-button>
        </div>
      </template>

      <el-table :data="caseList" border>
        <el-table-column prop="run_order" label="执行顺序" width="100" />
        <el-table-column prop="case_name" label="用例名称" min-width="150" />
        <el-table-column prop="case_desc" label="用例描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="数据驱动" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.ddt_data">已配置</el-tag>
            <el-tag v-else type="info">未配置</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditDdt(row)">配置数据</el-button>
            <el-button size="small" type="danger" @click="handleRemoveCase(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 数据驱动配置对话框 -->
    <el-dialog v-model="ddtDialogVisible" title="配置数据驱动" width="70%">
      <div>
        <p>数据驱动配置（JSON格式数组）：</p>
        <el-input
          v-model="currentDdtData"
          type="textarea"
          :rows="10"
          placeholder='示例: [{"desc": "数据组1", "username": "test1"}, {"desc": "数据组2", "username": "test2"}]'
        />
      </div>
      <template #footer>
        <el-button @click="ddtDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDdt">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { insertData, updateData, queryById, removeCase, updateDdtData } from './apiCollectionInfo'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const formData = ref({
  id: null,
  plan_name: '',
  plan_desc: '',
  project_id: null
})

const rules = {
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }]
}

const caseList = ref([])
const ddtDialogVisible = ref(false)
const currentDdtData = ref('')
const currentEditingCase = ref(null)

const formTitle = computed(() => formData.value.id ? '编辑测试计划' : '新增测试计划')

// 加载详情
const loadDetail = async (id) => {
  try {
    const res = await queryById(id)
    if (res.code === 20000 && res.data) {
      formData.value = {
        id: res.data.id,
        plan_name: res.data.plan_name,
        plan_desc: res.data.plan_desc,
        project_id: res.data.project_id
      }
      caseList.value = res.data.cases || []
    }
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const apiFunc = formData.value.id ? updateData : insertData
    const res = await apiFunc(formData.value)
    
    if (res.code === 20000) {
      ElMessage.success(formData.value.id ? '更新成功' : '新增成功')
      goBack()
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (error) {
    if (error !== false) { // 表单验证失败会返回false
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

// 添加用例（简化版，实际应该打开用例选择器）
const handleAddCase = () => {
  ElMessage.info('请在用例列表中选择用例添加到计划')
  // TODO: 实现用例选择器对话框
}

// 移除用例
const handleRemoveCase = async (row) => {
  try {
    const res = await removeCase(row.id)
    if (res.code === 20000) {
      ElMessage.success('移除成功')
      loadDetail(formData.value.id)
    }
  } catch (error) {
    ElMessage.error('移除失败: ' + error.message)
  }
}

// 编辑数据驱动
const handleEditDdt = (row) => {
  currentEditingCase.value = row
  currentDdtData.value = row.ddt_data || '[]'
  ddtDialogVisible.value = true
}

// 保存数据驱动配置
const handleSaveDdt = async () => {
  try {
    // 验证JSON格式
    JSON.parse(currentDdtData.value)
    
    const res = await updateDdtData({
      plan_case_id: currentEditingCase.value.id,
      ddt_data: JSON.parse(currentDdtData.value)
    })
    
    if (res.code === 20000) {
      ElMessage.success('保存成功')
      ddtDialogVisible.value = false
      loadDetail(formData.value.id)
    }
  } catch (error) {
    ElMessage.error('JSON格式错误或保存失败: ' + error.message)
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  if (route.query.id) {
    loadDetail(route.query.id)
  }
})
</script>

<style scoped>
.api-test-plan-form {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

