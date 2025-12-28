<template>
  <!-- 面包屑导航 -->
  <Breadcrumb />
  <div>
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="接口名称：">
        <el-input v-model="searchForm.api_name" placeholder="根据接口名称筛选" />
      </el-form-item>
      <el-form-item label="所属项目：">
        <el-select v-model="searchForm.project_id" placeholder="选择所属项目" @change="projectChange" clearable>
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>

      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增接口</el-button>
        <el-button type="primary" @click="loadSwagger()">swagger导入<el-icon><Upload /></el-icon></el-button>
      </el-row>
    </el-form>
    <!-- END 搜索表单 -->

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
      <!-- 数据列 -->
      <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
        show-overflow-tooltip="true" />
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
            编辑
          </el-button>
          <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- END 数据表格 -->

    <!-- 分页 -->
    <div class="demo-pagination-block">
      <div class="demonstration"></div>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
    <!-- END 分页 -->
  </div>


      <!-- Swagger 导入弹窗 -->
    <el-dialog v-model="swaggerDialogVisible" title="Swagger 导入" width="30%">
      <el-form :model="swaggerForm" label-width="120px">
       <el-form-item label="所属项目">
          <el-select v-model="swaggerForm.project_id" placeholder="选择所属项目" clearable>
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Swagger 版本">
          <el-select v-model="swaggerForm.version" placeholder="请选择 Swagger 版本">
            <el-option label="Swagger 2.0" value="v2" />
            <el-option label="Swagger 3.0" value="v3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Swagger 地址">
          <el-input v-model="swaggerForm.host" placeholder="请输入 Swagger地址" />
        </el-form-item>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="swaggerDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmSwaggerImport">确认导入</el-button>
        </span>
      </template>
    </el-dialog>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue";
import { queryByPage, deleteData } from './ApiInfo.js' // 不同页面不同的接口
import { useRouter } from "vue-router";
import Breadcrumb from "../../Breadcrumb.vue";
const router = useRouter()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索功能 - 筛选表单
const searchStatus = ref(false) // 是否应用搜索表单
const searchForm = reactive({ "api_name": "","project_id":"","module_id":"" })


// 表格列 - 不同页面不同的列
const columnList = ref([
    { prop: "id", label: '接口用例编号' },
    { prop: "api_name", label: '接口名称' },
    { prop: "request_method", label: '请求方法' },
    { prop: "request_url", label: '请求地址' }
    // ... 其他列 ...
])


// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    queryByPage(searchData).then((res: { data: { data: never[]; total: number; msg: string } }) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}
loadData()

// 变更 页大小
const handleSizeChange = (val: number) => {
    console.log("页大小变化:" + val)
    pageSize.value = val
    loadData()
}

// 变更 页码
const handleCurrentChange = (val: number) => {
    console.log("页码变化:" + val)
    currentPage.value = val
    loadData()
}

// 打开表单（编辑/新增）
const onDataForm = (index: number) => {
    let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index]["id"]
    };
  }
    router.push({
        path: 'ApiInfoForm', // 不同页面不同的表单路径
        query: params_data
    });
}

// 删除数据
const onDelete = (index: number) => {
    deleteData(tableData.value[index]["id"]).then((res: {}) => {
        loadData()
    })
}

// 其他功能拓展
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


//------------------------------------------拓展功能-swagger导入----------------------------------------------------------------------------
// Swagger 导入弹窗相关
const swaggerDialogVisible = ref(false);
const swaggerForm = reactive({
  version: "",
  host: "",
  // port: "",
  project_id: "",
  // module_id: "",
});

const loadSwagger = () => {
  swaggerDialogVisible.value = true;
};

import { doImportSwagger } from './ApiInfo.js';
const confirmSwaggerImport = () => {
  // 这里可以添加发送请求到后台的逻辑
  console.log("Swagger 导入信息:", swaggerForm);
  //  发送请求到后台
  doImportSwagger(swaggerForm).then((res: { data: { msg: string } }) => {
    console.log(res.data.msg);
    loadData();
  });
  
  swaggerDialogVisible.value = false;
};

</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}

</style>