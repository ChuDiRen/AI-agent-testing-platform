<!-- 通用表单对话框组件 -->
<template>
  <el-dialog
    v-model="dialogVisible"
    :title="title"
    :width="width"
    :top="top"
    :modal="modal"
    :modal-class="modalClass"
    :append-to-body="appendToBody"
    :lock-scroll="lockScroll"
    :custom-class="customClass"
    :open-delay="openDelay"
    :close-delay="closeDelay"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :before-close="handleBeforeClose"
    :center="center"
    :align-center="alignCenter"
    :destroy-on-close="destroyOnClose"
    @open="handleOpen"
    @opened="handleOpened"
    @close="handleClose"
    @closed="handleClosed"
    @open-auto-focus="handleOpenAutoFocus"
    @close-auto-focus="handleCloseAutoFocus"
  >
    <!-- 对话框内容 -->
    <div class="form-dialog-content" v-loading="loading">
      <!-- 自定义内容插槽 -->
      <slot v-if="$slots.default" />
      
      <!-- 动态表单 -->
      <el-form
        v-else
        ref="formRef"
        :model="formModel"
        :rules="formRules"
        :label-width="labelWidth"
        :label-position="labelPosition"
        :inline="inline"
        :size="size"
        :disabled="disabled"
        :validate-on-rule-change="validateOnRuleChange"
        :hide-required-asterisk="hideRequiredAsterisk"
        :show-message="showMessage"
        :inline-message="inlineMessage"
        :status-icon="statusIcon"
        @validate="handleValidate"
      >
        <template v-for="field in processedFields" :key="field.prop">
          <el-form-item
            :prop="field.prop"
            :label="field.label"
            :rules="field.rules"
            :error="field.error"
            :show-message="field.showMessage"
            :inline-message="field.inlineMessage"
            :size="field.size"
            :for="field.for"
            :required="field.required"
          >
            <!-- 自定义字段插槽 -->
            <slot 
              v-if="field.slot" 
              :name="field.slot" 
              :field="field" 
              :value="formModel[field.prop]"
              :setValue="(val: any) => setFieldValue(field.prop, val)"
            />
            
            <!-- 输入框 -->
            <el-input
              v-else-if="field.type === 'input' || !field.type"
              v-model="formModel[field.prop]"
              :type="field.inputType || 'text'"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :clearable="field.clearable"
              :show-password="field.showPassword"
              :show-word-limit="field.showWordLimit"
              :maxlength="field.maxlength"
              :minlength="field.minlength"
              :resize="field.resize"
              :autosize="field.autosize"
              :rows="field.rows"
              :cols="field.cols"
              :size="field.size"
              :prefix-icon="field.prefixIcon"
              :suffix-icon="field.suffixIcon"
              @change="handleFieldChange(field, $event)"
              @input="handleFieldInput(field, $event)"
              @focus="handleFieldFocus(field, $event)"
              @blur="handleFieldBlur(field, $event)"
            />
            
            <!-- 数字输入框 -->
            <el-input-number
              v-else-if="field.type === 'number'"
              v-model="formModel[field.prop]"
              :min="field.min"
              :max="field.max"
              :step="field.step"
              :step-strictly="field.stepStrictly"
              :precision="field.precision"
              :size="field.size"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :controls="field.controls"
              :controls-position="field.controlsPosition"
              :placeholder="field.placeholder"
              @change="handleFieldChange(field, $event)"
            />
            
            <!-- 选择器 -->
            <el-select
              v-else-if="field.type === 'select'"
              v-model="formModel[field.prop]"
              :multiple="field.multiple"
              :disabled="field.disabled"
              :value-key="field.valueKey"
              :size="field.size"
              :clearable="field.clearable"
              :collapse-tags="field.collapseTags"
              :collapse-tags-tooltip="field.collapseTagsTooltip"
              :multiple-limit="field.multipleLimit"
              :placeholder="field.placeholder"
              :filterable="field.filterable"
              :allow-create="field.allowCreate"
              :filter-method="field.filterMethod"
              :remote="field.remote"
              :remote-method="field.remoteMethod"
              :loading="field.loading"
              :loading-text="field.loadingText"
              :no-match-text="field.noMatchText"
              :no-data-text="field.noDataText"
              :popper-class="field.popperClass"
              :reserve-keyword="field.reserveKeyword"
              :default-first-option="field.defaultFirstOption"
              :teleported="field.teleported"
              :automatic-dropdown="field.automaticDropdown"
              @change="handleFieldChange(field, $event)"
              @visible-change="handleSelectVisibleChange(field, $event)"
              @remove-tag="handleSelectRemoveTag(field, $event)"
              @clear="handleSelectClear(field)"
              @blur="handleFieldBlur(field, $event)"
              @focus="handleFieldFocus(field, $event)"
            >
              <el-option
                v-for="option in field.options"
                :key="option.value"
                :label="option.label"
                :value="option.value"
                :disabled="option.disabled"
              />
            </el-select>
            
            <!-- 日期选择器 -->
            <el-date-picker
              v-else-if="field.type === 'date'"
              v-model="formModel[field.prop]"
              :type="field.dateType || 'date'"
              :placeholder="field.placeholder"
              :start-placeholder="field.startPlaceholder"
              :end-placeholder="field.endPlaceholder"
              :format="field.format"
              :value-format="field.valueFormat"
              :size="field.size"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :clearable="field.clearable"
              :disabled-date="field.disabledDate"
              :shortcuts="field.shortcuts"
              :cell-class-name="field.cellClassName"
              :range-separator="field.rangeSeparator"
              :default-value="field.defaultValue"
              :default-time="field.defaultTime"
              :teleported="field.teleported"
              @change="handleFieldChange(field, $event)"
              @blur="handleFieldBlur(field, $event)"
              @focus="handleFieldFocus(field, $event)"
              @calendar-change="handleCalendarChange(field, $event)"
              @panel-change="handlePanelChange(field, $event)"
              @visible-change="handleDateVisibleChange(field, $event)"
            />
            
            <!-- 时间选择器 -->
            <el-time-picker
              v-else-if="field.type === 'time'"
              v-model="formModel[field.prop]"
              :placeholder="field.placeholder"
              :start-placeholder="field.startPlaceholder"
              :end-placeholder="field.endPlaceholder"
              :is-range="field.isRange"
              :arrow-control="field.arrowControl"
              :format="field.format"
              :value-format="field.valueFormat"
              :size="field.size"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :clearable="field.clearable"
              :range-separator="field.rangeSeparator"
              :default-value="field.defaultValue"
              :teleported="field.teleported"
              @change="handleFieldChange(field, $event)"
              @blur="handleFieldBlur(field, $event)"
              @focus="handleFieldFocus(field, $event)"
              @visible-change="handleTimeVisibleChange(field, $event)"
            />
            
            <!-- 开关 -->
            <el-switch
              v-else-if="field.type === 'switch'"
              v-model="formModel[field.prop]"
              :size="field.size"
              :disabled="field.disabled"
              :loading="field.loading"
              :width="field.width"
              :inline-prompt="field.inlinePrompt"
              :active-icon="field.activeIcon"
              :inactive-icon="field.inactiveIcon"
              :active-text="field.activeText"
              :inactive-text="field.inactiveText"
              :active-value="field.activeValue"
              :inactive-value="field.inactiveValue"
              :active-color="field.activeColor"
              :inactive-color="field.inactiveColor"
              :border-color="field.borderColor"
              :name="field.name"
              :validate-event="field.validateEvent"
              @change="handleFieldChange(field, $event)"
            />
            
            <!-- 单选框组 -->
            <el-radio-group
              v-else-if="field.type === 'radio'"
              v-model="formModel[field.prop]"
              :size="field.size"
              :disabled="field.disabled"
              :text-color="field.textColor"
              :fill="field.fill"
              @change="handleFieldChange(field, $event)"
            >
              <el-radio
                v-for="option in field.options"
                :key="option.value"
                :label="option.value"
                :disabled="option.disabled"
                :border="field.border"
                :size="field.size"
              >
                {{ option.label }}
              </el-radio>
            </el-radio-group>
            
            <!-- 复选框组 -->
            <el-checkbox-group
              v-else-if="field.type === 'checkbox'"
              v-model="formModel[field.prop]"
              :size="field.size"
              :disabled="field.disabled"
              :min="field.min"
              :max="field.max"
              :text-color="field.textColor"
              :fill="field.fill"
              @change="handleFieldChange(field, $event)"
            >
              <el-checkbox
                v-for="option in field.options"
                :key="option.value"
                :label="option.value"
                :disabled="option.disabled"
                :border="field.border"
                :size="field.size"
                :checked="field.checked"
                :indeterminate="field.indeterminate"
              >
                {{ option.label }}
              </el-checkbox>
            </el-checkbox-group>
            
            <!-- 滑块 -->
            <el-slider
              v-else-if="field.type === 'slider'"
              v-model="formModel[field.prop]"
              :min="field.min"
              :max="field.max"
              :step="field.step"
              :show-input="field.showInput"
              :show-input-controls="field.showInputControls"
              :size="field.size"
              :disabled="field.disabled"
              :range="field.range"
              :vertical="field.vertical"
              :height="field.height"
              :label="field.label"
              :debounce="field.debounce"
              :tooltip-class="field.tooltipClass"
              :format-tooltip="field.formatTooltip"
              :marks="field.marks"
              @change="handleFieldChange(field, $event)"
              @input="handleFieldInput(field, $event)"
            />
            
            <!-- 文本域 -->
            <el-input
              v-else-if="field.type === 'textarea'"
              v-model="formModel[field.prop]"
              type="textarea"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :readonly="field.readonly"
              :clearable="field.clearable"
              :show-word-limit="field.showWordLimit"
              :maxlength="field.maxlength"
              :minlength="field.minlength"
              :resize="field.resize"
              :autosize="field.autosize"
              :rows="field.rows || 4"
              :size="field.size"
              @change="handleFieldChange(field, $event)"
              @input="handleFieldInput(field, $event)"
              @focus="handleFieldFocus(field, $event)"
              @blur="handleFieldBlur(field, $event)"
            />
            
            <!-- 级联选择器 -->
            <el-cascader
              v-else-if="field.type === 'cascader'"
              v-model="formModel[field.prop]"
              :options="field.options"
              :props="field.cascaderProps"
              :size="field.size"
              :placeholder="field.placeholder"
              :disabled="field.disabled"
              :clearable="field.clearable"
              :show-all-levels="field.showAllLevels"
              :collapse-tags="field.collapseTags"
              :collapse-tags-tooltip="field.collapseTagsTooltip"
              :separator="field.separator"
              :filterable="field.filterable"
              :filter-method="field.filterMethod"
              :debounce="field.debounce"
              :before-filter="field.beforeFilter"
              :popper-class="field.popperClass"
              :teleported="field.teleported"
              @change="handleFieldChange(field, $event)"
              @expand-change="handleCascaderExpandChange(field, $event)"
              @blur="handleFieldBlur(field, $event)"
              @focus="handleFieldFocus(field, $event)"
              @visible-change="handleCascaderVisibleChange(field, $event)"
              @remove-tag="handleCascaderRemoveTag(field, $event)"
            />
            
            <!-- 自定义组件 -->
            <component
              v-else-if="field.component"
              :is="field.component"
              v-model="formModel[field.prop]"
              v-bind="field.componentProps || {}"
              @change="handleFieldChange(field, $event)"
            />
            
            <!-- 提示文本 -->
            <div v-if="field.tip" class="field-tip">
              <el-text type="info" size="small">{{ field.tip }}</el-text>
            </div>
          </el-form-item>
        </template>
      </el-form>
    </div>
    
    <!-- 对话框底部 -->
    <template #footer>
      <slot name="footer" :loading="loading" :validate="validateForm" :reset="resetForm">
        <div class="dialog-footer">
          <el-button @click="handleCancel" :disabled="loading">
            {{ cancelText }}
          </el-button>
          <el-button 
            type="primary" 
            @click="handleConfirm" 
            :loading="loading"
            :disabled="loading"
          >
            {{ confirmText }}
          </el-button>
        </div>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'

