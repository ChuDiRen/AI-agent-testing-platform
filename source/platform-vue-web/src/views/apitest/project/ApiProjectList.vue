<template><h2>项目列表</h2>
  <!-- 搜索表单 -->
  <el-form ref="searchFormRef"  :inline="true" :model="searchForm" class="demo-form-inline">
    <el-row class="mb-4" type="flex" justify="end">
      <el-button type="warning" @click="onDataForm(-1)">新增项目</el-button>
    </el-row>
  </el-form>
  <!-- END搜索表单 -->

  <!-- 数据表格 -->
  <el-table :data="tableData" style="width: 100%" max-height="500">
    <!-- 数据列 -->
    <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" :show-overflow-tooltip="true" />
    <!-- END数据列 -->

    <!-- 操作 -->
    <el-table-column fixed="right" label="操作">
      <template #default="scope">
        <el-button  link  type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
          编辑
        </el-button>
        <el-button  link  type="primary" size="small" @click.prevent="showDbBaseManage(scope.$index)">
      数据库配置
        </el-button>
        <el-button  link  type="primary" size="small" @click.prevent="onDelete(scope.$index)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>
  <!-- END操作 -->
  <!-- END 数据表格 -->

  <!-- 分页 -->
  <div class="demo-pagination-block">
    <div class="demonstration"></div>
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 30, 50]"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
 </div>
  <!-- END 分页 -->

  <!-- 弹窗 - 增加功能：数据库配置 弹窗加载执行记录 -->
  <el-dialog v-model="DbBaseManageDialogFormVisible" style="width: 1100px">
     <el-form-item >
           <!-- 数据库数据信息显示 -->
          <el-table :data="DbBaseManageList" style="width: 100%"  max-height="300">
          <el-table-column prop="name" label="连接名" style="width: 10%" />
          <el-table-column prop="ref_name" label="引用变量" style="width: 20%" :show-overflow-tooltip="true" />
          <el-table-column prop="db_info" label="数据库连接信息" style="width: 40%" :show-overflow-tooltip="true" />
          <el-table-column prop="is_enabled" label="是否启用" style="width: 10%" :show-overflow-tooltip="true" >
            <template #default="scope">
              {{ scope.row.is_enabled === "0"?'否' : scope.row.is_enabled === "1"?'是':'-' }}
            </template>
          </el-table-column>
          <el-table-column prop="db_type" label="数据库类型" style="width: 10%" :show-overflow-tooltip="true" />
         
          <el-table-column label="操作" style="width: 5%" :show-overflow-tooltip="true">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="upDataDbinfo(scope.$index)">修改是否启动</el-button>
                <el-button link type="primary" size="small" @click.prevent="onDeleteDb(scope.$index)">删除</el-button>
            </template>
          </el-table-column>
          </el-table>


           <!-- 数据库添加数据信息 -->
          <div class="input-group" style="width: 100%" >
          <el-input v-model="ruleForm.name" placeholder="连接名" style="width: 15%"/>
          <el-input v-model="ruleForm.ref_name" placeholder="引用变量" style="width: 15%"/>
          <el-input v-model="ruleForm.db_info" placeholder="数据库连接信息，如：{host: 主机IP/服务器, port: 端口号, username: 用户名, password: 密码, database: 数据库名}" style="width: 30%"/>
          <el-select v-model="ruleForm.is_enabled"  placeholder="是否启用"  style="width: 20%">
            <el-option v-for="item in options"  :key="item.value" :label="item.label"  :value="item.value" />
          </el-select>
          <el-select v-model="ruleForm.db_type" placeholder="数据库类型" style="width: 10%">
            <el-option v-for="item in optionsDbType"  :key="item.value" :label="item.label"  :value="item.value" />
          </el-select>
          <el-button style="width: 10%" type="primary" @click="onAddDbinfo">添加</el-button>
         </div> 
    </el-form-item>
  </el-dialog>

</template>
  
<script lang="ts" setup>
// 1. 其他功能拓展
import { ref, reactive, compile } from "vue";
import { queryByPage, deleteData } from "./ApiProject.js"; // 不同页面不同的接口
import { useRouter } from "vue-router";

const router = useRouter(); 

// 2. 分页参数
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 3. 搜索功能 - 筛选表单
const searchForm = reactive({});


// 4. 表格列 - 不同页面不同的列
const columnList = ref([
  { prop: "id", label: "项目编号" },
  { prop: "project_name", label: "项目名称" },
  { prop: "project_desc", label: "项目描述" },
  { prop: "create_time", label: "创建时间" },
]);

// 5. 表格数据
const tableData = ref([]);

// 6. 加载页面数据
const loadData = () => {
  let searchData = searchForm;
  searchData["page"] = currentPage.value;
  searchData["pageSize"] = pageSize.value;

  queryByPage(searchData).then(
    (res: { data: { data: never[]; total: number; msg: string } }) => {
      tableData.value = res.data.data;
      total.value = res.data.total;
    }
  );
};
loadData();

// 7. 变更页大小
const handleSizeChange = (val: number) => {
  console.log("页大小变化:" + val);
  pageSize.value = val;
  loadData();
};

