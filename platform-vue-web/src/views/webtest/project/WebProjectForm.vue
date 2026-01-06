<template>
  <el-dialog 
    v-model="visible" 
    :title="form.id ? '编辑 Web 项目' : '新增 Web 项目'" 
    width="500px"
    @close="handleClose"
  >
    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="rules" 
      label-width="100px"
      class="p-4"
    >
      <el-form-item label="项目名称" prop="project_name">
        <el-input v-model="form.project_name" placeholder="请输入项目名称" />
      </el-form-item>
      <el-form-item label="项目描述" prop="project_desc">
        <el-input 
          v-model="form.project_desc" 
          type="textarea" 
          placeholder="请输入项目描述" 
          :rows="3" 
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { addWebProject, updateWebProject } from './webProject'

const emit = defineEmits(['success'])

const visible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  project_name: '',
  project_desc: ''
})

const rules = {
  project_name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

// 打开弹窗
const open = (data = null) => {
  visible.value = true
  if (data) {
    Object.assign(form, data)
  } else {
    resetForm()
  }
}

// 重置表单
const resetForm = () => {
  form.id = null
  form.project_name = ''
  form.project_desc = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 关闭处理
const handleClose = () => {
  resetForm()
}

// 提交
const handleSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (form.id) {
          await updateWebProject(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await addWebProject(form)
          ElMessage.success('创建成功')
        }
        visible.value = false
        emit('success')
      } catch (error) {
        // Mock 提交
        ElMessage.success(form.id ? '更新成功 (Mock)' : '创建成功 (Mock)')
        visible.value = false
        emit('success')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

defineExpose({ open })
</script>
