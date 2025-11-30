<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑步骤' : '添加步骤'"
    width="800px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="stepForm" :rules="rules" label-width="120px">
      <el-form-item label="运行序号" prop="run_order">
        <el-input-number v-model="stepForm.run_order" :min="1" :step="1" />
      </el-form-item>

      <el-form-item label="步骤描述" prop="step_desc">
        <el-input v-model="stepForm.step_desc" placeholder="请输入步骤描述" />
      </el-form-item>

      <el-form-item label="操作类型" prop="operation_type_id">
        <el-select
          v-model="stepForm.operation_type_id"
          placeholder="请选择操作类型"
          @change="handleOperationTypeChange"
          clearable
        >
          <el-option
            v-for="type in operationTypeList"
            :key="type.id"
            :label="type.operation_type_name"
            :value="type.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="关键字" prop="keyword_id">
        <el-select
          v-model="stepForm.keyword_id"
          placeholder="请选择关键字"
          @change="handleKeywordChange"
          :disabled="!stepForm.operation_type_id"
          clearable
        >
          <el-option
            v-for="keyword in keywordList"
            :key="keyword.id"
            :label="keyword.name"
            :value="keyword.id"
          />
        </el-select>
      </el-form-item>

      <!-- 动态字段区域 -->
      <div v-if="dynamicFields.length > 0" class="dynamic-fields">
        <el-divider>关键字参数配置</el-divider>
        <el-form-item
          v-for="field in dynamicFields"
          :key="field.name"
          :label="field.placeholder || field.name"
        >
          <!-- 特殊字段：接口信息下拉 -->
          <el-select
            v-if="field.name.startsWith('_接口信息')"
            v-model="stepForm.step_data[field.name]"
            placeholder="请选择接口"
            filterable
            clearable
          >
            <el-option
              v-for="api in apiInfoList"
              :key="api.id"
              :label="`${api.api_name} (${api.request_method} ${api.request_url})`"
              :value="api.id"
            />
          </el-select>

          <!-- 特殊字段：数据库下拉 -->
          <el-select
            v-else-if="field.name && field.name.startsWith('_数据库')"
            v-model="stepForm.step_data[field.name]"
            placeholder="请选择数据库"
            filterable
            clearable
          >
            <el-option
              v-for="db in dbList"
              :key="db.id"
              :label="`${db.db_name} (${db.db_type})`"
              :value="db.id"
            />
          </el-select>

          <!-- JSON/对象类型：使用文本域（后续可升级为JSON编辑器） -->
          <el-input
            v-else-if="['HEADERS', 'PARAMS', 'DATA', 'JSON'].includes(field.name)"
            v-model="stepForm.step_data[field.name]"
            type="textarea"
            :rows="4"
            :placeholder="field.placeholder || `请输入${field.name} (JSON格式)`"
          />

          <!-- 普通文本输入框 -->
          <el-input
            v-else
            v-model="stepForm.step_data[field.name]"
            :placeholder="field.placeholder || `请输入${field.name}`"
          />
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { queryKeywordsByType, getKeywordFields } from '../apiCase.js'
import { queryAll as queryOperationType } from '../../keyword/operationType.js'
import { queryAll as queryApiInfo } from '../../apiinfo/apiinfo.js'
import { queryAll as queryDbBase } from '../../project/dbBase.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  stepData: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  nextOrder: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

// 对话框显示状态
const dialogVisible = ref(false)
const formRef = ref(null)

// 表单数据
const stepForm = reactive({
  run_order: 1,
  step_desc: '',
  operation_type_id: null,
  keyword_id: null,
  step_data: {}
})

// 表单验证规则
const rules = {
  run_order: [{ required: true, message: '请输入运行序号', trigger: 'blur' }],
  step_desc: [{ required: true, message: '请输入步骤描述', trigger: 'blur' }],
  operation_type_id: [{ required: true, message: '请选择操作类型', trigger: 'change' }],
  keyword_id: [{ required: true, message: '请选择关键字', trigger: 'change' }]
}

// 下拉列表数据
const operationTypeList = ref([])
const keywordList = ref([])
const dynamicFields = ref([])
const apiInfoList = ref([])
const dbList = ref([])

