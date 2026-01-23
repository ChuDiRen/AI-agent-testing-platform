<template>
  <div class="document-upload">
    <el-upload
      :action="uploadUrl"
      :headers="uploadHeaders"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :on-progress="handleProgress"
      :data="uploadData"
      :file-list="fileList"
      :auto-upload="false"
      ref="uploadRef"
    >
      <template #trigger>
        <el-button type="primary">
          <el-icon><Upload /></el-icon>
          选择文件
        </el-button>
      </template>
      
      <el-button
        class="ml-3"
        type="success"
        @click="submitUpload"
        :disabled="!canUpload"
      >
        开始上传
      </el-button>
      
      <template #tip>
        <div class="el-upload__tip">
          支持 PDF、DOC、DOCX、TXT、MD 格式，文件大小不超过 50MB
        </div>
      </template>
    </el-upload>

    <!-- 文档信息表单 -->
    <el-form
      v-if="showForm"
      :model="docForm"
      :rules="formRules"
      ref="formRef"
      label-width="100px"
      class="doc-form"
    >
      <el-form-item label="文档标题" prop="title">
        <el-input v-model="docForm.title" placeholder="请输入文档标题" />
      </el-form-item>
      
      <el-form-item label="文档描述" prop="description">
        <el-input
          v-model="docForm.description"
          type="textarea"
          :rows="3"
          placeholder="请输入文档描述"
        />
      </el-form-item>
      
      <el-form-item label="权限设置" prop="permission">
        <el-radio-group v-model="docForm.permission">
          <el-radio label="private">私有</el-radio>
          <el-radio label="public">公开</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item label="标签" prop="tags">
        <el-select
          v-model="docForm.tags"
          multiple
          filterable
          allow-create
          placeholder="添加标签"
        >
          <el-option
            v-for="tag in commonTags"
            :key="tag"
            :label="tag"
            :value="tag"
          />
        </el-select>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/auth'
import { uploadDocument } from '../api/document'

const emit = defineEmits(['success', 'error'])

const authStore = useAuthStore()
const uploadRef = ref()
const formRef = ref()

const fileList = ref([])
const showForm = ref(false)
const uploading = ref(false)

const docForm = ref({
  title: '',
  description: '',
  permission: 'private',
  tags: []
})

const formRules = {
  title: [
    { required: true, message: '请输入文档标题', trigger: 'blur' }
  ],
  permission: [
    { required: true, message: '请选择权限设置', trigger: 'change' }
  ]
}

const commonTags = [
  '技术文档',
  '产品说明',
  '用户手册',
  'API文档',
  '规章制度',
  '培训资料',
  '会议记录',
  '项目文档'
]

const uploadUrl = computed(() => `${import.meta.env.VITE_API_BASE_URL}/documents/upload`)
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${authStore.token}`
}))

const canUpload = computed(() => {
  return fileList.value.length > 0 && showForm.value
})

const uploadData = computed(() => ({
  title: docForm.value.title,
  description: docForm.value.description,
  permission: docForm.value.permission,
  tags: JSON.stringify(docForm.value.tags)
}))

// 监听文件选择
watch(fileList, (newList) => {
  if (newList.length > 0 && !showForm.value) {
    showForm.value = true
    // 自动填充标题
    const file = newList[0].raw
    if (file && !docForm.value.title) {
      docForm.value.title = file.name.replace(/\.[^/.]+$/, '')
    }
  }
}, { deep: true })

const beforeUpload = (file) => {
  // 检查文件类型
  const allowedTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown'
  ]
  
  const isValidType = allowedTypes.includes(file.type) || 
    file.name.endsWith('.md') || 
    file.name.endsWith('.txt')
  
  if (!isValidType) {
    ElMessage.error('不支持的文件格式！')
    return false
  }
  
  // 检查文件大小
  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过 50MB！')
    return false
  }
  
  return true
}

const submitUpload = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    uploading.value = true
    await uploadRef.value.submit()
  } catch (error) {
    ElMessage.error('请完善文档信息')
  }
}

const handleSuccess = (response, file) => {
  uploading.value = false
  ElMessage.success('文档上传成功')
  
  // 重置表单
  resetForm()
  
  // 通知父组件
  emit('success', response.data)
}

const handleError = (error, file) => {
  uploading.value = false
  ElMessage.error('文档上传失败')
  
  // 通知父组件
  emit('error', error)
}

const handleProgress = (event, file) => {
  // 可以在这里显示上传进度
}

const resetForm = () => {
  fileList.value = []
  showForm.value = false
  docForm.value = {
    title: '',
    description: '',
    permission: 'private',
    tags: []
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 暴露方法给父组件
defineExpose({
  resetForm
})
</script>

<style scoped>
.document-upload {
  max-width: 600px;
}

.doc-form {
  margin-top: 20px;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.ml-3 {
  margin-left: 12px;
}

.el-upload__tip {
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}
</style>
