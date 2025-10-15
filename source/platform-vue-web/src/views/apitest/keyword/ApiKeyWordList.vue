<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>关键字管理</h3>
          <el-button type="primary" @click="onDataForm(-1)">
            <el-icon><Plus /></el-icon>
            新增关键字
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 --> 
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="search-form">
    
    <el-form-item label="关键字名称：">
      <el-input  v-model="searchForm.name"  placeholder="根据关键字名称筛选"/>
    </el-form-item>

    <el-form-item label="操作类型ID：">
      <el-select v-model="searchForm.operation_type_id"  placeholder="选择所属类型" clearable>
        <!-- 需要对应的操作类型的下拉数据 -->
      <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>     
    </el-select>
    </el-form-item>

    <el-form-item>
      <el-button type="primary" @click="loadData()">查询</el-button>
      <el-button @click="resetSearch">重置</el-button>
    </el-form-item>
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
        <span v-else-if="col.prop === 'create_time'">
          {{ formatDateTime(scope.row.create_time) }}
        </span>
        <span v-else>
          {{ scope.row[col.prop] }}
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
  <div class="pagination">
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
    </el-card>
  </div>
</template>
  
<script lang="ts" setup>
// 其他功能拓展
import { ref, reactive } from "vue";
import { formatDateTime } from '~/utils/timeFormatter';
import { queryByPage, deleteData } from "./apiKeyWord.js"; // 不同页面不同的接口
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
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
    (res: { data: { code: number; data: never[]; total: number; msg: string } }) => {
      if (res.data.code === 200) {
        tableData.value = res.data.data || [];
        total.value = res.data.total || 0;
        ElMessage.success('查询成功');
      } else {
        ElMessage.error(res.data.msg || '查询失败');
      }
    }
  ).catch((error: any) => {
    console.error('查询失败:', error);
    ElMessage.error('查询失败，请稍后重试');
  });
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
  const item = tableData.value[index];
  ElMessageBox.confirm(
    `确定要删除关键字"${item.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteData(item.id).then((res: { data: { code: number; msg: string } }) => {
      if (res.data.code === 200) {
        ElMessage.success('删除成功');
        loadData();
      } else {
        ElMessage.error(res.data.msg || '删除失败');
      }
    }).catch((error: any) => {
      console.error('删除失败:', error);
      ElMessage.error('删除失败，请稍后重试');
    });
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// 加载元素操作类型
import { queryAll } from "./operationType.js"; // 不同页面不同的接口
const operationTypeList = ref([{
  id: 0,
  operation_type_name: '',
  create_time: ''
}]);
function getOperationTypeList() {
  queryAll().then((res: { data: { code: number; data: any; msg: string } }) => {
    if (res.data.code === 200) {
      operationTypeList.value = res.data.data || [];
    } else {
      console.error('加载操作类型失败:', res.data.msg);
    }
  }).catch((error: any) => {
    console.error('加载操作类型失败:', error);
  });
}
getOperationTypeList();
</script>


<style scoped>
@import '@/styles/common-list.css';
@import '@/styles/common-form.css';

.el-select {  
  width: 200px;
}  
</style>