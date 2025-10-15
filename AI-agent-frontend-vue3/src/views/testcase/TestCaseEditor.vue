<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="testcase-editor-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Edit /></el-icon>
            {{ isEdit ? '编辑用例' : '创建用例' }}
          </span>
          <div class="actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleSave" :loading="saving">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="用例名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入用例名称"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="测试类型" prop="test_type">
          <el-radio-group v-model="formData.test_type">
            <el-radio label="API">API测试</el-radio>
            <el-radio label="Web">Web测试</el-radio>
            <el-radio label="App">App测试</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" placeholder="选择优先级">
                <el-option label="P0 - 紧急" value="P0" />
                <el-option label="P1 - 高" value="P1" />
                <el-option label="P2 - 中" value="P2" />
                <el-option label="P3 - 低" value="P3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="选择状态">
                <el-option label="草稿" value="draft" />
                <el-option label="启用" value="active" />
                <el-option label="废弃" value="deprecated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="所属模块">
          <el-input
            v-model="formData.module"
            placeholder="例如：用户管理、订单系统等"
          />
        </el-form-item>

        <el-form-item label="用例描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入用例描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="前置条件">
          <el-input
            v-model="formData.preconditions"
            type="textarea"
            :rows="3"
            placeholder="执行此用例前需要满足的条件"
          />
        </el-form-item>

        <el-form-item label="测试步骤">
          <el-input
            v-model="formData.test_steps"
            type="textarea"
            :rows="6"
            placeholder="请输入测试步骤，每行一个步骤"
          />
        </el-form-item>

        <el-form-item label="预期结果">
          <el-input
            v-model="formData.expected_result"
            type="textarea"
            :rows="3"
            placeholder="执行所有步骤后的预期结果"
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-input
            v-model="formData.tags"
            placeholder="多个标签用逗号分隔，例如: 登录,认证,P0"
          />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Edit, Check, Plus, Delete } from '@element-plus/icons-vue'
import {
  getTestCaseAPI,
  createTestCaseAPI,
  updateTestCaseAPI,
  type TestCaseCreate,
  type TestCaseUpdate
} from '@/api/testcase'

const route = useRoute()
const router = useRouter()

// 状态
const formRef = ref<FormInstance>()
const saving = ref(false)
const isEdit = computed(() => !!route.params.id && route.query.mode === 'edit')

// 表单数据
const formData = reactive<TestCaseCreate>({
  name: '',
  test_type: 'API',
  module: '',
  description: '',
  preconditions: '',
  test_steps: '',
  expected_result: '',
  priority: 'P2',
  status: 'draft',
  tags: ''
})


// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' }
  ],
  test_type: [
    { required: true, message: '请选择测试类型', trigger: 'change' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 加载用例数据（编辑模式）
const loadTestCase = async () => {
  if (!route.params.id) return

  try {
    const response = await getTestCaseAPI(Number(route.params.id))
    if (response.data) {
      const data = response.data
      formData.name = data.name
      formData.test_type = data.test_type
      formData.module = data.module || ''
      formData.description = data.description || ''
      formData.preconditions = data.preconditions || ''
      formData.test_steps = data.test_steps || ''
      formData.expected_result = data.expected_result || ''
      formData.priority = data.priority
      formData.status = data.status
      formData.tags = data.tags || ''
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载用例失败')
    router.back()
  }
}

// 保存
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      if (isEdit.value) {
        // 编辑模式
        await updateTestCaseAPI(
          Number(route.params.id),
          formData as TestCaseUpdate
        )
        ElMessage.success('更新成功')
      } else {
        // 创建模式
        await createTestCaseAPI(formData)
        ElMessage.success('创建成功')
      }
      router.push('/testcase/list')
    } catch (error: any) {
      ElMessage.error(error.message || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

// 取消
const handleCancel = () => {
  router.back()
}

// 初始化
onMounted(() => {
  if (isEdit.value) {
    loadTestCase()
  }
})
</script>

<style scoped lang="scss">
.testcase-editor-container {
  padding: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 500;
    }

    .actions {
      display: flex;
      gap: 10px;
    }
  }

  .steps-editor {
    width: 100%;

    .step-item {
      padding: 15px;
      margin-bottom: 10px;
      border: 1px solid #dcdfe6;
      border-radius: 4px;

      .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;

        .step-number {
          font-weight: 500;
          color: #409eff;
        }
      }
    }
  }
}
</style>

