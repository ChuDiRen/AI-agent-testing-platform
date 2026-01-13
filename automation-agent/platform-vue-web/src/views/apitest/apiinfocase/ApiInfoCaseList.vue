<template>
  <!-- 面包屑导航 -->
  <Breadcrumb />
  <div>
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="API用例名称：">
        <el-input v-model="searchForm.case_name" placeholder="根据API用例名称筛选"  clearable/>
      </el-form-item>
      <el-form-item label="所属项目：">
        <el-select
          v-model="searchForm.project_id" placeholder="选择所属项目" clearable  >
          <el-option  v-for="project in projectList" :key="project.id"  :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>
      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增用例</el-button>

        <!-- 扩展功能：导入测试用例 -->
        <el-dropdown @command="handleImportCommand" trigger="hover">
        <el-button type="primary" style="margin-left: 15px;">
          导入用例<el-icon><ArrowDown /></el-icon>
        </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="onDownloadFile()">下载模板</el-dropdown-item>
              <el-dropdown-item  @click="handleFileUploadClick">文件导入</el-dropdown-item>
            </el-dropdown-menu>
          </template>
         </el-dropdown>
         
      </el-row>

        <!-- 隐藏的文件输入 -->
       <input
        ref="fileInputRef"
        type="file"
        accept=".xmind"
        style="display: none"
        @change="uploadFile"
      />
      
    </el-form>
    <!-- END 搜索表单 -->

  


    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%" max-height="500">
      <!-- 数据列 -->
      <el-table-column
        v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" :show-overflow-tooltip="true">
      </el-table-column>
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作">
        <template #default="scope">
          <el-button
            link
            type="primary"
            size="small"
            @click.prevent="onDataForm(scope.$index)"
          >
            编辑
          </el-button>
          <el-button
            link
            type="primary"
            size="small"
            @click.prevent="onDelete(scope.$index)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- END 数据表格 -->

    <!-- 分页 -->
    <div class="demo-pagination-block">
      <div class="demonstration"></div>
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    <!-- END 分页 -->


        <!-- 文件上传弹窗 -->
    <el-dialog v-model="uploadDialogVisible" title="选择所属项目" width="30%">
      <el-select v-model="selectedProjectId" placeholder="请选择所属项目">
        <el-option
          v-for="project in projectList"
          :key="project.id"
          :label="project.project_name"
          :value="project.id"
        />
      </el-select>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="uploadDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmUpload">确认上传</el-button>
        </span>
      </template>
    </el-dialog>
     <!-- END 文件上传弹窗 -->

  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue";
import { queryByPage, deleteData } from "./ApiInfoCase.js"; // 不同页面不同的接口
import { useRouter } from "vue-router";
import Breadcrumb from "../../Breadcrumb.vue";

const router = useRouter();

// 分页参数
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 搜索功能 - 筛选表单
const searchForm = reactive({ case_name: "", project_id: "", module_id: "" });

// 表格列 - 不同页面不同的列
const columnList = ref([
  { prop: "id", label: "用例编号" },
  { prop: "case_name", label: "用例名称" },
  { prop: "case_desc", label: "用例描述" },
  // { prop: "is_pre", label: "是否前置" },
  // ... 其他列 ...
]);

// 表格数据
const tableData = ref([]);

// 加载页面数据
const loadData = () => {
  let searchData = searchForm;
  searchData["page"] = currentPage.value;
  searchData["pageSize"] = pageSize.value;

  queryByPage(searchData).then(
    (res: { data: { data: never[]; total: number; msg: string } }) => {
      console.log(res.data.data);
      tableData.value = res.data.data;
      total.value = res.data.total;
    }
  );
};

loadData();

// 变更 页大小
const handleSizeChange = (val: number) => {
  console.log("页大小变化:" + val);
  pageSize.value = val;
  loadData();
};

// 变更 页码
const handleCurrentChange = (val: number) => {
  console.log("页码变化:" + val);
  currentPage.value = val;
  loadData();
};

// 打开表单（编辑/新增）
const onDataForm = (index: number) => {
  let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index]["id"],
    };
  }
  router.push({
    path: "./ApiInfoCaseForm", // 不同页面不同的表单路径
    query: params_data,
  });
};

// 删除数据
const onDelete = (index: number) => {
  let searchData = searchForm;
  searchData["page"] = currentPage.value;
  searchData["pageSize"] = pageSize.value;
  deleteData(tableData.value[index]["id"]).then((res: {}) => {
  loadData();
  });
};

// 其他功能拓展
import { queryAllProject } from "../project/ApiProject.js"; // 不同页面不同的接口
const projectList = ref([
  {
    id: 0,
    project_name: "",
    project_desc: "",
  },
]);
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data;
  });
}
getProjectList();


//------------------------------------拓展功能6- 添加文件上传函数----------------------------------------------
const fileInputRef = ref(); // 绑定隐藏的 input[type='file']
let fileToUpload = null; // 存储待上传的文件
const uploadDialogVisible = ref(false); // 控制上传弹窗的显示

// 点击“文件上传”按钮时触发文件选择
const handleFileUploadClick = () => {
// 打开文件选择的窗口--点击确定会调用uploadFile方法
  fileInputRef.value.click();
};


// 处理文件选择并打开弹窗
const uploadFile = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  // 校验文件类型是否为 xmind
  const isValidType = file.name.toLowerCase().endsWith(".xmind");
  if (!isValidType) {
    alert("只能上传 .xmind 格式的文件！");
    event.target.value = null; // 清空文件选择
    return;
  }

  fileToUpload = file; // 存储待上传的文件
  uploadDialogVisible.value = true; // 打开弹窗-选择需要导入的项目
};


// 确认上传
const selectedProjectId = ref(null); // 选中的项目ID
// 导入我们的函数
import { uploadXmindFile } from './ApiInfoCase.js'
const confirmUpload = () => {
  if (!selectedProjectId.value) {
    alert("请选择所属项目！");
    return;
  }

  // 使用 FormData 封装文件数据和项目ID
  const formData = new FormData();
  formData.append("file", fileToUpload);
  formData.append("project_id", selectedProjectId.value);

  // 调用上传接口
  uploadXmindFile(formData)
    .then((res) => {
      alert("上传成功");
      console.log("上传结果：", res);
      loadData(); // 可选：刷新列表
    })
    .catch((err) => {
      alert("上传失败，请重试");
      console.error("上传失败：", err);
    })
    .finally(() => {
      uploadDialogVisible.value = false; // 关闭弹窗
      selectedProjectId.value = null; // 重置选中的项目ID
      fileToUpload = null; // 重置待上传的文件
    });
};



// 下载文件
const onDownloadFile = () => {
   // 假设xminde文件放在assets文件夹怎么前端进行下载
  // 指定文件路径（假设文件在 public 目录下）
  const filePath = '/template.xmind'; // 例如：public/template.xmind

  // 创建一个隐藏的 <a> 标签
  const link = document.createElement('a');
  link.href = filePath;
  link.download = 'template.xmind'; // 设置下载文件名
  document.body.appendChild(link);
  link.click(); // 触发点击
  document.body.removeChild(link); // 移除标签
};
</script>

<style scoped>
.demo-pagination-block + .demo-pagination-block {
  margin-top: 10px;
}

.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}

/* 更改 el-select 的宽度 */  
.el-select {  
  width: 200px; /* 设置你想要的宽度 */  
}  
</style>