// 加载操作类型列表
const loadOperationTypes = async () => {
  try {
    const res = await queryOperationType()
    if (res.data.code === 200) {
      operationTypeList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载操作类型失败:', error)
  }
}

// 加载接口信息列表（用于特殊字段）
const loadApiInfo = async () => {
  try {
    const res = await queryApiInfo()
    if (res.data.code === 200) {
      apiInfoList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载接口信息失败:', error)
  }
}

// 加载数据库列表（用于特殊字段）
const loadDbList = async () => {
  try {
    const res = await queryDbBase()
    if (res.data.code === 200) {
      dbList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载数据库列表失败:', error)
  }
}

// 操作类型改变事件
const handleOperationTypeChange = async (value) => {
  // 清空关键字和动态字段
  stepForm.keyword_id = null
  dynamicFields.value = []
  stepForm.step_data = {}
  
  if (!value) {
    keywordList.value = []
    return
  }
  
  // 加载关键字列表
  try {
    const res = await queryKeywordsByType(value)
    if (res.data.code === 200) {
      keywordList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载关键字列表失败:', error)
    ElMessage.error('加载关键字列表失败')
  }
}

// 关键字改变事件
const handleKeywordChange = async (value) => {
  // 清空动态字段
  dynamicFields.value = []
  stepForm.step_data = {}
  
  if (!value) {
    return
  }
  
  // 加载关键字字段描述
  try {
    const res = await getKeywordFields(value)
    if (res.data.code === 200) {
      const fields = Array.isArray(res.data.data) ? res.data.data : []
      dynamicFields.value = fields
      
      // 确保step_data是对象
      if (!stepForm.step_data) {
        stepForm.step_data = {}
      }
      
      // 初始化step_data
      fields.forEach(field => {
        if (field && field.name) {
          // 只有当字段不存在时才初始化，避免覆盖已有值（在编辑模式下）
          if (stepForm.step_data[field.name] === undefined) {
            stepForm.step_data[field.name] = field.default || ''
          }
        }
      })
      
      // 如果有特殊字段，加载对应的下拉数据
      const hasApiField = fields.some(f => f.name && f.name.startsWith('_接口信息'))
      const hasDbField = fields.some(f => f.name && f.name.startsWith('_数据库'))
      
      if (hasApiField) {
        loadApiInfo()
      }
      if (hasDbField) {
        loadDbList()
      }
    } else {
      console.error('加载关键字字段失败，后端返回错误:', res.data.msg)
    }
  } catch (error) {
    console.error('加载关键字字段失败:', error)
    ElMessage.error('加载关键字字段失败: ' + (error.message || '未知错误'))
  }
}

// 监听modelValue变化
watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    // 对话框打开时
    loadOperationTypes()
    
    if (props.stepData) {
      // 编辑模式：加载步骤数据
      const rawStepData = props.stepData.step_data ? JSON.parse(JSON.stringify(props.stepData.step_data)) : {}
      
      // 将对象类型的参数转换为JSON字符串以便编辑
      for (const key in rawStepData) {
        if (typeof rawStepData[key] === 'object' && rawStepData[key] !== null) {
          rawStepData[key] = JSON.stringify(rawStepData[key], null, 2)
        }
      }

      Object.assign(stepForm, {
        run_order: props.stepData.run_order,
        step_desc: props.stepData.step_desc,
        operation_type_id: props.stepData.operation_type_id,
        keyword_id: props.stepData.keyword_id,
        step_data: rawStepData
      })
      
      // 加载关键字列表和字段
      if (props.stepData.operation_type_id) {
        handleOperationTypeChange(props.stepData.operation_type_id)
      }
      if (props.stepData.keyword_id) {
        setTimeout(() => {
          handleKeywordChange(props.stepData.keyword_id)
        }, 300)
      }
    } else {
      // 新增模式：重置表单
      stepForm.run_order = props.nextOrder
      stepForm.step_desc = ''
      stepForm.operation_type_id = null
      stepForm.keyword_id = null
      stepForm.step_data = {}
      dynamicFields.value = []
      keywordList.value = []
    }
  }
})

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false)
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 确认
const handleConfirm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (!valid) {
      return
    }
    
    // 处理数据：尝试解析JSON字符串
    const processedStepData = { ...stepForm.step_data }
    for (const key in processedStepData) {
      const val = processedStepData[key]
      if (['HEADERS', 'PARAMS', 'DATA', 'JSON'].includes(key) && typeof val === 'string') {
        try {
          // 只有当看起来像JSON对象或数组时才解析
          if ((val.trim().startsWith('{') || val.trim().startsWith('['))) {
             processedStepData[key] = JSON.parse(val)
          }
        } catch (e) {
          // 解析失败保持原样
        }
      }
    }

    // 发送数据
    const stepData = {
      run_order: stepForm.run_order,
      step_desc: stepForm.step_desc,
      operation_type_id: stepForm.operation_type_id,
      keyword_id: stepForm.keyword_id,
      step_data: processedStepData
    }
    
    emit('confirm', stepData)
    handleClose()
  })
}
</script>

<style scoped>
.dynamic-fields {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

:deep(.el-divider) {
  margin: 10px 0 20px 0;
}
</style>

