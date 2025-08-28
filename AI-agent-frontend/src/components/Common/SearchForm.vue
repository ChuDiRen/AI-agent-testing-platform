<template>
  <div class="search-form">
    <el-form
      ref="formRef"
      :model="formData"
      :inline="inline"
      :label-width="labelWidth"
      class="search-form-content"
    >
      <template v-for="field in fields" :key="field.prop">
        <el-form-item
          :label="field.label"
          :prop="field.prop"
          :label-width="field.labelWidth"
        >
          <!-- 输入框 -->
          <el-input
            v-if="field.component === 'input'"
            v-model="formData[field.prop]"
            :placeholder="field.placeholder || `请输入${field.label}`"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            v-bind="field.props"
            @keyup.enter="handleSearch"
          />
          
          <!-- 选择器 -->
          <el-select
            v-else-if="field.component === 'select'"
            v-model="formData[field.prop]"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            :multiple="field.multiple"
            v-bind="field.props"
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
            v-else-if="field.component === 'date'"
            v-model="formData[field.prop]"
            :type="field.dateType || 'date'"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            :format="field.format"
            :value-format="field.valueFormat"
            v-bind="field.props"
          />
          
          <!-- 日期范围选择器 -->
          <el-date-picker
            v-else-if="field.component === 'daterange'"
            v-model="formData[field.prop]"
            type="daterange"
            :range-separator="field.rangeSeparator || '至'"
            :start-placeholder="field.startPlaceholder || '开始日期'"
            :end-placeholder="field.endPlaceholder || '结束日期'"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            :format="field.format"
            :value-format="field.valueFormat"
            v-bind="field.props"
          />
          
          <!-- 数字输入框 -->
          <el-input-number
            v-else-if="field.component === 'number'"
            v-model="formData[field.prop]"
            :placeholder="field.placeholder"
            :disabled="field.disabled"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            v-bind="field.props"
          />
          
          <!-- 树形选择器 -->
          <el-tree-select
            v-else-if="field.component === 'tree-select'"
            v-model="formData[field.prop]"
            :data="field.data"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            :multiple="field.multiple"
            :check-strictly="field.checkStrictly"
            :node-key="field.nodeKey || 'id'"
            :props="field.treeProps || { label: 'label', children: 'children' }"
            v-bind="field.props"
          />
          
          <!-- 级联选择器 -->
          <el-cascader
            v-else-if="field.component === 'cascader'"
            v-model="formData[field.prop]"
            :options="field.options"
            :placeholder="field.placeholder || `请选择${field.label}`"
            :clearable="field.clearable !== false"
            :disabled="field.disabled"
            :props="field.cascaderProps"
            v-bind="field.props"
          />
          
          <!-- 自定义插槽 -->
          <slot
            v-else-if="field.component === 'slot'"
            :name="field.slot"
            :field="field"
            :value="formData[field.prop]"
            :setValue="(val: any) => formData[field.prop] = val"
          />
        </el-form-item>
      </template>
      
      <!-- 操作按钮 -->
      <el-form-item>
        <el-button
          type="primary"
          :icon="Search"
          @click="handleSearch"
          :loading="loading"
        >
          搜索
        </el-button>
        <el-button
          :icon="Refresh"
          @click="handleReset"
        >
          重置
        </el-button>
        <el-button
          v-if="showToggle && fields.length > toggleCount"
          type="text"
          @click="toggleExpanded"
        >
          {{ expanded ? '收起' : '展开' }}
          <el-icon class="toggle-icon" :class="{ 'expanded': expanded }">
            <ArrowUp />
          </el-icon>
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { Search, Refresh, ArrowUp } from '@element-plus/icons-vue'
import type { SearchField } from '@/api/types'

export interface SearchFormProps {
  // 表单字段配置
  fields: SearchField[]
  // 初始值
  modelValue?: Record<string, any>
  // 是否内联
  inline?: boolean
  // 标签宽度
  labelWidth?: string
  // 加载状态
  loading?: boolean
  // 是否显示展开/收起
  showToggle?: boolean
  // 展开收起的临界数量
  toggleCount?: number
}

const props = withDefaults(defineProps<SearchFormProps>(), {
  inline: true,
  labelWidth: '80px',
  loading: false,
  showToggle: true,
  toggleCount: 3
})

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, any>]
  search: [value: Record<string, any>]
  reset: []
}>()

const formRef = ref()
const expanded = ref(false)

// 表单数据
const formData = reactive<Record<string, any>>({})

// 初始化表单数据
const initFormData = () => {
  props.fields.forEach(field => {
    if (formData[field.prop] === undefined) {
      formData[field.prop] = field.defaultValue ?? (field.multiple ? [] : '')
    }
  })
  
  // 合并传入的初始值
  if (props.modelValue) {
    Object.assign(formData, props.modelValue)
  }
}

// 监听字段变化重新初始化
watch(() => props.fields, initFormData, { immediate: true, deep: true })

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    Object.assign(formData, newVal)
  }
}, { deep: true })

// 监听表单数据变化，同步到外部
watch(formData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

// 显示的字段 - 暂时注释掉未使用的计算属性
// const visibleFields = computed(() => {
//   if (!props.showToggle || expanded.value || props.fields.length <= props.toggleCount) {
//     return props.fields
//   }
//   return props.fields.slice(0, props.toggleCount)
// })

// 搜索
const handleSearch = () => {
  emit('search', { ...formData })
}

// 重置
const handleReset = () => {
  formRef.value?.resetFields()
  
  // 重置为默认值
  props.fields.forEach(field => {
    formData[field.prop] = field.defaultValue ?? (field.multiple ? [] : '')
  })
  
  emit('reset')
  emit('search', { ...formData })
}

// 切换展开/收起
const toggleExpanded = () => {
  expanded.value = !expanded.value
}

// 验证表单
const validate = () => {
  return formRef.value?.validate()
}

// 清除验证
const clearValidate = () => {
  formRef.value?.clearValidate()
}

// 重置字段
const resetFields = () => {
  formRef.value?.resetFields()
}

// 暴露方法
defineExpose({
  validate,
  clearValidate,
  resetFields,
  formData
})
</script>

<style scoped lang="scss">
.search-form {
  background: #fff;
  padding: 20px;
  border-radius: 6px;
  margin-bottom: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  
  .search-form-content {
    :deep(.el-form-item) {
      margin-bottom: 16px;
      
      .el-form-item__content {
        width: 200px;
      }
    }
    
    :deep(.el-input), 
    :deep(.el-select), 
    :deep(.el-date-editor), 
    :deep(.el-tree-select), 
    :deep(.el-cascader) {
      width: 100%;
    }
  }
  
  .toggle-icon {
    margin-left: 4px;
    transition: transform 0.3s;
    
    &.expanded {
      transform: rotate(180deg);
    }
  }
}
</style>