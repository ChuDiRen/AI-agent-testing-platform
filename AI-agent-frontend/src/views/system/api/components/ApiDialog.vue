<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      :disabled="mode === 'view'"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="API路径" prop="path">
            <el-input
              v-model="formData.path"
              placeholder="请输入API路径，如：/api/v1/users"
              :disabled="mode === 'edit'"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="HTTP方法" prop="method">
            <el-select
              v-model="formData.method"
              placeholder="选择HTTP方法"
              style="width: 100%"
              :disabled="mode === 'edit'"
            >
              <el-option
                v-for="method in HTTP_METHODS"
                :key="method"
                :label="method"
                :value="method"
              />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="API名称" prop="name">
            <el-input
              v-model="formData.name"
              placeholder="请输入API名称"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="API版本" prop="version">
            <el-input
              v-model="formData.version"
              placeholder="请输入API版本，如：v1"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="所属模块" prop="module">
            <el-input
              v-model="formData.module"
              placeholder="请输入所属模块"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="权限标识" prop="permission">
            <el-input
              v-model="formData.permission"
              placeholder="请输入权限标识，如：user:view"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="API描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入API描述"
        />
      </el-form-item>

      <el-form-item label="API状态" prop="status" v-if="mode !== 'create'">
        <el-radio-group v-model="formData.status">
          <el-radio
            v-for="(label, value) in API_STATUS_LABELS"
            :key="value"
            :label="value"
          >
            {{ label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 请求参数示例 -->
      <el-form-item label="请求示例">
        <div class="json-editor">
          <el-input
            v-model="requestExampleText"
            type="textarea"
            :rows="6"
            placeholder="请输入JSON格式的请求参数示例"
            @blur="validateJson('request')"
          />
          <div v-if="jsonErrors.request" class="json-error">
            {{ jsonErrors.request }}
          </div>
        </div>
      </el-form-item>

      <!-- 响应示例 -->
      <el-form-item label="响应示例">
        <div class="json-editor">
          <el-input
            v-model="responseExampleText"
            type="textarea"
            :rows="6"
            placeholder="请输入JSON格式的响应示例"
            @blur="validateJson('response')"
          />
          <div v-if="jsonErrors.response" class="json-error">
            {{ jsonErrors.response }}
          </div>
        </div>
      </el-form-item>

      <!-- 统计信息（仅查看模式显示） -->
      <template v-if="mode === 'view' && apiData">
        <el-divider content-position="left">统计信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="总调用次数">
              <el-input :value="apiData.total_calls" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="成功次数">
              <el-input :value="apiData.success_calls" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="错误次数">
              <el-input :value="apiData.error_calls" readonly />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="成功率">
              <el-input :value="apiData.success_rate.toFixed(2) + '%'" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平均响应时间">
              <el-input :value="apiData.avg_response_time.toFixed(2) + 'ms'" readonly />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最后调用时间">
              <el-input :value="apiData.last_called_at || '暂无'" readonly />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          v-if="mode !== 'view'"
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          {{ mode === 'create' ? '创建' : '更新' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { ApiEndpointApi, type ApiEndpoint, API_STATUS_LABELS, HTTP_METHODS } from '@/api/modules/apiEndpoint'

// Props
interface Props {
  visible: boolean
  mode: 'create' | 'edit' | 'view'
  apiData?: ApiEndpoint | null
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  mode: 'create',
  apiData: null
})

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const loading = ref(false)
const requestExampleText = ref('')
const responseExampleText = ref('')

// JSON验证错误
const jsonErrors = reactive({
  request: '',
  response: ''
})

// 表单数据
const formData = reactive({
  path: '',
  method: 'GET',
  name: '',
  description: '',
  module: '',
  permission: '',
  version: 'v1',
  status: 'active'
})

// 计算属性
const dialogVisible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

const dialogTitle = computed(() => {
  const titles = {
    create: '新增API端点',
    edit: '编辑API端点',
    view: 'API端点详情'
  }
  return titles[props.mode]
})

// 表单验证规则
const formRules: FormRules = {
  path: [
    { required: true, message: '请输入API路径', trigger: 'blur' },
    { min: 1, max: 500, message: '路径长度在1到500个字符', trigger: 'blur' }
  ],
  method: [
    { required: true, message: '请选择HTTP方法', trigger: 'change' }
  ],
  name: [
    { required: true, message: '请输入API名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度在1到100个字符', trigger: 'blur' }
  ],
  version: [
    { max: 20, message: '版本长度不能超过20个字符', trigger: 'blur' }
  ],
  module: [
    { max: 100, message: '模块名称长度不能超过100个字符', trigger: 'blur' }
  ],
  permission: [
    { max: 100, message: '权限标识长度不能超过100个字符', trigger: 'blur' }
  ]
}

// 监听器
watch(() => props.visible, (visible) => {
  if (visible) {
    initForm()
  }
})

// 方法
const initForm = () => {
  if (props.apiData) {
    Object.assign(formData, {
      path: props.apiData.path,
      method: props.apiData.method,
      name: props.apiData.name,
      description: props.apiData.description || '',
      module: props.apiData.module || '',
      permission: props.apiData.permission || '',
      version: props.apiData.version,
      status: props.apiData.status
    })
    
    // 设置JSON示例
    requestExampleText.value = props.apiData.request_example 
      ? JSON.stringify(props.apiData.request_example, null, 2) 
      : ''
    responseExampleText.value = props.apiData.response_example 
      ? JSON.stringify(props.apiData.response_example, null, 2) 
      : ''
  } else {
    // 重置表单
    Object.assign(formData, {
      path: '',
      method: 'GET',
      name: '',
      description: '',
      module: '',
      permission: '',
      version: 'v1',
      status: 'active'
    })
    requestExampleText.value = ''
    responseExampleText.value = ''
  }
  
  // 清除JSON错误
  jsonErrors.request = ''
  jsonErrors.response = ''
  
  // 清除表单验证
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const validateJson = (type: 'request' | 'response') => {
  const text = type === 'request' ? requestExampleText.value : responseExampleText.value
  
  if (!text.trim()) {
    jsonErrors[type] = ''
    return true
  }
  
  try {
    JSON.parse(text)
    jsonErrors[type] = ''
    return true
  } catch (error) {
    jsonErrors[type] = 'JSON格式不正确'
    return false
  }
}

const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()
    
    // 验证JSON
    const requestValid = validateJson('request')
    const responseValid = validateJson('response')
    
    if (!requestValid || !responseValid) {
      ElMessage.error('请检查JSON格式')
      return
    }
    
    loading.value = true
    
    // 准备提交数据
    const submitData = {
      ...formData,
      request_example: requestExampleText.value ? JSON.parse(requestExampleText.value) : undefined,
      response_example: responseExampleText.value ? JSON.parse(responseExampleText.value) : undefined
    }
    
    // 提交数据
    if (props.mode === 'create') {
      await ApiEndpointApi.createApiEndpoint(submitData)
      ElMessage.success('创建成功')
    } else {
      await ApiEndpointApi.updateApiEndpoint(props.apiData!.id, submitData)
      ElMessage.success('更新成功')
    }
    
    emit('success')
    handleClose()
  } catch (error: any) {
    console.error('提交失败:', error)
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  dialogVisible.value = false
}
</script>

<style scoped lang="scss">
.json-editor {
  .json-error {
    color: #f56c6c;
    font-size: 12px;
    margin-top: 4px;
  }
}

.dialog-footer {
  text-align: right;
}

:deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
}
</style>
