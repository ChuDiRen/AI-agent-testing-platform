<template>
  <el-dialog
    :title="dialogTitle"
    v-model="visible"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-form-item label="模板名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入模板名称" :disabled="viewMode" />
      </el-form-item>
      <el-form-item label="模板类型" prop="template_type">
        <el-select v-model="form.template_type" placeholder="请选择" :disabled="viewMode" style="width: 100%">
          <el-option label="system" value="system" />
          <el-option label="user" value="user" />
          <el-option label="assistant" value="assistant" />
        </el-select>
      </el-form-item>
      <el-form-item label="测试类型" prop="test_type">
        <el-select v-model="form.test_type" placeholder="请选择" :disabled="viewMode" style="width: 100%">
          <el-option label="API" value="API" />
          <el-option label="Web" value="Web" />
          <el-option label="App" value="App" />
          <el-option label="通用" value="通用" />
        </el-select>
      </el-form-item>
      <el-form-item label="模板内容" prop="content">
        <el-input v-model="form.content" type="textarea" :rows="10" placeholder="请输入模板内容，支持变量如{case_count}" :disabled="viewMode" />
      </el-form-item>
      <el-form-item label="变量说明">
        <el-input v-model="form.variables" placeholder='如:["case_count", "test_type"]' :disabled="viewMode" />
      </el-form-item>
      <el-form-item label="是否激活" prop="is_active">
        <el-switch v-model="form.is_active" :disabled="viewMode" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="handleClose">{{ viewMode ? '关闭' : '取消' }}</el-button>
      <el-button v-if="!viewMode" type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { insertData, updateData } from './prompttemplate'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  formData: {
    type: Object,
    default: () => ({})
  },
  viewMode: {
    type: Boolean,
    default: false
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
const dialogTitle = computed(() => {
  if (props.viewMode) return '查看模板'
  return isEdit.value ? '编辑模板' : '新增模板'
})

// 表单数据
const form = reactive({
  id: null,
  name: '',
  template_type: 'user',
  test_type: 'API',
  content: '',
  variables: '',
  is_active: true
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  template_type: [{ required: true, message: '请选择模板类型', trigger: 'change' }],
  test_type: [{ required: true, message: '请选择测试类型', trigger: 'change' }],
  content: [{ required: true, message: '请输入模板内容', trigger: 'blur' }]
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    template_type: 'user',
    test_type: 'API',
    content: '',
    variables: '',
    is_active: true
  })
  formRef.value?.clearValidate()
}

// 监听formData变化，更新表单数据
watch(() => props.formData, (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    Object.assign(form, newData)
  } else {
    resetForm()
  }
}, { immediate: true, deep: true })

// 提交表单
const handleSubmit = async () => {
  if (props.viewMode) {
    handleClose()
    return
  }
  
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

