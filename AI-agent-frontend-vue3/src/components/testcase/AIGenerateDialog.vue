<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <el-dialog
    v-model="visible"
    title="AI 生成测试用例"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 生成配置表单 -->
    <div v-if="currentStep === 1" class="generate-form">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="AI 模型" prop="model_key">
          <el-select v-model="form.model_key" placeholder="请选择 AI 模型" style="width: 100%">
            <el-option
              v-for="model in aiModels"
              :key="model.model_key"
              :label="`${model.name} (${model.provider})`"
              :value="model.model_key"
            >
              <div class="model-option">
                <span>{{ model.name }}</span>
                <el-tag :type="model.is_enabled ? 'success' : 'danger'" size="small">
                  {{ model.is_enabled ? '已启用' : '未启用' }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="测试类型" prop="test_type">
          <el-radio-group v-model="form.test_type">
            <el-radio label="API">API 测试</el-radio>
            <el-radio label="Web">Web 测试</el-radio>
            <el-radio label="App">App 测试</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="模块名称" prop="module">
          <el-input v-model="form.module" placeholder="例如：用户管理、订单系统" clearable />
        </el-form-item>

        <el-form-item label="输入方式" prop="input_mode">
          <el-radio-group v-model="form.input_mode">
            <el-radio label="text">文本输入</el-radio>
            <el-radio label="file">文件上传</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 文本输入 -->
        <el-form-item v-if="form.input_mode === 'text'" label="需求描述" prop="requirement">
          <el-input
            v-model="form.requirement"
            type="textarea"
            :rows="8"
            placeholder="请详细描述功能需求，包括功能点、业务流程、接口信息等。内容越详细，生成的测试用例质量越高。"
            show-word-limit
            maxlength="5000"
          />
        </el-form-item>

        <!-- 文件上传 -->
        <el-form-item v-if="form.input_mode === 'file'" label="需求文档" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".txt,.doc,.docx,.pdf"
            drag
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或<em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 TXT、Word、PDF 格式，文件大小不超过 10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="生成数量" prop="count">
          <el-slider v-model="form.count" :min="1" :max="20" show-input />
        </el-form-item>

        <el-form-item label="提示词模板">
          <el-select v-model="form.template_id" placeholder="使用默认模板" clearable style="width: 100%">
            <el-option
              v-for="template in templates"
              :key="template.template_id"
              :label="template.name"
              :value="template.template_id"
            >
              <div class="template-option">
                <span>{{ template.name }}</span>
                <el-tag v-if="template.is_default" type="primary" size="small">默认</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- 生成结果预览 -->
    <div v-if="currentStep === 2" class="preview-table">
      <el-alert
        v-if="generatedTestcases.length > 0"
        title="生成成功"
        :description="`共生成 ${generatedTestcases.length} 个测试用例，请预览并选择要保存的用例`"
        type="success"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <el-table
        :data="generatedTestcases"
        border
        stripe
        max-height="500"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="60" />
        
        <el-table-column label="用例名称" min-width="200">
          <template #default="{ row }">
            <el-input v-model="row.name" size="small" />
          </template>
        </el-table-column>

        <el-table-column label="模块" width="120">
          <template #default="{ row }">
            <el-input v-model="row.module" size="small" />
          </template>
        </el-table-column>

        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-select v-model="row.priority" size="small">
              <el-option label="P0" value="P0" />
              <el-option label="P1" value="P1" />
              <el-option label="P2" value="P2" />
              <el-option label="P3" value="P3" />
            </el-select>
          </template>
        </el-table-column>

        <el-table-column label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.description }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ $index }">
            <el-button
              link
              type="primary"
              size="small"
              @click="handleViewDetail($index)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <div v-if="currentStep === 1">
          <el-button @click="handleClose">取消</el-button>
          <el-button type="primary" :loading="generating" @click="handleGenerate">
            <el-icon v-if="!generating"><MagicStick /></el-icon>
            {{ generating ? '生成中...' : '开始生成' }}
          </el-button>
        </div>
        <div v-else>
          <el-button @click="handleBack">返回修改</el-button>
          <el-button @click="handleClose">取消</el-button>
          <el-button
            type="primary"
            :loading="saving"
            :disabled="selectedTestcases.length === 0"
            @click="handleSave"
          >
            保存选中的用例 ({{ selectedTestcases.length }})
          </el-button>
        </div>
      </div>
    </template>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="测试用例详情"
      width="700px"
      append-to-body
    >
      <el-form v-if="currentDetailCase" label-width="100px">
        <el-form-item label="用例名称">
          <el-input v-model="currentDetailCase.name" />
        </el-form-item>
        <el-form-item label="测试类型">
          <el-tag>{{ currentDetailCase.test_type }}</el-tag>
        </el-form-item>
        <el-form-item label="模块">
          <el-input v-model="currentDetailCase.module" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="currentDetailCase.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="前置条件">
          <el-input v-model="currentDetailCase.preconditions" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="测试步骤">
          <el-input v-model="currentDetailCase.test_steps" type="textarea" :rows="5" />
        </el-form-item>
        <el-form-item label="预期结果">
          <el-input v-model="currentDetailCase.expected_result" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="currentDetailCase.priority">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, MagicStick } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, UploadFile } from 'element-plus'
