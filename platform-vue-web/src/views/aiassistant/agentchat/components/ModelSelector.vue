<template>
  <div class="model-selector">
    <el-form :model="form" label-width="80px" size="small">
      <el-form-item label="提供商">
        <el-select v-model="form.provider" @change="handleProviderChange" placeholder="选择AI提供商">
          <el-option v-for="p in providers" :key="p.code" :label="p.name" :value="p.code">
            <span>{{ p.name }}</span>
            <span class="provider-url">{{ p.base_url }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="API密钥">
        <el-input v-model="form.api_key" type="password" show-password placeholder="输入API密钥" />
      </el-form-item>
      
      <el-form-item label="模型">
        <el-select v-model="form.model" placeholder="选择模型">
          <el-option v-for="m in currentModels" :key="m" :label="m" :value="m" />
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleTest" :loading="testing">
          测试连接
        </el-button>
        <el-tag v-if="testResult" :type="testResult.success ? 'success' : 'danger'" class="test-result">
          {{ testResult.success ? '连接成功' : testResult.error }}
        </el-tag>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '~/utils/request'

const emit = defineEmits(['update:modelValue', 'change'])

const props = defineProps({
  modelValue: { type: Object, default: () => ({}) }
})

const form = ref({
  provider: 'siliconflow',
  api_key: '',
  model: ''
})

const providers = ref([])
const testing = ref(false)
const testResult = ref(null)

const currentModels = computed(() => {
  const provider = providers.value.find(p => p.code === form.value.provider)
  return provider?.models || []
})

const handleProviderChange = () => {
  const provider = providers.value.find(p => p.code === form.value.provider)
  if (provider?.models?.length) {
    form.value.model = provider.models[0]
  }
  emitChange()
}


const emitChange = () => {
  const config = {
    provider: form.value.provider,
    api_key: form.value.api_key,
    reader_model: form.value.model,
    writer_model: form.value.model,
    reviewer_model: form.value.model
  }
  emit('update:modelValue', config)
  emit('change', config)
}

const handleTest = async () => {
  if (!form.value.api_key) {
    ElMessage.warning('请输入API密钥')
    return
  }
  testing.value = true
  testResult.value = null
  try {
    const res = await request.post('/LangGraph/model/test', {
      provider: form.value.provider,
      api_key: form.value.api_key,
      model_code: form.value.model
    })
    testResult.value = res.code === 200 ? { success: true } : { success: false, error: res.msg }
  } catch (e) {
    testResult.value = { success: false, error: e.message }
  } finally {
    testing.value = false
  }
}

const loadProviders = async () => {
  try {
    const res = await request.get('/LangGraph/providers')
    if (res.code === 200) {
      providers.value = res.data
      if (providers.value.length && !form.value.model) {
        handleProviderChange()
      }
    }
  } catch (e) {
    console.error('Failed to load providers:', e)
  }
}

onMounted(() => {
  loadProviders()
  if (props.modelValue) {
    Object.assign(form.value, props.modelValue)
  }
})
</script>

<style scoped>
.model-selector {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.provider-url {
  font-size: 11px;
  color: #909399;
  margin-left: 8px;
}
.test-result {
  margin-left: 12px;
}
</style>