// 8. 变更页码
const handleCurrentChange = (val: number) => {
  console.log("页码变化:" + val);
  currentPage.value = val;
  loadData();
};

// 9. 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
  let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index]["id"],
    };
  }
  router.push({
    path: "/ApiProjectForm", // 不同页面不同的表单路径
    query: params_data,
  });
};

// 10. 删除项目
const onDelete = (index: number) => {
    deleteData(tableData.value[index]["id"]).then((res: {}) => {
    loadData();
  });
};


// ---------------------扩展：数据库展示弹窗-------------------------------

// 11. 增加功能：数据库相关的操作
import { queryByPage as queryByPageList } from "./DbBaseManage.js"; // 不同页面不同的接口
import { updateData } from "./DbBaseManage.js"; // 不同页面不同的接口
import { insertData } from "./DbBaseManage.js"; // 不同页面不同的接口
import { deleteData as deleteDbData } from "./DbBaseManage.js"; // 不同页面不同的接口

const DbBaseManageList = ref([] as any[]); // 数据库数据列表数据
const currentApiHistoryPage = ref(1) // 页码
const DbBaseManageDialogFormVisible = ref(false) // 是否展示弹窗
const currentProjectId = ref(0) // 当前展示的执行记录关联的 ProjectId


// 11-1 显示当前弹窗信息
const showDbBaseManage = (index: number) => {
    DbBaseManageDialogFormVisible.value = true
    currentProjectId.value = tableData.value[index]["id"]
    console.log("当前添加数据库的ID",currentProjectId.value)
    loadDbBaseManage(currentProjectId.value)
}

// 11-2 加载当中项目的数据
const loadDbBaseManage = (index: number) => {
    let searchData = {}
    searchData["project_id"] = index
    searchData["page"] = currentApiHistoryPage.value
    searchData["pageSize"] = 100
    queryByPageList(searchData).then((res: { data: { data: never[]; total: number; msg: string } }) => {
        DbBaseManageList.value = res.data.data
    })
}

// 11-3 数据库信息-提交表单-表单数据
const ruleForm =reactive({
  id:0,
  project_id: currentProjectId.value,
  name: "",
  db_info:"",
  ref_name:"",
  db_type: "",
  is_enabled:"1", // 默认值 1
}); 

// 11-4 下拉列表的值-是否启动
const options = [
  {
    value: '1',
    label: '是',
  },
  {
    value: '0',
    label: '否',
  }
]

// 11-5 下拉列表的值-数据库类型
const optionsDbType = [
  {
    value: 'Mysql',
    label: 'Mysql',
  },
  {
    value: 'Oracle',
    label: 'Oracle',
  }
]


// 11-6  添加-数据库数据
const onAddDbinfo = (index: number) => {
     // 添加数据的时候，设置项目对应的值
      ruleForm.project_id = currentProjectId.value

      insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
          if (res.data.code == 200) {
            loadDbBaseManage(currentProjectId.value);

            // 设置字段都为空：
            ruleForm.name = ""
            ruleForm.ref_name = ""
            ruleForm.db_info = ""
            ruleForm.is_enabled = "1"
            ruleForm.db_type = ""
          }
        });
};

// 11-7 修改-数据库数据
// 修改的变量
const UpDataruleForm =reactive({
  id:0,
  project_id: currentProjectId.value,
  name: "",
  db_info:"",
  ref_name:"",
  db_type: "",
  is_enabled:"1", // 默认值 1
}); 

// 修改的方法
const upDataDbinfo = (index: number) => {
     // 添加数据的时候，设置项目对应的值
      // ruleForm.project_id = currentProjectId.value

      UpDataruleForm.id = DbBaseManageList.value[index].id
      UpDataruleForm.project_id = DbBaseManageList.value[index].project_id
      UpDataruleForm.name = DbBaseManageList.value[index].name
      UpDataruleForm.ref_name = DbBaseManageList.value[index].ref_name
      UpDataruleForm.db_info = DbBaseManageList.value[index].db_info
      UpDataruleForm.db_type = DbBaseManageList.value[index].db_type
      UpDataruleForm.is_enabled = DbBaseManageList.value[index].is_enabled === '1' ? '0' : '1';
        
        updateData(UpDataruleForm).then((res: { data: { code: number; msg: string; }; }) => {
          if (res.data.code == 200) {
            loadDbBaseManage(currentProjectId.value)
          }
        });
};

// 11-8 删除数据库
const onDeleteDb = (index: number) => {
    deleteDbData(DbBaseManageList.value[index]["id"]).then((res: {}) => {
    loadDbBaseManage(currentProjectId.value)
  });
};

// ---------------------  END扩展：数据库展示弹窗-------------------------------
</script>
  
<style>
.demo-pagination-block .demo-pagination-block {
  margin-top: 10px;   /* 设置元素的上外边距,根据需要调整间隔大小 */
}
.demo-pagination-block .demonstration {
  margin-bottom: 16px; /* 设置元素的下外边距,根据需要调整间隔大小 */
}
.input-group {  
  margin-top: 16px; /* 设置元素的上外边距,根据需要调整间隔大小  */  
}
</style>
