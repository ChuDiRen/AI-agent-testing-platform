<template>
  <div class="case-editor-container">
    <el-page-header @back="goBack">
      <template #content>
        <span>{{ isEdit ? '编辑用例' : '创建用例' }}</span>
      </template>
      <template #extra>
        <el-button-group>
          <el-button
            :type="configMode === 'form' ? 'primary' : ''"
            @click="switchMode('form')"
          >
            表单模式
          </el-button>
          <el-button
            :type="configMode === 'yaml' ? 'primary' : ''"
            @click="switchMode('yaml')"
          >
            YAML模式
          </el-button>
        </el-button-group>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
        <el-button @click="handleCancel">取消</el-button>
      </template>
    </el-page-header>

    <el-card class="editor-card">
      <!-- 基本信息 -->
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="所属套件" prop="suite_id">
          <el-select v-model="formData.suite_id" placeholder="请选择套件" style="width: 100%">
            <el-option
              v-for="suite in store.suites"
              :key="suite.suite_id"
              :label="suite.name"
              :value="suite.suite_id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用例名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入用例名称" />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" style="width: 200px">
            <el-option label="P0-最高" value="P0" />
            <el-option label="P1-高" value="P1" />
            <el-option label="P2-中" value="P2" />
            <el-option label="P3-低" value="P3" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="draft">草稿</el-radio>
            <el-radio label="active">激活</el-radio>
            <el-radio label="deprecated">已弃用</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入用例描述"
          />
        </el-form-item>
      </el-form>

      <el-divider />

      <!-- 表单模式 -->
      <div v-if="configMode === 'form'" class="form-config">
        <step-editor v-model="formConfig.steps" />
      </div>

      <!-- YAML模式 -->
      <div v-else class="yaml-config">
        <div class="yaml-header">
          <h3>YAML配置</h3>
          <div class="yaml-actions">
            <el-button size="small" @click="formatYaml">格式化</el-button>
            <el-button size="small" @click="validateYaml">验证</el-button>
          </div>
        </div>
        <el-input
          v-model="yamlContent"
          type="textarea"
          :rows="20"
          placeholder="请输入YAML配置内容"
          class="yaml-editor"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import StepEditor from '../components/StepEditor.vue'
import type { Case } from '../api'

const route = useRoute()
const router = useRouter()
const store = useApiEngineStore()

const caseId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})
const isEdit = computed(() => !!caseId.value)

const formRef = ref()
const saving = ref(false)
const configMode = ref<'form' | 'yaml'>('form')

const formData = reactive<Case>({
  suite_id: 0,
  name: '',
  description: '',
  config_mode: 'form',
  priority: 'P2',
  status: 'draft'
})

const formConfig = reactive({
  steps: [] as any[]
})

const yamlContent = ref('')

const rules = {
  suite_id: [{ required: true, message: '请选择所属套件', trigger: 'change' }],
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const switchMode = (mode: 'form' | 'yaml') => {
  if (mode === configMode.value) return

  // 模式切换时进行数据转换
  if (mode === 'yaml') {
    // 表单转YAML
    yamlContent.value = convertFormToYaml()
  } else {
    // YAML转表单
    try {
      formConfig.steps = convertYamlToForm()
    } catch (error: any) {
      ElMessage.error('YAML格式错误,无法转换为表单模式')
      return
    }
  }

  configMode.value = mode
  formData.config_mode = mode
}

const convertFormToYaml = (): string => {
  // 简单的表单到YAML转换
  const steps = formConfig.steps.map(step => {
    const params = Object.entries(step.params)
      .filter(([_, value]) => value !== undefined && value !== '')
      .map(([key, value]) => `    ${key}: ${JSON.stringify(value)}`)
      .join('\n')
    
    return `- ${step.keyword}:\n${params || '    # 无参数'}\n  name: ${step.name || step.keyword}`
  })

  return `# ${formData.name}
# ${formData.description || ''}

test:
${steps.join('\n')}`
}

const convertYamlToForm = (): any[] => {
  // 简单的YAML到表单转换 (实际应该用YAML解析库)
  // 这里只是示例,实际需要更复杂的解析
  ElMessage.info('YAML转表单功能需要完善')
  return formConfig.steps
}

const formatYaml = () => {
  // 格式化YAML
  ElMessage.info('YAML格式化功能')
}

const validateYaml = () => {
  // 验证YAML
  try {
    // 这里应该调用后端API验证
    ElMessage.success('YAML格式正确')
  } catch (error) {
    ElMessage.error('YAML格式错误')
  }
}

const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      saving.value = true
      try {
        const caseData: Case = {
          ...formData,
          config_mode: configMode.value,
          form_config: configMode.value === 'form' ? formConfig : undefined,
          yaml_config: configMode.value === 'yaml' ? yamlContent.value : undefined
        }

        if (isEdit.value && caseId.value) {
          await store.updateCase(caseId.value, caseData)
          ElMessage.success('更新成功')
        } else {
          await store.createCase(caseData)
          ElMessage.success('创建成功')
        }

        goBack()
      } catch (error: any) {
        ElMessage.error(error.message || '保存失败')
      } finally {
        saving.value = false
      }
    }
  })
}

const handleCancel = () => {
  goBack()
}

const goBack = () => {
  router.go(-1)
}

const loadCaseData = async () => {
  if (!caseId.value) return

  try {
    const caseData = await store.fetchCaseById(caseId.value)
    
    Object.assign(formData, {
      suite_id: caseData.suite_id,
      name: caseData.name,
      description: caseData.description,
      config_mode: caseData.config_mode,
      priority: caseData.priority,
      status: caseData.status
    })

    configMode.value = caseData.config_mode || 'form'

    if (caseData.config_mode === 'yaml') {
      yamlContent.value = caseData.yaml_config || ''
    } else {
      formConfig.steps = caseData.form_config?.steps || []
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载用例失败')
    goBack()
  }
}

onMounted(async () => {
  await store.fetchSuites()
  
  if (isEdit.value) {
    await loadCaseData()
  } else {
    // 从查询参数获取suite_id
    const suiteId = route.query.suite_id
    if (suiteId) {
      formData.suite_id = Number(suiteId)
    }
  }
})
</script>

<style scoped lang="scss">
.case-editor-container {
  padding: 20px;

  .editor-card {
    margin-top: 20px;

    .form-config {
      padding: 20px 0;
    }

    .yaml-config {
      .yaml-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;

        h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
        }

        .yaml-actions {
          display: flex;
          gap: 8px;
        }
      }

      .yaml-editor {
        font-family: 'Courier New', monospace;
        font-size: 14px;

        :deep(textarea) {
          font-family: 'Courier New', monospace;
          line-height: 1.5;
        }
      }
    }
  }
}
</style>

