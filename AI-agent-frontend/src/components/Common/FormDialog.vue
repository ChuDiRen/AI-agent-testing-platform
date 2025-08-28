<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :fullscreen="fullscreen"
    :modal="modal"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :destroy-on-close="destroyOnClose"
    :append-to-body="appendToBody"
    @open="handleOpen"
    @opened="handleOpened"
    @close="handleClose"
    @closed="handleClosed"
    class="form-dialog"
  >
    <div class="dialog-content">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        :label-width="labelWidth"
        :label-position="labelPosition"
        :size="size"
        :disabled="formDisabled"
        class="dialog-form"
      >
        <el-row :gutter="gutter">
          <template v-for="field in (fields || [])" :key="field.prop">
            <el-col :span="field.span || defaultSpan">
              <el-form-item
                :label="field.label"
                :prop="field.prop"
                :required="field.required"
                :rules="field.rules"
                :label-width="field.labelWidth"
              >
                <!-- 输入框 -->
                <el-input
                  v-if="field.component === 'input'"
                  v-model="formData[field.prop]"
                  :type="field.inputType || 'text'"
                  :placeholder="field.placeholder || `请输入${field.label}`"
                  :clearable="field.clearable !== false"
                  :disabled="field.disabled || formDisabled"
                  :readonly="field.readonly"
                  :maxlength="field.maxlength"
                  :show-password="field.showPassword"
                  :rows="field.rows"
                  :autosize="field.autosize"
                  v-bind="field.props"
                />
                
                <!-- 数字输入框 -->
                <el-input-number
                  v-else-if="field.component === 'number'"
                  v-model="formData[field.prop]"
                  :placeholder="field.placeholder"
                  :disabled="field.disabled || formDisabled"
                  :min="field.min"
                  :max="field.max"
                  :step="field.step"
                  :precision="field.precision"
                  :controls-position="field.controlsPosition"
                  v-bind="field.props"
                />
                
                <!-- 选择器 -->
                <el-select
                  v-else-if="field.component === 'select'"
                  v-model="formData[field.prop]"
                  :placeholder="field.placeholder || `请选择${field.label}`"
                  :clearable="field.clearable !== false"
                  :disabled="field.disabled || formDisabled"
                  :multiple="field.multiple"
                  :filterable="field.filterable"
                  :remote="field.remote"
                  :remote-method="field.remoteMethod"
                  :loading="field.loading"
                  v-bind="field.props"
                >
                  <el-option
                    v-for="option in (field.options || [])"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                    :disabled="option.disabled"
                  />
                </el-select>
                
                <!-- 单选框组 -->
                <el-radio-group
                  v-else-if="field.component === 'radio'"
                  v-model="formData[field.prop]"
                  :disabled="field.disabled || formDisabled"
                  v-bind="field.props"
                >
                  <el-radio
                    v-for="option in (field.options || [])"
                    :key="option.value"
                    :label="option.value"
                    :disabled="option.disabled"
                  >
                    {{ option.label }}
                  </el-radio>
                </el-radio-group>
                
                <!-- 复选框组 -->
                <el-checkbox-group
                  v-else-if="field.component === 'checkbox'"
                  v-model="formData[field.prop]"
                  :disabled="field.disabled || formDisabled"
                  v-bind="field.props"
                >
                  <el-checkbox
                    v-for="option in (field.options || [])"
                    :key="option.value"
                    :label="option.value"
                    :disabled="option.disabled"
                  >
                    {{ option.label }}
                  </el-checkbox>
                </el-checkbox-group>
                
                <!-- 开关 -->
                <el-switch
                  v-else-if="field.component === 'switch'"
                  v-model="formData[field.prop]"
                  :disabled="field.disabled || formDisabled"
                  :active-text="field.activeText"
                  :inactive-text="field.inactiveText"
                  :active-value="field.activeValue"
                  :inactive-value="field.inactiveValue"
                  v-bind="field.props"
                />
                
                <!-- 日期选择器 -->
                <el-date-picker
                  v-else-if="field.component === 'date'"
                  v-model="formData[field.prop]"
                  :type="field.dateType || 'date'"
                  :placeholder="field.placeholder || `请选择${field.label}`"
                  :clearable="field.clearable !== false"
                  :disabled="field.disabled || formDisabled"
                  :format="field.format"
                  :value-format="field.valueFormat"
                  v-bind="field.props"
                />
                
                <!-- 时间选择器 -->
                <el-time-picker
                  v-else-if="field.component === 'time'"
                  v-model="formData[field.prop]"
                  :placeholder="field.placeholder || `请选择${field.label}`"
                  :clearable="field.clearable !== false"
                  :disabled="field.disabled || formDisabled"
                  :format="field.format"
                  :value-format="field.valueFormat"
                  v-bind="field.props"
                />
                
                <!-- 上传组件 -->
                <el-upload
                  v-else-if="field.component === 'upload'"
                  :action="field.action"
                  :disabled="field.disabled || formDisabled"
                  :multiple="field.multiple"
                  :accept="field.accept"
                  :limit="field.limit"
                  :file-list="formData[field.prop]"
                  :on-success="(response: any) => handleUploadSuccess(field.prop, response)"
                  :on-remove="(file: any) => handleUploadRemove(field.prop, file)"
                  v-bind="field.props"
                >
                  <el-button type="primary">点击上传</el-button>
                </el-upload>
                
                <!-- 自定义插槽 -->
                <slot
                  v-else-if="field.component === 'slot'"
                  :name="field.slot"
                  :field="field"
                  :value="formData[field.prop]"
                  :setValue="(val: any) => formData[field.prop] = val"
                  :disabled="field.disabled || formDisabled"
                />
                
                <!-- 提示文本 -->
                <div v-if="field.tip" class="field-tip">
                  <el-icon><InfoFilled /></el-icon>
                  {{ field.tip }}
                </div>
              </el-form-item>
            </el-col>
          </template>
        </el-row>
      </el-form>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" :disabled="loading">
          取消
        </el-button>
        <el-button
          type="primary"
          @click="handleConfirm"
          :loading="loading"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { InfoFilled } from '@element-plus/icons-vue'
