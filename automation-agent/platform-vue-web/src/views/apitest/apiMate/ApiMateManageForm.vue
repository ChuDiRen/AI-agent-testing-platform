<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="apiMate" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>   
      <el-form-item label="所属项目ID">
        <el-select v-model="apiMate.project_id" placeholder="选择所属项目" @change="projectChange" filterable clearable>
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="文件名">
        <el-input v-model="apiMate.mate_name" placeholder="输入文件名" clearable />
      </el-form-item>
      <el-form-item label="素材选择">
        <el-button type="primary" @click="onSelectMaterial">选择素材</el-button>
        <!-- 扩展：预览上传图片容器 -->
         <div v-if="apiMate.material_file">
          <p>已选择素材: {{ apiMate.material_file.name }}</p>
        </div>
      </el-form-item>

      <el-form-item class="form-buttons">
        <el-button type="primary" @click="onSubmit()">确定</el-button>
         <el-button @click="onCancel">关闭</el-button>
      </el-form-item>
  </el-form>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus"; // 弹窗
import { updateData,  insertData,  deleteData,queryById } from "./ApiMateManage.js"; // 不同页面不同的接口
import Breadcrumb from "../../Breadcrumb.vue";
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
const rules = reactive({
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

// 项目选择变化处理
const projectChange = (value) => {
  console.log('项目选择变化:', value);
};

// 提交表单
const onSubmit = () => {
  //   1. 获取表单数据
  //   2. 验证表单数据有对应的素材
  //   3. 提交表单数据
  if(apiMate.project_id == "选择所属项目")
  {
    ElMessage.warning('请选择所属项目！');
    return;
  }

  //   1. 获取表单数据
  if (apiMate.material_file) {
    const formData = new FormData();
    // 单独追加每个字段到 formData
    formData.append('project_id', apiMate.project_id);
    formData.append('mate_name', apiMate.mate_name);
    formData.append('file', apiMate.material_file);

    console.log("=========当前获取的数据提交数据：formData===========")
    console.log("formData:",formData)
    console.log("=========END 当前获取的数据提交数据：formData===========")


    // 2.调用insertData方法提交表单数据，并且设置请求头
    insertData(formData).then((res) => {
      if (res.data.code === 200) {
        ElMessage.success('素材上传成功');
        router.push("/ApiMateManageList"); // 跳转回列表页面 - 不同的页面，不同的路径
      } else {
        ElMessage.error('素材上传失败：' + res.data.msg);
      }
    }).catch((error) => {
      ElMessage.error('素材上传失败：' + error.message);
    });
  }
  else {
      // 没有素材上传，提示用户
      ElMessage.warning('请选择素材文件！');
  }
};


// 关闭按钮方法
const onCancel = () => {
  router.push("/ApiMateManageList");
};

// 加载表单数据
const loadData = async (id) => {
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


// ===============扩展：素材选择=================

// 素材选择按钮点击事件
const onSelectMaterial = () => {
  // 创建一个隐藏的input元素用于文件选择
  const input = document.createElement('input');
  input.type = 'file';
  input.onchange = (event) => {
    const file = event.target.files?.[0];
    if (file) {
      // 缓存选择的素材文件
      apiMate.material_file = file;

      // 如果文件名文本框为空，则自动填入文件名
      if (!apiMate.mate_name) {
        apiMate.mate_name = file.name;
      }

      ElMessage.success('素材已选择，点击确定后上传');
    }
  };
  input.click();
};

// ===============END 扩展：素材选择=================
</script>