// 定义字段接口
export interface FormField {
  prop: string
  label: string
  type?: 'input' | 'number' | 'select' | 'date' | 'time' | 'switch' | 'radio' | 'checkbox' | 'slider' | 'textarea' | 'cascader'
  rules?: any[]
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  tip?: string
  slot?: string
  
  // input相关
  inputType?: string
  clearable?: boolean
  showPassword?: boolean
  showWordLimit?: boolean
  maxlength?: number
  minlength?: number
  resize?: string
  autosize?: boolean | object
  rows?: number
  cols?: number
  prefixIcon?: string
  suffixIcon?: string
  
  // number相关
  min?: number
  max?: number
  step?: number
  stepStrictly?: boolean
  precision?: number
  controls?: boolean
  controlsPosition?: string
  
  // select相关
  multiple?: boolean
  valueKey?: string
  collapseTags?: boolean
  collapseTagsTooltip?: boolean
  multipleLimit?: number
  filterable?: boolean
  allowCreate?: boolean
  filterMethod?: Function
  remote?: boolean
  remoteMethod?: Function
  loading?: boolean
  loadingText?: string
  noMatchText?: string
  noDataText?: string
  popperClass?: string
  reserveKeyword?: boolean
  defaultFirstOption?: boolean
  teleported?: boolean
  automaticDropdown?: boolean
  options?: Array<{ label: string; value: any; disabled?: boolean }>
  
