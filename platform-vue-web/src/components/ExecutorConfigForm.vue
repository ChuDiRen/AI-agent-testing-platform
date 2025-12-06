<template>
  <div class="executor-config-form">
    <el-form :model="formData" label-width="120px" size="default">
      <template v-for="param in visibleParams" :key="param.name">
        <!-- select 类型 -->
        <el-form-item v-if="param.type === 'select'" :label="param.label || param.name">
          <el-select v-model="formData[param.name]" :placeholder="param.help || '请选择'" style="width: 100%">
            <el-option
              v-for="opt in param.options"
              :key="typeof opt === 'object' ? opt.value : opt"
              :label="typeof opt === 'object' ? opt.label : opt"
              :value="typeof opt === 'object' ? opt.value : opt"
            />
          </el-select>
          <div v-if="param.help" class="param-help">{{ param.help }}</div>
        </el-form-item>

        <!-- boolean 类型 -->
        <el-form-item v-else-if="param.type === 'boolean'" :label="param.label || param.name">
          <el-switch v-model="formData[param.name]" />
          <span class="switch-label">{{ formData[param.name] ? '是' : '否' }}</span>
          <div v-if="param.help" class="param-help">{{ param.help }}</div>
        </el-form-item>

        <!-- string/其他类型 -->
        <el-form-item v-else :label="param.label || param.name">
          <el-input
            v-model="formData[param.name]"
            :placeholder="param.help || '请输入'"
            clearable
          />
          <div v-if="param.help" class="param-help">{{ param.help }}</div>
        </el-form-item>
      </template>

      <el-empty v-if="!visibleParams.length" description="该执行器无需配置参数" :image-size="60" />
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  // config_schema 对象，包含 params 数组
  configSchema: {
    type: Object,
    default: () => ({})
  },
  // 初始值
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

// 表单数据
const formData = ref({})

// 获取参数列表
const params = computed(() => {
  if (!props.configSchema) return []
  // 优先使用 params 数组
  if (Array.isArray(props.configSchema.params)) {
    return props.configSchema.params
  }
  // 回退到 properties 对象
  if (props.configSchema.properties) {
    return Object.entries(props.configSchema.properties).map(([name, prop]) => ({
      name,
      ...prop
    }))
  }
  return []
})

// 可见参数（根据 show_when 条件过滤）
const visibleParams = computed(() => {
  return params.value.filter(param => {
    if (!param.show_when) return true
    // 检查条件
    for (const [key, value] of Object.entries(param.show_when)) {
      if (formData.value[key] !== value) {
        return false
      }
    }
    return true
  })
})

// 初始化表单数据
const initFormData = () => {
  const data = { ...props.modelValue }
  params.value.forEach(param => {
    if (!(param.name in data)) {
      data[param.name] = param.default ?? (param.type === 'boolean' ? false : '')
    }
  })
  formData.value = data
}

// 监听 configSchema 变化
watch(() => props.configSchema, () => {
  initFormData()
}, { immediate: true, deep: true })

// 监听 modelValue 变化
watch(() => props.modelValue, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(formData.value)) {
    formData.value = { ...newVal }
  }
}, { deep: true })

// 监听表单数据变化，向上同步
watch(formData, (newVal) => {
  emit('update:modelValue', { ...newVal })
}, { deep: true })

onMounted(() => {
  initFormData()
})
</script>

<style scoped>
.executor-config-form {
  padding: 10px 0;
}

.param-help {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.switch-label {
  margin-left: 10px;
  color: #606266;
}
</style>
