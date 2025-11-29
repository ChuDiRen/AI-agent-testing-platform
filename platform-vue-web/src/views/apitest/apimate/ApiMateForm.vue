<template>
  <BaseForm 
    title="上传素材"
    :model="apiMate"
    :rules="rules"
    :loading="loading"
    @submit="handleSubmit"
    @cancel="handleCancel"
  >
    <el-form-item label="所属项目" prop="project_id">
      <el-select v-model="apiMate.project_id" placeholder="选择所属项目" filterable clearable>
        <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
      </el-select>
    </el-form-item>
    <el-form-item label="文件名" prop="mate_name">
      <el-input v-model="apiMate.mate_name" placeholder="输入文件名" clearable />
    </el-form-item>
    <el-form-item label="素材选择">
      <el-button type="primary" @click="onSelectMaterial">选择素材</el-button>
      <span v-if="apiMate.material_file" style="margin-left: 10px; color: #67c23a;">
        已选择: {{ apiMate.material_file.name }}
      </span>
    </el-form-item>
  </BaseForm>
</template>

<script lang="ts" setup>
import { reactive, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { insertData, queryById } from "./apiMate.js";
import { queryAllProject } from "../project/apiProject.js";
import BaseForm from '@/components/BaseForm/index.vue';

const router = useRouter();

// 加载状态
const loading = ref(false);

// 表单数据
const apiMate = reactive({
  id: 0,
  project_id: null as number | null,
  mate_name: "",
  material_file: null as File | null,
});

// 表单验证规则
const rules = reactive({
  project_id: [
    { required: true, message: '请选择所属项目', trigger: 'change' }
  ],
  mate_name: [
    { required: true, message: '请输入文件名', trigger: 'blur' }
  ],
});

// 项目列表
const projectList = ref<Array<{id: number, project_name: string}>>([]);

// 加载项目列表
const getProjectList = async () => {
  try {
    const res = await queryAllProject();
    if (res.data.code === 200) {
      projectList.value = res.data.data || [];
    }
  } catch (error) {
    console.error('加载项目列表失败:', error);
  }
};

// 提交表单
const handleSubmit = async () => {
  if (!apiMate.material_file) {
    ElMessage.warning('请选择素材文件！');
    return;
  }

  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('project_id', String(apiMate.project_id));
    formData.append('mate_name', apiMate.mate_name);
    formData.append('file', apiMate.material_file);

    const res = await insertData(formData);
    if (res.data.code === 200) {
      ElMessage.success('素材上传成功');
      router.push("/ApiMateManageList");
    } else {
      ElMessage.error(res.data.msg || '素材上传失败');
    }
  } catch (error: any) {
    console.error('素材上传失败:', error);
    ElMessage.error('素材上传失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 取消
const handleCancel = () => {
  router.push("/ApiMateManageList");
};

// 加载表单数据
const loadData = async (id: number) => {
  try {
    const res = await queryById(id);
    if (res.data.code === 200) {
      apiMate.id = res.data.data.id;
      apiMate.project_id = res.data.data.project_id;
      apiMate.mate_name = res.data.data.mate_name;
    }
  } catch (error) {
    console.error('加载数据失败:', error);
  }
};

// 素材选择
const onSelectMaterial = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.onchange = (event) => {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      apiMate.material_file = file;
      if (!apiMate.mate_name) {
        apiMate.mate_name = file.name;
      }
      ElMessage.success('素材已选择，点击保存后上传');
    }
  };
  input.click();
};

onMounted(() => {
  getProjectList();
  const query_id = router.currentRoute.value.query.id;
  apiMate.id = query_id ? Number(query_id) : 0;
  if (apiMate.id > 0) {
    loadData(apiMate.id);
  }
});
</script>

<style scoped>
@import '~/styles/common-form.css';
</style>
