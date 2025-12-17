<template>
  <div class="environment-selector">
    <el-select
      v-model="currentEnvId"
      placeholder="选择环境"
      size="default"
      :style="{ width: width }"
      @change="handleEnvChange"
    >
      <template #prefix>
        <el-icon :style="{ color: getEnvColor(currentEnv?.env_code) }">
          <Monitor />
        </el-icon>
      </template>
      <el-option
        v-for="env in environments"
        :key="env.id"
        :label="env.env_name"
        :value="env.id"
      >
        <div class="env-option">
          <el-tag :type="getEnvTagType(env.env_code)" size="small" effect="plain">
            {{ env.env_code }}
          </el-tag>
          <span class="env-name">{{ env.env_name }}</span>
          <el-tag v-if="env.is_default === 1" type="success" size="small">默认</el-tag>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Monitor } from '@element-plus/icons-vue'
import { queryByProject, getDefaultEnv } from '~/views/apitest/environment/apiEnvironment'

const props = defineProps({
  projectId: {
    type: Number,
    default: null
  },
  modelValue: {
    type: Number,
    default: null
  },
  width: {
    type: String,
    default: '180px'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const environments = ref([])
const currentEnvId = ref(props.modelValue)

// 当前选中的环境
const currentEnv = computed(() => {
  return environments.value.find(e => e.id === currentEnvId.value)
})

// 获取环境标签类型
const getEnvTagType = (code) => {
  const typeMap = {
    dev: 'info',
    test: 'warning',
    prod: 'danger',
    uat: 'success',
    pre: ''
  }
  return typeMap[code] || 'info'
}

// 获取环境颜色
const getEnvColor = (code) => {
  const colorMap = {
    dev: '#909399',
    test: '#E6A23C',
    prod: '#F56C6C',
    uat: '#67C23A',
    pre: '#409EFF'
  }
  return colorMap[code] || '#909399'
}

// 加载环境列表
const loadEnvironments = async () => {
  if (!props.projectId) {
    environments.value = []
    return
  }
  
  try {
    const res = await queryByProject(props.projectId)
    if (res.data.code === 200) {
      environments.value = res.data.data || []
      
      // 如果没有选中环境，选择默认环境
      if (!currentEnvId.value && environments.value.length > 0) {
        const defaultEnv = environments.value.find(e => e.is_default === 1)
        currentEnvId.value = defaultEnv ? defaultEnv.id : environments.value[0].id
        emit('update:modelValue', currentEnvId.value)
        emit('change', currentEnv.value)
      }
    }
  } catch (error) {
    console.error('加载环境失败:', error)
  }
}

// 环境切换
const handleEnvChange = (envId) => {
  emit('update:modelValue', envId)
  emit('change', currentEnv.value)
}

// 获取当前环境配置
const getCurrentEnv = () => {
  return currentEnv.value
}

// 获取环境变量
const getEnvVariables = () => {
  if (!currentEnv.value?.env_variables) return {}
  try {
    const vars = JSON.parse(currentEnv.value.env_variables)
    const result = {}
    vars.forEach(v => {
      if (v.key) result[v.key] = v.value
    })
    return result
  } catch {
    return {}
  }
}

// 获取基础URL
const getBaseUrl = () => {
  return currentEnv.value?.base_url || ''
}

// 监听项目变化
watch(() => props.projectId, () => {
  currentEnvId.value = null
  loadEnvironments()
})

// 监听外部值变化
watch(() => props.modelValue, (val) => {
  currentEnvId.value = val
})

onMounted(() => {
  loadEnvironments()
})

// 暴露方法
defineExpose({
  getCurrentEnv,
  getEnvVariables,
  getBaseUrl,
  reload: loadEnvironments
})
</script>

<style scoped>
.environment-selector {
  display: inline-block;
}

.env-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.env-name {
  flex: 1;
}
</style>
