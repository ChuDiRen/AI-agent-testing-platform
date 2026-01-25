<template>
  <div>
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
      <el-form-item label="系统名称" prop="system_name">
        <el-input v-model="ruleForm.system_name" />
      </el-form-item>
      <el-form-item label="系统描述" prop="system_description">
        <el-input v-model="ruleForm.system_description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item label="版本号" prop="version">
        <el-input v-model="ruleForm.version" />
      </el-form-item>
      <el-form-item label="维护模式">
        <el-switch v-model="ruleForm.maintenance_mode" />
      </el-form-item>
      <el-form-item label="允许注册">
        <el-switch v-model="ruleForm.allow_registration" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)">保存设置</el-button>
        <el-button @click="resetForm(ruleFormRef)">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { querySettings, updateSettings } from '@/api/settingsApi'
import { Message } from '@/utils/message'
import Breadcrumb from "../../Breadcrumb.vue"

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const ruleForm = reactive({
  system_name: '',
  system_description: '',
  version: '',
  maintenance_mode: false,
  allow_registration: true
})

const rules = reactive({
  system_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '必填项', trigger: 'blur' }
  ]
})

const loadSettings = async () => {
  const res = await querySettings()
  ruleForm.system_name = res.data.data.system_name || ''
  ruleForm.system_description = res.data.data.system_description || ''
  ruleForm.version = res.data.data.version || ''
  ruleForm.maintenance_mode = res.data.data.maintenance_mode || false
  ruleForm.allow_registration = res.data.data.allow_registration !== false
}

const submitForm = async (form) => {
  if (!form) return
  await form.validate((valid, fields) => {
    if (!valid) return
    
    updateSettings(ruleForm).then((res) => {
      if (res.data.code == 200) {
        Message.success('设置保存成功')
      }
    })
  })
}

const resetForm = (form) => {
  if (!form) return
  loadSettings()
}

// ========== 初始化 ==========
onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
  margin-top: 10px;
}

.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}
</style>
