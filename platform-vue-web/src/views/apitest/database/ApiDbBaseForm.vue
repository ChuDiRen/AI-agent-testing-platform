<template>
  <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
    <el-form-item label="配置名称" prop="name">
      <el-input v-model="form.name" placeholder="请输入配置名称" />
    </el-form-item>

    <el-form-item label="所属项目" prop="project_id">
      <el-select v-model="form.project_id" placeholder="请选择项目" style="width: 100%">
        <el-option v-for="item in projects" :key="item.id" :label="item.project_name" :value="item.id" />
      </el-select>
    </el-form-item>

    <el-form-item label="数据库类型" prop="db_type">
      <el-select v-model="form.db_type" placeholder="请选择数据库类型" style="width: 100%">
        <el-option label="MySQL" value="mysql" />
        <el-option label="PostgreSQL" value="postgresql" />
        <el-option label="Oracle" value="oracle" />
        <el-option label="SQL Server" value="sqlserver" />
      </el-select>
    </el-form-item>

    <el-form-item label="主机地址" prop="host">
      <el-input v-model="form.host" placeholder="localhost" />
    </el-form-item>

    <el-form-item label="端口" prop="port">
      <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" />
    </el-form-item>

    <el-form-item label="数据库名" prop="database">
      <el-input v-model="form.database" placeholder="请输入数据库名" />
    </el-form-item>

    <el-form-item label="用户名" prop="username">
      <el-input v-model="form.username" placeholder="请输入用户名" />
    </el-form-item>

    <el-form-item label="密码" prop="password">
      <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
      <el-button @click="emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from '@/axios'

const props = defineProps({
  id: Number
})

const emit = defineEmits(['success', 'cancel'])

const formRef = ref(null)
const projects = ref([])
const form = ref({
  name: '',
  project_id: null,
  db_type: 'mysql',
  host: 'localhost',
  port: 3306,
  database: '',
  username: '',
  password: '',
  db_info: '{}'
})

const rules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  project_id: [{ required: true, message: '请选择项目', trigger: 'change' }],
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }]
}

const loadProjects = async () => {
  try {
    const { data } = await axios.get('/ApiProject/queryAll')
    if (data.code === 200) {
      projects.value = data.data.list
    }
  } catch (error) {
    console.error('加载项目失败:', error)
  }
}

const loadDetail = async () => {
  if (!props.id) return
  
  try {
    const { data } = await axios.get(`/ApiDbBase/queryById?id=${props.id}`)
    if (data.code === 200) {
      Object.assign(form.value, data.data)
    }
  } catch (error) {
    ElMessage.error('加载失败: ' + error.message)
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  
  try {
    const url = props.id ? '/ApiDbBase/update' : '/ApiDbBase/insert'
    const method = props.id ? 'put' : 'post'
    
    const { data } = await axios[method](url, form.value)
    if (data.code === 200) {
      ElMessage.success('保存成功')
      emit('success')
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error.message)
  }
}

watch(() => props.id, () => {
  if (props.id) {
    loadDetail()
  }
}, { immediate: true })

onMounted(() => {
  loadProjects()
})
</script>
