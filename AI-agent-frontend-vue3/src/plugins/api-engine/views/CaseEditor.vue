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
            <el-button size="small" @click="generateTemplate">生成模板</el-button>
            <el-button size="small" @click="formatYaml">格式化</el-button>
            <el-button size="small" @click="validateYaml">验证</el-button>
            <el-button size="small" @click="getStructure">结构分析</el-button>
          </div>
        </div>
        <div class="yaml-editor-wrapper">
          <el-input
            v-model="yamlContent"
            type="textarea"
            :rows="20"
            placeholder="请输入YAML配置内容，支持以下格式：

desc: '用例描述'
pre_script:
  - print('前置脚本')
steps:
  - send_request:
      url: 'https://api.example.com/test'
      method: 'GET'
      headers:
        Content-Type: 'application/json'
  - assert_status_code:
      EXPECTED: 200
post_script:
  - print('后置脚本')
context:
  base_url: 'https://api.example.com'
ddts:
  - username: 'user1'
    password: 'pass1'"
            class="yaml-editor"
            @input="handleYamlChange"
          />
          <div v-if="yamlStructure" class="yaml-structure">
            <h4>YAML结构</h4>
            <el-descriptions :column="3" size="small" border>
              <el-descriptions-item label="描述">
                <el-tag :type="yamlStructure.hasDesc ? 'success' : 'info'">
                  {{ yamlStructure.hasDesc ? '已设置' : '未设置' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="步骤数">
                <el-tag type="primary">{{ yamlStructure.stepCount }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="前置脚本">
                <el-tag :type="yamlStructure.hasPreScript ? 'success' : 'info'">
                  {{ yamlStructure.hasPreScript ? '已设置' : '未设置' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="后置脚本">
                <el-tag :type="yamlStructure.hasPostScript ? 'success' : 'info'">
                  {{ yamlStructure.hasPostScript ? '已设置' : '未设置' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="数据驱动">
                <el-tag :type="yamlStructure.hasDdts ? 'success' : 'info'">
                  {{ yamlStructure.hasDdts ? '已设置' : '未设置' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="上下文">
                <el-tag :type="yamlStructure.hasContext ? 'success' : 'info'">
                  {{ yamlStructure.hasContext ? '已设置' : '未设置' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
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
import { YamlUtils, type FormTestCase } from '@/utils/yaml'

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

const formConfig = reactive<FormTestCase>({
  steps: []
})

const yamlContent = ref('')
const yamlStructure = ref<any>(null)

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
    try {
      // 使用表单配置中的描述
      formConfig.desc = formData.description || formData.name
      yamlContent.value = YamlUtils.formToYaml(formConfig)
    } catch (error: any) {
      ElMessage.error(`表单转YAML失败: ${error.message}`)
      return
    }
  } else {
    // YAML转表单
    try {
      const form = YamlUtils.yamlToForm(yamlContent.value)
      Object.assign(formConfig, form)
      formData.description = formConfig.desc
    } catch (error: any) {
      ElMessage.error(`YAML转表单失败: ${error.message}`)
      return
    }
  }

  configMode.value = mode
  formData.config_mode = mode
}

const formatYaml = () => {
  try {
    yamlContent.value = YamlUtils.format(yamlContent.value)
    ElMessage.success('YAML格式化成功')
  } catch (error: any) {
    ElMessage.error(`YAML格式化失败: ${error.message}`)
  }
}

const validateYaml = () => {
  const result = YamlUtils.validate(yamlContent.value)
  if (result.valid) {
    ElMessage.success('YAML格式正确')
  } else {
    ElMessage.error(`YAML格式错误: ${result.error}`)
  }
}

const generateTemplate = () => {
  yamlContent.value = YamlUtils.generateTemplate(formData.name || '测试用例')
  ElMessage.success('已生成YAML模板')
}

const getStructure = () => {
  try {
    const structure = YamlUtils.getStructure(yamlContent.value)
    yamlStructure.value = structure
    ElMessage.success('YAML结构分析完成')
  } catch (error: any) {
    yamlStructure.value = null
    ElMessage.error(`获取YAML结构失败: ${error.message}`)
  }
}

const handleYamlChange = () => {
  try {
    // 实时更新YAML结构信息
    const structure = YamlUtils.getStructure(yamlContent.value)
    yamlStructure.value = structure
  } catch (error) {
    yamlStructure.value = null
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

        // 如果是YAML模式，验证YAML格式
        if (configMode.value === 'yaml') {
          const validation = YamlUtils.validate(yamlContent.value)
          if (!validation.valid) {
            ElMessage.error(`YAML格式错误: ${validation.error}`)
            return
          }
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

      .yaml-editor-wrapper {
        display: flex;
        gap: 20px;
        flex-direction: column;

        .yaml-editor {
          font-family: 'Courier New', monospace;
          font-size: 14px;

          :deep(textarea) {
            font-family: 'Courier New', monospace;
            line-height: 1.5;
            min-height: 400px;
          }
        }

        .yaml-structure {
          margin-top: 16px;
          padding: 16px;
          background-color: #f8f9fa;
          border-radius: 6px;
          border: 1px solid #e9ecef;

          h4 {
            margin: 0 0 12px 0;
            font-size: 14px;
            font-weight: 600;
            color: #495057;
          }

          :deep(.el-descriptions) {
            .el-descriptions__body {
              background-color: transparent;
            }
          }
        }
      }
    }
  }
}
</style>

