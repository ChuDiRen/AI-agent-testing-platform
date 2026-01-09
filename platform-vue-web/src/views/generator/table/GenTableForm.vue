<template>
  <BaseForm
    ref="baseFormRef"
    :title="isViewMode ? '表配置详情' : (ruleForm.id ? '编辑表配置' : '新增表配置')"
    :model="ruleForm"
    :rules="rules"
    label-width="120px"
    :loading="loading"
    @submit="onBaseFormSubmit"
    @cancel="closeForm"
  >
    <!-- 表单字段 -->
    <el-form-item label="编号" prop="id">
      <el-input v-model="ruleForm.id" disabled />
    </el-form-item>
    <el-form-item label="表名" prop="table_name">
      <el-input v-model="ruleForm.table_name" :readonly="isViewMode" />
    </el-form-item>
    <el-form-item label="表注释" prop="table_comment">
      <el-input v-model="ruleForm.table_comment" :readonly="isViewMode" />
    </el-form-item>
    <el-form-item label="类名" prop="class_name">
      <el-input v-model="ruleForm.class_name" placeholder="如：User" :readonly="isViewMode" />
    </el-form-item>
    <el-form-item label="模块名" prop="module_name">
      <el-input v-model="ruleForm.module_name" placeholder="如：sysmanage" :readonly="isViewMode" />
    </el-form-item>
    <el-form-item label="业务名" prop="business_name">
      <el-input v-model="ruleForm.business_name" placeholder="如：user" :readonly="isViewMode" />
    </el-form-item>
    <el-form-item label="功能名称" prop="function_name">
      <el-input v-model="ruleForm.function_name" placeholder="如：用户管理" :readonly="isViewMode" />
    </el-form-item>
    <el-form-item label="模板类型" prop="tpl_category">
      <el-select v-model="ruleForm.tpl_category" placeholder="请选择" :disabled="isViewMode">
        <el-option label="单表（增删改查）" value="single" />
        <el-option label="树表（增删改查）" value="tree" />
        <el-option label="主子表（增删改查）" value="main_sub" />
      </el-select>
    </el-form-item>
    <el-form-item label="生成选项" prop="gen_type">
      <el-checkbox-group v-model="genTypeList" :disabled="isViewMode">
        <el-checkbox value="0">zip压缩包</el-checkbox>
        <el-checkbox value="1">自定义路径</el-checkbox>
      </el-checkbox-group>
    </el-form-item>
    <el-form-item label="生成路径" prop="gen_path" v-if="genTypeList.includes('1')">
      <el-input v-model="ruleForm.gen_path" placeholder="如：./output" :readonly="isViewMode" />
    </el-form-item>
    <!-- END 表单字段 -->

    <!-- 底部按钮已被BaseForm接管 -->
  </BaseForm>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from "vue"
import { queryById, updateData } from './gentable'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'
import BaseForm from '~/components/BaseForm/index.vue'

const router = useRouter()

// 判断是否为查看模式
const isViewMode = computed(() => router.currentRoute.value.query.view === 'true')

// BaseForm 引用
const baseFormRef = ref()
const loading = ref(false)

// 生成类型列表（用于checkbox）
const genTypeList = ref(['0'])

// 表单数据
const ruleForm = reactive({
  id: 0,
  table_name: '',
  table_comment: '',
  class_name: '',
  module_name: '',
  business_name: '',
  function_name: '',
  tpl_category: 'single',
  gen_type: '0',
  gen_path: ''
})

// 表单验证规则
const rules = computed(() => {
  if (isViewMode.value) {
    return {}
  }
  return {
    table_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    table_comment: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    class_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    module_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    business_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    function_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    tpl_category: [
      { required: true, message: '必填项', trigger: 'change' }
    ],
    gen_path: [
      { required: true, message: '必填项', trigger: 'blur' }
    ]
  }
})

// 提交表单 (BaseForm 已验证通过)
const onBaseFormSubmit = async () => {
  loading.value = true
  try {
    // 转换 genTypeList 为 gen_type
    ruleForm.gen_type = genTypeList.value.join(',')
    ruleForm.gen_path = genTypeList.value.includes('1') ? ruleForm.gen_path : ''
    
    const res = await updateData(ruleForm)
    if (res.data.code == 200) {
      ElMessage.success('更新成功')
      router.push('/GenTableList')
    } else {
      ElMessage.error(res.data.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 关闭表单
const closeForm = () => {
  router.push('/GenTableList')
}

// 加载表单数据
const loadData = async (id: number) => {
  const res = await queryById(id)
  if (res.data.code === 200) {
    const table = res.data.data.table
    ruleForm.id = table.id
    ruleForm.table_name = table.table_name || ''
    ruleForm.table_comment = table.table_comment || ''
    ruleForm.class_name = table.class_name || ''
    ruleForm.module_name = table.module_name || ''
    ruleForm.business_name = table.business_name || ''
    ruleForm.function_name = table.function_name || ''
    ruleForm.tpl_category = table.tpl_category || 'single'
    ruleForm.gen_type = table.gen_type || '0'
    ruleForm.gen_path = table.gen_path || ''
    
    // 转换 gen_type 为 genTypeList
    genTypeList.value = ruleForm.gen_type.split(',')
  }
}

// 初始化
let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
  loadData(ruleForm.id)
}
</script>

<style scoped>
</style>
