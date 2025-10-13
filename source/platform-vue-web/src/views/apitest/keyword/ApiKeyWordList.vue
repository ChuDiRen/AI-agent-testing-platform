<template>
  <!-- 搜索表单 --> 
  <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
    
    <el-form-item label="关键字名称：">
      <el-input  v-model="searchForm.name"  placeholder="根据关键字名称筛选"/>
    </el-form-item>

    <el-form-item label="操作类型ID：">
      <el-select v-model="searchForm.operation_type_id"  placeholder="选择所属类型" clearable>
        <!-- 需要对应的操作类型的下拉数据 -->
      <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>     
    </el-select>
    </el-form-item>

    <el-row class="mb-4" type="flex" justify="end">
      <el-button type="primary" @click="loadData()">查询</el-button>
      <el-button type="warning" @click="onDataForm(-1)" >新增关键字方法</el-button>
    </el-row>
  </el-form>
  <!-- END 搜索表单 -->


  <!-- 数据表格 -->
  <el-table :data="tableData" style="width: 100%" max-height="500">
    <!-- 数据列 -->
    <el-table-column
      v-for="col in columnList"
      :prop="col.prop"
      :label="col.label"
      :key="col.prop"
      :show-overflow-tooltip="true"
    >
    <!-- 自定义某个列的数据 -->
      <template #default="scope">
        <span v-if="col.prop === 'is_enabled'">
          {{
              scope.row.is_enabled === "false"
              ? "否"
              : scope.row.is_enabled === "true"
              ? "是"
              : "-"
          }}
        </span>
      </template>

    </el-table-column>
  <!-- END 数据表格  -->

    <!-- 操作 -->
    <el-table-column fixed="right" label="操作">
      <template #default="scope">
        <el-button link type="primary" size="small"  @click.prevent="onDataForm(scope.$index)">
          编辑
        </el-button>
          
        <el-button link type="primary" size="small"  @click.prevent="onDelete(scope.$index)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>

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

</template>
  
<script lang="ts" setup>
// 其他功能拓展
import { ref, reactive } from "vue";
import { queryByPage, deleteData } from "./ApiKeyWord.js"; // 不同页面不同的接口
import { useRouter } from "vue-router";
const router = useRouter();

// 分页参数
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 搜索功能 - 筛选表单
const searchForm = reactive({ "name": null, "operation_type_id": null });

// 表格列 - 不同页面不同的列
const columnList = ref([
  { prop: "id", label: "关键字编号" },
  { prop: "name", label: "关键字名称" },
  { prop: "keyword_fun_name", label: "关键字函数名" },
  { prop: "is_enabled", label: "是否启动" },
  { prop: "create_time", label: "创建时间" },
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
      tableData.value = res.data.data;
      total.value = res.data.total;
    }
  );
};
loadData();

// 变更页大小
const handleSizeChange = (val: number) => {
  console.log("页大小变化:" + val);
  pageSize.value = val;
  loadData();
};

// 变更页码
const handleCurrentChange = (val: number) => {
  console.log("页码变化:" + val);
  currentPage.value = val;
  loadData();
};

// 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
  let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index]["id"],
    };
  }
  router.push({
    path: "/ApiKeyWordForm", // 不同页面不同的表单路径
    query: params_data,
  });
};

// 删除
const onDelete = (index: number) => {
  deleteData(tableData.value[index]["id"]).then((res: {}) => {
    loadData();
  });
};

// 加载元素操作类型
import { queryAll } from "./ApiOperationType.js"; // 不同页面不同的接口
const operationTypeList = ref([{
  id: 0,
  operation_type_name: '',
  create_time: ''
}]);
function getOperationTypeList() {
  queryAll().then((res) => {
    operationTypeList.value = res.data.data;
  });
}
getOperationTypeList();
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