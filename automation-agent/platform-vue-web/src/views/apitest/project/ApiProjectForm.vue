<template>
  <div>
    <!-- 面包屑导航 -->
     <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
      <el-form-item label="项目编号" prop="id">
        <el-input v-model="ruleForm.id" disabled />
      </el-form-item>
      <el-form-item label="项目名称" prop="project_name"  >
        <el-input v-model="ruleForm.project_name" placeholder="请输入项目名称"/>
      </el-form-item>
      <el-form-item label="项目描述" prop="project_desc" >
        <el-input v-model="ruleForm.project_desc" placeholder="请输入项目描述" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
        <el-button @click="resetForm(ruleFormRef)">清空</el-button>
        <el-button @click="closeForm()">关闭</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
  
  <script setup>
  import { ref, reactive } from "vue";
  import { useRouter } from "vue-router";
  import Breadcrumb from "../../Breadcrumb.vue";
  
  // 不同页面不同的接口
  import { queryById, insertData, updateData } from './ApiProject.js'; 
  
  const router = useRouter();
  
  // 1. 表单实例
  const ruleFormRef = ref();
  
  // 2. 表单数据
  const ruleForm = reactive({
    id: 0,
    project_name: '',
    project_desc: ''
  });
  
  // 3. 表单验证规则
  const rules = reactive({
    project_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    project_desc: [
      { required: true, message: '必填项', trigger: 'blur' }
    ]
  });
  
  // 4. 提交表单
  const submitForm = async (form) => {
    if (!form) return;
    await form.validate((valid, fields) => {
      if (!valid) {
        return;
      }
      // 有ID代表是修改，没有ID代表是新增
      if (ruleForm.id > 0) {
        updateData(ruleForm).then((res) => {
          if (res.data.code == 200) {
            router.push('/ApiProjectList'); // 跳转回列表页面
          }
        });
      } else {
        insertData(ruleForm).then((res) => {
          console.log(res)
          if (res.data.code == 200) {
            router.push('/ApiProjectList'); // 跳转回列表页面
          }
        });
      }
    });
  };
  
  // 5. 重置表单
  const resetForm = (form) => {
    if (!form) return;
    form.resetFields();
  };
  
  // 6. 关闭表单 - 回到数据列表页
  const closeForm = () => {
    router.back();
  };
  
  // 7. 加载表单数据
  const loadData = async (id) => {
    const res = await queryById(id);
    ruleForm.id = res.data.data.id;
    ruleForm.project_name = res.data.data.project_name;
    ruleForm.project_desc = res.data.data.project_desc;
  };
  
  // 8. 如果有id参数，说明是编辑，需要获取数据
  let query_id = router.currentRoute.value.query.id;
  ruleForm.id = query_id ? Number(query_id) : 0;

  if (ruleForm.id > 0) {
    loadData(ruleForm.id);
  }
  
  </script>