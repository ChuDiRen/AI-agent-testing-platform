<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visible"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="模型名称" prop="model_name">
        <el-input v-model="form.model_name" placeholder="请输入模型名称" />
      </el-form-item>
      <el-form-item label="模型代码" prop="model_code">
        <el-input v-model="form.model_code" placeholder="如:deepseek-chat" :disabled="isEdit" />
      </el-form-item>
      <el-form-item label="提供商" prop="provider">
        <el-input v-model="form.provider" placeholder="如:DeepSeek" />
      </el-form-item>
      <el-form-item label="API地址" prop="api_url">
        <el-input v-model="form.api_url" placeholder="请输入API地址" />
      </el-form-item>
      <el-form-item label="API Key" prop="api_key">
        <el-input v-model="form.api_key" type="password" show-password placeholder="请输入API Key" />
      </el-form-item>
      <el-form-item label="是否启用" prop="is_enabled">
        <el-switch v-model="form.is_enabled" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入模型描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { insertData, updateData } from './aimodel'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  formData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'success'])

// 对话框显示状态
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 表单引用
const formRef = ref(null)
const submitLoading = ref(false)

// 是否为编辑模式
const isEdit = computed(() => !!props.formData.id)

// 对话框标题
const dialogTitle = computed(() => isEdit.value ? '编辑模型' : '新增模型')

// 表单数据
const form = reactive({
  id: null,
  model_name: '',
  model_code: '',
  provider: '',
  api_url: '',
  api_key: '',
  is_enabled: true,
  description: ''
})

// 表单验证规则
const rules = {
  model_name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  model_code: [{ required: true, message: '请输入模型代码', trigger: 'blur' }],
  provider: [{ required: true, message: '请输入提供商', trigger: 'blur' }],
  api_url: [{ required: true, message: '请输入API地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API Key', trigger: 'blur' }]
}

// 监听formData变化，更新表单数据
watch(() => props.formData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    Object.assign(form, newData)
  } else {
    resetForm()
  }
}, { immediate: true, deep: true })

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    model_name: '',
    model_code: '',
    provider: '',
    api_url: '',
    api_key: '',
    is_enabled: true,
    description: ''
  })
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitLoading.value = true
    
    const data = { ...form }
    if (isEdit.value) {
      delete data.create_time
      delete data.modify_time
    } else {
      delete data.id
    }
    
    const res = isEdit.value 
      ? await updateData(data) 
      : await insertData(data)
      
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || res.data.message || (isEdit.value ? '更新成功' : '新增成功'))
      emit('success')
      handleClose()
    } else {
      ElMessage.error(res.data.msg || res.data.message || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    if (error !== false) {
      ElMessage.error('操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  resetForm()
  visible.value = false
}
</script>

<style scoped>
:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>

