<template>
  <BaseForm 
    :title="ruleForm.id > 0 ? '编辑项目' : '新增项目'"
    :model="ruleForm"
    :rules="rules"
    :loading="loading"
    @submit="handleSubmit"
    @cancel="handleCancel"
  >
    <el-form-item label="项目编号" prop="id" v-if="ruleForm.id > 0">
      <el-input v-model="ruleForm.id" disabled />
    </el-form-item>
    <el-form-item label="项目名称" prop="project_name">
      <el-input v-model="ruleForm.project_name" placeholder="请输入项目名称" />
    </el-form-item>
    <el-form-item label="项目描述" prop="project_desc">
      <el-input v-model="ruleForm.project_desc" type="textarea" :rows="3" placeholder="请输入项目描述" />
    </el-form-item>
  </BaseForm>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import type { FormRules } from 'element-plus';
import { useRouter } from "vue-router";
import { ElMessage } from 'element-plus';
import { queryById, insertData, updateData } from './apiProject.js';
import BaseForm from '~/components/BaseForm/index.vue';

const router = useRouter();

// 加载状态
const loading = ref(false);

// 表单数据
const ruleForm = reactive({
  id: 0,
  project_name: '',
  project_desc: ''
});

// 表单验证规则
const rules = reactive<FormRules>({
  project_name: [
    { required: true, message: '项目名称为必填项', trigger: 'blur' }
  ],
  project_desc: [
    { required: true, message: '项目描述为必填项', trigger: 'blur' }
  ]
});

// 提交表单
const handleSubmit = async () => {
  loading.value = true;
  try {
    if (ruleForm.id > 0) {
      const res = await updateData(ruleForm);
      if (res.data.code === 200) {
        ElMessage.success('更新成功');
        router.push('/ApiProjectList');
      } else {
        ElMessage.error(res.data.msg || '更新失败');
      }
    } else {
      const res = await insertData(ruleForm);
      if (res.data.code === 200) {
        ElMessage.success('新增成功');
        router.push('/ApiProjectList');
      } else {
        ElMessage.error(res.data.msg || '新增失败');
      }
    }
  } catch (error: any) {
    console.error('操作失败:', error);
    ElMessage.error('操作失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 取消
const handleCancel = () => {
  router.push('/ApiProjectList');
};

// 加载表单数据
const loadData = async (id: number) => {
  try {
    const res = await queryById(id);
    if (res.data.code === 200) {
      Object.assign(ruleForm, res.data.data);
    }
  } catch (error) {
    console.error('加载数据失败:', error);
    ElMessage.error('加载数据失败');
  }
};

onMounted(() => {
  const query_id = router.currentRoute.value.query.id;
  ruleForm.id = query_id ? Number(query_id) : 0;
  if (ruleForm.id > 0) {
    loadData(ruleForm.id);
  }
});
</script>

<style scoped>
@import '~/styles/common-form.css';
</style>