  // date相关
  dateType?: string
  startPlaceholder?: string
  endPlaceholder?: string
  format?: string
  valueFormat?: string
  disabledDate?: Function
  shortcuts?: any[]
  cellClassName?: Function
  rangeSeparator?: string
  defaultValue?: any
  defaultTime?: any
  
  // time相关
  isRange?: boolean
  arrowControl?: boolean
  
  // switch相关
  width?: number
  inlinePrompt?: boolean
  activeIcon?: string
  inactiveIcon?: string
  activeText?: string
  inactiveText?: string
  activeValue?: any
  inactiveValue?: any
  activeColor?: string
  inactiveColor?: string
  borderColor?: string
  name?: string
  validateEvent?: boolean
  
  // radio/checkbox相关
  textColor?: string
  fill?: string
  border?: boolean
  checked?: boolean
  indeterminate?: boolean
  
  // slider相关
  showInput?: boolean
  showInputControls?: boolean
  range?: boolean
  vertical?: boolean
  height?: string
  debounce?: number
  tooltipClass?: string
  formatTooltip?: Function
  marks?: object
  
  // cascader相关
  cascaderProps?: object
  showAllLevels?: boolean
  separator?: string
  beforeFilter?: Function
  
  // 其他
  size?: string
  error?: string
  showMessage?: boolean
  inlineMessage?: boolean
  for?: string
  component?: any
  componentProps?: object
}

