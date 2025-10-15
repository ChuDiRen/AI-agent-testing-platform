<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="report-generator-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><DocumentAdd /></el-icon>
            生成测试报告
          </span>
          <div class="actions">
            <el-button @click="handleCancel">取消</el-button>
            <el-button type="primary" @click="handleGenerate" :loading="generating">
              <el-icon><Check /></el-icon>
              生成报告
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
        <el-form-item label="报告名称" prop="name">
          <el-input
            v-model="formData.name"
            placeholder="请输入报告名称"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="报告类型" prop="report_type">
          <el-select v-model="formData.report_type" placeholder="选择报告类型">
            <el-option label="API测试报告" value="API" />
            <el-option label="Web测试报告" value="Web" />
            <el-option label="App测试报告" value="App" />
            <el-option label="综合测试报告" value="Integrated" />
          </el-select>
        </el-form-item>

        <el-form-item label="选择测试用例">
          <div class="testcase-selector">
            <el-button type="primary" @click="showTestCaseSelector = true">
              <el-icon><Plus /></el-icon>
              选择用例 (已选 {{ selectedTestCases.length }})
            </el-button>
            <div v-if="selectedTestCases.length > 0" class="selected-cases">
              <el-tag
                v-for="tc in selectedTestCases"
                :key="tc"
                closable
                @close="removeTestCase(tc)"
                style="margin: 5px"
              >
                用例ID: {{ tc }}
              </el-tag>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="报告描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入报告描述"
          />
        </el-form-item>

        <el-alert
          title="提示"
          description="请选择要包含在报告中的测试用例，至少选择一个测试用例。"
          type="info"
          :closable="false"
          show-icon
        />
      </el-form>
    </el-card>

    <!-- 测试用例选择对话框 -->
    <el-dialog
      v-model="showTestCaseSelector"
      title="选择测试用例"
      width="800px"
    >
      <el-table
        :data="availableTestCases"
        @selection-change="handleTestCaseSelection"
        max-height="400"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="testcase_id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" />
        <el-table-column prop="test_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.test_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showTestCaseSelector = false">取消</el-button>
        <el-button type="primary" @click="confirmTestCaseSelection">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { DocumentAdd, Check, Plus } from '@element-plus/icons-vue'
import {
  generateReportAPI,
  type ReportGenerateRequest
} from '@/api/report'
import { getTestCasesAPI, type TestCase } from '@/api/testcase'

const router = useRouter()

// 状态
const formRef = ref<FormInstance>()
const generating = ref(false)
const showTestCaseSelector = ref(false)

// 表单数据
const formData = reactive<ReportGenerateRequest>({
  name: '',
  description: '',
  report_type: 'API',
  testcase_ids: [],
  environment: 'default',
  config: {}
})

// 测试用例选择
const availableTestCases = ref<TestCase[]>([])
const selectedTestCases = ref<number[]>([])
const tempSelectedTestCases = ref<TestCase[]>([])

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入报告名称', trigger: 'blur' }
  ],
  report_type: [
    { required: true, message: '请选择报告类型', trigger: 'change' }
  ]
}

// 加载可用测试用例
const loadTestCases = async () => {
  try {
    const response = await getTestCasesAPI({
      page: 1,
      page_size: 1000
    })
    
    if (response.data) {
      availableTestCases.value = response.data.items
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载测试用例失败')
  }
}

// 测试用例选择变化
const handleTestCaseSelection = (selection: TestCase[]) => {
  tempSelectedTestCases.value = selection
}

// 确认选择测试用例
const confirmTestCaseSelection = () => {
  selectedTestCases.value = tempSelectedTestCases.value.map(tc => tc.testcase_id)
  showTestCaseSelector.value = false
}

// 移除测试用例
const removeTestCase = (testcaseId: number) => {
  const index = selectedTestCases.value.indexOf(testcaseId)
  if (index !== -1) {
    selectedTestCases.value.splice(index, 1)
  }
}

// 生成报告
const handleGenerate = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    // 检查是否选择了测试用例
    if (selectedTestCases.value.length === 0) {
      ElMessage.warning('请至少选择一个测试用例')
      return
    }

    generating.value = true
    try {
      // 设置测试用例ID
      formData.testcase_ids = selectedTestCases.value

      const response = await generateReportAPI(formData)
      
      if (response.data) {
        ElMessage.success('报告生成成功')
        router.push(`/report/${response.data.report_id}`)
      }
    } catch (error: any) {
      ElMessage.error(error.message || '生成失败')
    } finally {
      generating.value = false
    }
  })
}

// 取消
const handleCancel = () => {
  router.back()
}

// 初始化
onMounted(() => {
  loadTestCases()
  
  // 设置默认报告名称
  const now = new Date()
  formData.name = `测试报告_${now.getFullYear()}${(now.getMonth() + 1).toString().padStart(2, '0')}${now.getDate().toString().padStart(2, '0')}_${now.getHours().toString().padStart(2, '0')}${now.getMinutes().toString().padStart(2, '0')}`
})
</script>

<style scoped lang="scss">
.report-generator-container {
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

  .testcase-selector {
    .selected-cases {
      margin-top: 10px;
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      min-height: 50px;
    }
  }
}
</style>