import {
  generateTestCasesWithTextAPI,
  generateTestCasesWithFileAPI,
  batchSaveTestCasesAPI,
  getAIModelsAPI
} from '@/api/testcase'
import { getPromptTemplatesAPI } from '@/api/prompt-template'

// Props & Emits
const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

// 状态
const visible = ref(props.modelValue)
const currentStep = ref(1) // 1: 配置, 2: 预览
const generating = ref(false)
const saving = ref(false)
const aiModels = ref<any[]>([])
const templates = ref<any[]>([])
const generatedTestcases = ref<any[]>([])
const selectedTestcases = ref<any[]>([])
const uploadedFile = ref<File | null>(null)
const detailDialogVisible = ref(false)
const currentDetailCase = ref<any>(null)

// 表单
const formRef = ref<FormInstance>()
const form = reactive({
  model_key: '',
  test_type: 'API',
  module: '',
  input_mode: 'text',
  requirement: '',
  count: 5,
  template_id: undefined as number | undefined
})

const rules: FormRules = {
  model_key: [{ required: true, message: '请选择 AI 模型', trigger: 'change' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  requirement: [
    { 
      required: true, 
      message: '请输入需求描述', 
      trigger: 'blur',
      validator: (rule, value, callback) => {
        if (form.input_mode === 'text' && !value) {
          callback(new Error('请输入需求描述'))
        } else {
          callback()
        }
      }
    }
  ],
  file: [
    {
      validator: (rule, value, callback) => {
        if (form.input_mode === 'file' && !uploadedFile.value) {
          callback(new Error('请上传需求文档'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 加载 AI 模型列表
const loadAIModels = async () => {
  try {
    const response = await getAIModelsAPI()
    if (response.data) {
      aiModels.value = response.data
      // 默认选择第一个启用的模型
      const enabledModel = response.data.find((m: any) => m.is_enabled)
      if (enabledModel) {
        form.model_key = enabledModel.model_key
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载 AI 模型失败')
  }
}

// 加载提示词模板
const loadTemplates = async () => {
  try {
    const response = await getPromptTemplatesAPI({
      template_type: 'testcase_generation',
      is_active: true
    })
    if (response.data) {
      templates.value = response.data
    }
  } catch (error: any) {
    console.error('加载提示词模板失败:', error)
  }
}

// 文件变化处理
const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    uploadedFile.value = file.raw
  }
}

// 文件删除处理
const handleFileRemove = () => {
  uploadedFile.value = null
}

// 生成测试用例
const handleGenerate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    generating.value = true
    
    try {
      let response
      
      if (form.input_mode === 'text') {
        // 文本输入模式
        response = await generateTestCasesWithTextAPI({
          requirement: form.requirement,
          test_type: form.test_type,
          module: form.module || undefined,
          count: form.count,
          model_key: form.model_key,
          template_id: form.template_id
        })
      } else {
        // 文件上传模式
        if (!uploadedFile.value) {
          ElMessage.error('请上传需求文档')
          return
        }
        
        response = await generateTestCasesWithFileAPI(uploadedFile.value, {
          test_type: form.test_type,
          module: form.module || undefined,
          count: form.count,
          model_key: form.model_key,
          template_id: form.template_id
        })
      }
      
      if (response.data && response.data.testcases) {
        generatedTestcases.value = response.data.testcases
        currentStep.value = 2
        ElMessage.success(`成功生成 ${response.data.total} 个测试用例`)
      } else {
        ElMessage.warning('生成结果为空')
      }
    } catch (error: any) {
      ElMessage.error(error.message || 'AI 生成失败')
    } finally {
      generating.value = false
    }
  })
}

// 选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedTestcases.value = selection
}

// 查看详情
const handleViewDetail = (index: number) => {
  currentDetailCase.value = generatedTestcases.value[index]
  detailDialogVisible.value = true
}

// 返回修改
const handleBack = () => {
  currentStep.value = 1
}

// 保存测试用例
const handleSave = async () => {
  if (selectedTestcases.value.length === 0) {
    ElMessage.warning('请至少选择一个测试用例')
    return
  }
  
  saving.value = true
  
  try {
    const response = await batchSaveTestCasesAPI(selectedTestcases.value)
    
    if (response.data) {
      const { saved_count, failed_count } = response.data
      
      if (failed_count === 0) {
        ElMessage.success(`成功保存 ${saved_count} 个测试用例`)
        emit('success')
        handleClose()
      } else {
        ElMessage.warning(`保存了 ${saved_count} 个用例，${failed_count} 个失败`)
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
  emit('update:modelValue', false)
  
  // 重置状态
  setTimeout(() => {
    currentStep.value = 1
    generatedTestcases.value = []
    selectedTestcases.value = []
    uploadedFile.value = null
    formRef.value?.resetFields()
  }, 300)
}

// 监听 props 变化
import { watch } from 'vue'
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadAIModels()
    loadTemplates()
  }
})

// 初始化
onMounted(() => {
  if (visible.value) {
    loadAIModels()
    loadTemplates()
  }
})
</script>

<style scoped lang="scss">
.generate-form {
  padding: 20px 0;
}

.preview-table {
  :deep(.el-table) {
    .el-input__inner {
      height: 28px;
      line-height: 28px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.model-option,
.template-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
</style>