// Props定义
interface Props {
  modelValue: boolean
  title: string
  width?: string | number
  top?: string
  modal?: boolean
  modalClass?: string
  appendToBody?: boolean
  lockScroll?: boolean
  customClass?: string
  openDelay?: number
  closeDelay?: number
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  showClose?: boolean
  beforeClose?: Function
  center?: boolean
  alignCenter?: boolean
  destroyOnClose?: boolean
  
  // 表单相关
  fields?: FormField[]
  formData?: Record<string, any>
  rules?: FormRules
  loading?: boolean
  labelWidth?: string
  labelPosition?: string
  inline?: boolean
  size?: string
  disabled?: boolean
  validateOnRuleChange?: boolean
  hideRequiredAsterisk?: boolean
  showMessage?: boolean
  inlineMessage?: boolean
  statusIcon?: boolean
  
  // 按钮文本
  confirmText?: string
  cancelText?: string
}

const props = withDefaults(defineProps<Props>(), {
  width: '600px',
  top: '15vh',
  modal: true,
  appendToBody: true,
  lockScroll: true,
  closeOnClickModal: false,
  closeOnPressEscape: true,
  showClose: true,
  center: false,
  alignCenter: true,
  destroyOnClose: true,
  loading: false,
  labelWidth: '120px',
  labelPosition: 'right',
  inline: false,
  disabled: false,
  validateOnRuleChange: true,
  hideRequiredAsterisk: false,
  showMessage: true,
  inlineMessage: false,
  statusIcon: false,
  confirmText: '确定',
  cancelText: '取消',
  fields: () => [],
  formData: () => ({})
})

// Emits定义
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [data: Record<string, any>]
  cancel: []
  open: []
  opened: []
  close: []
  closed: []
  'open-auto-focus': []
  'close-auto-focus': []
  validate: [prop: string, isValid: boolean, message: string]
  'field-change': [field: FormField, value: any]
}>()

// 引用
const formRef = ref<FormInstance>()

// 响应式数据
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const formModel = ref<Record<string, any>>({})
const formRules = ref<FormRules>({})

// 计算属性
const processedFields = computed(() => {
  return props.fields?.filter(field => field.prop && field.label) || []
})

// 监听表单数据变化
watch(() => props.formData, (newData) => {
  if (newData) {
    formModel.value = { ...newData }
  }
}, { immediate: true, deep: true })

