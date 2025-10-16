<template>
  <div class="api-info-form-container">
    <h2>{{ isEdit ? '编辑接口信息' : '新增接口信息' }}</h2>
    
    <el-form ref="formRef" :model="ruleForm" :rules="rules" label-width="120px" style="max-width: 800px">
      <el-form-item label="所属项目" prop="project_id">
        <el-select v-model="ruleForm.project_id" placeholder="选择项目" style="width: 100%">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>     
        </el-select>
      </el-form-item>
      
      <el-form-item label="接口名称" prop="api_name">
        <el-input v-model="ruleForm.api_name" placeholder="请输入接口名称" />
      </el-form-item>
      
      <el-form-item label="请求方法" prop="request_method">
        <el-select v-model="ruleForm.request_method" placeholder="选择请求方法" style="width: 200px">
          <el-option v-for="method in methodList" :key="method" :label="method" :value="method"/>     
        </el-select>
      </el-form-item>
      
      <el-form-item label="请求地址" prop="request_url">
        <el-input v-model="ruleForm.request_url" placeholder="请输入请求地址，如：/api/user/login" />
      </el-form-item>
      
      <el-form-item label="URL参数">
        <el-input 
          v-model="ruleForm.request_params" 
          type="textarea" 
          :rows="3" 
          placeholder="JSON格式，如：{&quot;page&quot;: 1, &quot;size&quot;: 10}"
        />
      </el-form-item>
      
      <el-form-item label="请求头">
        <el-input 
          v-model="ruleForm.request_headers" 
          type="textarea" 
          :rows="3" 
          placeholder="JSON格式，如：{&quot;Content-Type&quot;: &quot;application/json&quot;}"
        />
      </el-form-item>
      
      <el-form-item label="调试变量">
        <el-input 
          v-model="ruleForm.debug_vars" 
          type="textarea" 
          :rows="3" 
          placeholder="JSON格式，如：{&quot;username&quot;: &quot;admin&quot;, &quot;password&quot;: &quot;123456&quot;}"
        />
      </el-form-item>
      
      <el-form-item label="Form Data">
        <el-input 
          v-model="ruleForm.request_form_datas" 
          type="textarea" 
          :rows="3" 
          placeholder="JSON格式，如：{&quot;username&quot;: &quot;admin&quot;, &quot;password&quot;: &quot;123456&quot;}"
        />
      </el-form-item>
      
      <el-form-item label="URL编码数据">
        <el-input 
          v-model="ruleForm.request_www_form_datas" 
          type="textarea" 
          :rows="3" 
          placeholder="JSON格式，如：{&quot;username&quot;: &quot;admin&quot;, &quot;password&quot;: &quot;123456&quot;}"
        />
      </el-form-item>
      
      <el-form-item label="JSON数据">
        <el-input 
          v-model="ruleForm.requests_json_data" 
          type="textarea" 
          :rows="4" 
          placeholder="JSON格式，如：{&quot;username&quot;: &quot;admin&quot;, &quot;password&quot;: &quot;123456&quot;}"
        />
      </el-form-item>
      
      <el-form-item label="文件上传">
        <el-input 
          v-model="ruleForm.request_files" 
          type="textarea" 
          :rows="2" 
          placeholder="文件字段配置，JSON格式"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="submitForm">{{ isEdit ? '更新' : '创建' }}</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button @click="goBack">返回</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { queryById, insertData, updateData, getMethods } from './apiinfo.js';
import { queryByPage as getProjectList } from '../project/apiProject.js';
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();

// 表单引用
const formRef = ref();

// 是否编辑模式
const isEdit = ref(false);

// 项目列表
const projectList = ref([]);

// 请求方法列表
const methodList = ref([]);

// 表单数据
const ruleForm = reactive({
  id: null,
  project_id: null,
  api_name: '',
  request_method: 'GET',
  request_url: '',
  request_params: '',
  request_headers: '',
  debug_vars: '',
  request_form_datas: '',
  request_www_form_datas: '',
  requests_json_data: '',
  request_files: ''
});

// 表单验证规则
const rules = reactive({
  api_name: [
    { required: true, message: '请输入接口名称', trigger: 'blur' }
  ],
  request_method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  request_url: [
    { required: true, message: '请输入请求地址', trigger: 'blur' }
  ]
});

// 加载项目列表
const loadProjectList = () => {
  getProjectList({ page: 1, pageSize: 1000 }).then((res) => {
    if (res.data.code === 200) {
      projectList.value = res.data.data;
    }
  }).catch((error) => {
    console.error('加载项目列表失败:', error);
  });
};

// 加载请求方法列表
const loadMethodList = () => {
  getMethods().then((res) => {
    if (res.data.code === 200) {
      methodList.value = res.data.data;
    }
  }).catch((error) => {
    console.error('加载请求方法失败:', error);
  });
};

// 加载数据（编辑模式）
const loadData = (id) => {
  queryById(id).then((res) => {
    if (res.data.code === 200 && res.data.data) {
      const data = res.data.data;
      Object.keys(ruleForm).forEach(key => {
        if (data.hasOwnProperty(key)) {
          ruleForm[key] = data[key];
        }
      });
    } else {
      ElMessage.error('数据加载失败');
      goBack();
    }
  }).catch((error) => {
    console.error('数据加载失败:', error);
    ElMessage.error('数据加载失败，请稍后重试');
    goBack();
  });
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  await formRef.value.validate((valid, fields) => {
    if (valid) {
      const submitData = { ...ruleForm };
      
      if (isEdit.value) {
        // 更新
        updateData(submitData).then((res) => {
          if (res.data.code === 200) {
            ElMessage.success('更新成功');
            goBack();
          } else {
            ElMessage.error(res.data.msg || '更新失败');
          }
        }).catch((error) => {
          console.error('更新失败:', error);
          ElMessage.error('更新失败，请稍后重试');
        });
      } else {
        // 新增
        delete submitData.id; // 新增时不需要id
        insertData(submitData).then((res) => {
          if (res.data.code === 200) {
            ElMessage.success('创建成功');
            goBack();
          } else {
            ElMessage.error(res.data.msg || '创建失败');
          }
        }).catch((error) => {
          console.error('创建失败:', error);
          ElMessage.error('创建失败，请稍后重试');
        });
      }
    } else {
      console.log('表单验证失败!', fields);
    }
  });
};

// 重置表单
const resetForm = () => {
  if (!formRef.value) return;
  formRef.value.resetFields();
};

// 返回列表页
const goBack = () => {
  router.push('/ApiInfoList');
};

// 页面加载时执行
onMounted(() => {
  loadProjectList();
  loadMethodList();
  
  // 检查是否为编辑模式
  const id = route.query.id;
  if (id) {
    isEdit.value = true;
    loadData(parseInt(id));
  }
});
</script>

<style scoped>
.api-info-form-container {
  padding: 20px;
}
</style>
