<template>
  <el-form ref="ruleFormRef" :model="apiMate.project_id" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>   
      <el-form-item label="所属项目ID">
        <el-select v-model="apiMate.project_id" placeholder="选择所属项目" @change="projectChange" filterable clearable>
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="文件名">
        <el-input v-model="apiMate.mate_name" placeholder="输入文件名" clearable />
      </el-form-item>
      <el-form-item label="素材选择">
        <el-button type="primary">选择素材</el-button>
        <!-- 扩展：预览上传图片容器 -->
      </el-form-item>

      <el-form-item class="form-buttons">
        <el-button type="primary" @click="onSubmit()">确定</el-button>
         <el-button @click="onCancel">关闭</el-button>
      </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus"; // 弹窗
import { updateData,  insertData,  deleteData,queryById } from "./ApiMateManage.js"; // 不同页面不同的接口
import axios from 'axios';

// 获取当前路由的实例
const router = useRouter();

// 表单实例
const ruleFormRef = ref();


// 表单数据 - 不同的页面，不同的表单字段
const apiMate = reactive({
  id: 0,
  project_id: "选择所属项目",
  mate_name: "",
  material_file: null, // 新增：用于缓存选择的素材文件
});

// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive<any>({
  project_id: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
    mate_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
});


// 加载对应的所有项目的数据
// 1. 加载项目
import { queryAllProject } from "../project/ApiProject.js"; // 不同页面不同的接口
const projectList = ref([{
  id: 0,
  project_name: '',
  project_desc: ''
}]);
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data;
  });
}
getProjectList();

console.log("======================")
console.log(projectList.value)
console.log("======================")



// 提交表单
const onSubmit = () => {
//   1. 获取表单数据
//   2. 验证表单数据有对应的素材
//   3. 提交表单数据
};


// 关闭按钮方法
const onCancel = () => {
  router.push("/ApiMateManageList");
};

// 加载表单数据
const loadData = async (id: number) => {
  const res = await queryById(id);
  // 不同的页面，不同的表单字段 (注意这里的res.data.data.xxx，xxx是接口返回的字段，不同的接口，字段不同)
  apiMate.id = res.data.data.id;
  apiMate.project_id = res.data.data.project_id;
  apiMate.mate_name = res.data.data.mate_name;
};

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id;
apiMate.id = query_id ? Number(query_id) : 0;
if (apiMate.id > 0) {
  loadData(apiMate.id);
}

</script>