// 监听字段变化，生成规则
watch(() => props.fields, (newFields) => {
  const rules: FormRules = {}
  newFields?.forEach(field => {
    if (field.rules) {
      rules[field.prop] = field.rules
    }
  })
  formRules.value = rules
}, { immediate: true, deep: true })

// 监听表单规则变化
watch(() => props.rules, (newRules) => {
  if (newRules) {
    formRules.value = { ...formRules.value, ...newRules }
  }
}, { immediate: true, deep: true })

// 工具函数
const setFieldValue = (prop: string, value: any) => {
  formModel.value[prop] = value
}

// 表单验证
const validateForm = async (): Promise<boolean> => {
  if (!formRef.value) return false
  
  try {
    await formRef.value.validate()
    return true
  } catch (error) {
    return false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields()
  formModel.value = { ...props.formData }
}

// 清空验证
const clearValidate = (props?: string | string[]) => {
  formRef.value?.clearValidate(props)
}

// 事件处理函数
const handleBeforeClose = (done: Function) => {
  if (props.beforeClose) {
    props.beforeClose(done)
  } else {
    done()
  }
}

const handleOpen = () => {
  emit('open')
}

const handleOpened = () => {
  emit('opened')
  // 对话框打开后，重置表单数据
  nextTick(() => {
    formModel.value = { ...props.formData }
    clearValidate()
  })
}

const handleClose = () => {
  emit('close')
}

const handleClosed = () => {
  emit('closed')
}

const handleOpenAutoFocus = () => {
  emit('open-auto-focus')
}

const handleCloseAutoFocus = () => {
  emit('close-auto-focus')
}

const handleValidate = (prop: string, isValid: boolean, message: string) => {
  emit('validate', prop, isValid, message)
}

const handleFieldChange = (field: FormField, value: any) => {
  emit('field-change', field, value)
}

const handleFieldInput = (field: FormField, value: any) => {
  // 可以在这里添加输入事件处理
}

const handleFieldFocus = (field: FormField, event: Event) => {
  // 可以在这里添加焦点事件处理
}

const handleFieldBlur = (field: FormField, event: Event) => {
  // 可以在这里添加失焦事件处理
}

// Select相关事件
const handleSelectVisibleChange = (field: FormField, visible: boolean) => {
  // 处理选择器显示状态变化
}

const handleSelectRemoveTag = (field: FormField, tag: any) => {
  // 处理选择器移除标签
}

const handleSelectClear = (field: FormField) => {
  // 处理选择器清空
}

// Date相关事件
const handleCalendarChange = (field: FormField, dates: any) => {
  // 处理日历变化
}

const handlePanelChange = (field: FormField, date: any, mode: string) => {
  // 处理面板变化
}

const handleDateVisibleChange = (field: FormField, visible: boolean) => {
  // 处理日期选择器显示状态变化
}

// Time相关事件
const handleTimeVisibleChange = (field: FormField, visible: boolean) => {
  // 处理时间选择器显示状态变化
}

// Cascader相关事件
const handleCascaderExpandChange = (field: FormField, activeNames: any) => {
  // 处理级联选择器展开变化
}

const handleCascaderVisibleChange = (field: FormField, visible: boolean) => {
  // 处理级联选择器显示状态变化
}

const handleCascaderRemoveTag = (field: FormField, tag: any) => {
  // 处理级联选择器移除标签
}

// 按钮事件
const handleConfirm = async () => {
  const isValid = await validateForm()
  if (isValid) {
    emit('confirm', { ...formModel.value })
  }
}

const handleCancel = () => {
  emit('cancel')
  dialogVisible.value = false
}

// 暴露方法
defineExpose({
  validateForm,
  resetForm,
  clearValidate,
  formRef,
  formModel
})
</script>

<style scoped lang="scss">
.form-dialog-content {
  padding: 20px 0;
  
  .field-tip {
    margin-top: 4px;
    
    :deep(.el-text) {
      font-size: 12px;
      line-height: 1.4;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-dialog__body) {
  padding: 20px 24px;
}

:deep(.el-dialog__footer) {
  padding: 12px 24px 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}

:deep(.el-form-item) {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input),
:deep(.el-select),
:deep(.el-date-editor),
:deep(.el-time-picker),
:deep(.el-cascader) {
  width: 100%;
}

:deep(.el-textarea) {
  .el-textarea__inner {
    resize: vertical;
  }
}
</style>