import type { FormField, FormRule } from '@/api/types'

export interface FormDialogProps {
  // 对话框属性
  modelValue: boolean
  title: string
  width?: string | number
  fullscreen?: boolean
  modal?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  showClose?: boolean
  destroyOnClose?: boolean
  appendToBody?: boolean
  
  // 表单属性
  fields?: FormField[]
  formData?: Record<string, any>
  rules?: Record<string, FormRule[]>
  labelWidth?: string
  labelPosition?: 'left' | 'right' | 'top'
  size?: 'large' | 'default' | 'small'
  disabled?: boolean
  loading?: boolean
  
  // 布局属性
  gutter?: number
  defaultSpan?: number
}

const props = withDefaults(defineProps<FormDialogProps>(), {
  width: '600px',
  fullscreen: false,
  modal: true,
  closeOnClickModal: false,
  closeOnPressEscape: true,
  showClose: true,
  destroyOnClose: false,
  appendToBody: true,
  labelWidth: '100px',
  labelPosition: 'right',
  size: 'default',
  disabled: false,
  loading: false,
  gutter: 20,
  defaultSpan: 24,
  fields: () => []
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'update:formData': [data: Record<string, any>]
  confirm: [data: Record<string, any>]
  cancel: []
  open: []
  opened: []
  close: []
  closed: []
}>()

const formRef = ref()
const formData = reactive<Record<string, any>>({})

// 对话框显示状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 表单禁用状态
const formDisabled = computed(() => props.disabled || props.loading)

// 初始化表单数据
const initFormData = () => {
  // 清空表单数据
  Object.keys(formData).forEach(key => {
    delete formData[key]
  })
  
  // 设置默认值（安全遍历）
  const fields = Array.isArray(props.fields) ? props.fields : []
  fields.forEach((field) => {
    formData[field.prop] = field?.defaultValue ?? (field?.multiple ? [] : '')
  })
  
  // 合并传入的数据
  if (props.formData) {
    Object.assign(formData, props.formData)
  }
}

// 监听表单字段变化
watch(() => props.fields ?? [], initFormData, { immediate: true, deep: true })

// 监听外部数据变化
watch(() => props.formData, (newVal) => {
  if (newVal) {
    Object.assign(formData, newVal)
  }
}, { deep: true, immediate: true })

// 监听表单数据变化
watch(formData, (newVal) => {
  emit('update:formData', { ...newVal })
}, { deep: true })

// 对话框事件
const handleOpen = () => {
  initFormData()
  emit('open')
}

const handleOpened = () => {
  emit('opened')
}

const handleClose = () => {
  emit('close')
}

const handleClosed = () => {
  formRef.value?.clearValidate()
  emit('closed')
}

// 表单操作
const handleConfirm = async () => {
  try {
    const valid = await formRef.value?.validate()
    if (valid) {
      emit('confirm', { ...formData })
    }
  } catch (error) {
    console.warn('Form validation failed:', error)
  }
}

const handleCancel = () => {
  dialogVisible.value = false
  emit('cancel')
}

// 上传处理
const handleUploadSuccess = (prop: string, response: any) => {
  if (!formData[prop]) {
    formData[prop] = []
  }
  formData[prop].push(response)
}

const handleUploadRemove = (prop: string, file: any) => {
  const fileList = formData[prop] || []
  const index = fileList.findIndex((item: any) => item.uid === file.uid)
  if (index > -1) {
    fileList.splice(index, 1)
  }
}

// 表单方法
const validate = () => {
  return formRef.value?.validate()
}

const validateField = (prop: string) => {
  return formRef.value?.validateField(prop)
}

const resetFields = () => {
  formRef.value?.resetFields()
}

const clearValidate = () => {
  formRef.value?.clearValidate()
}

// 暴露方法
defineExpose({
  validate,
  validateField,
  resetFields,
  clearValidate,
  formData
})
</script>

<style scoped lang="scss">
.form-dialog {
  :deep(.el-dialog__body) {
    padding: 20px;
  }
  
  .dialog-content {
    max-height: 60vh;
    overflow-y: auto;
    
    .dialog-form {
      .field-tip {
        display: flex;
        align-items: center;
        margin-top: 4px;
        font-size: 12px;
        color: #909399;
        
        .el-icon {
          margin-right: 4px;
        }
      }
    }
  }
  
  .dialog-footer {
    text-align: right;
  }
}
</style>