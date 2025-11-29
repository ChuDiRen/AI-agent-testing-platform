<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="操作类型名称" prop="operation_type_name">
        <el-input v-model="searchForm.operation_type_name" placeholder="根据操作类型名称筛选" clearable style="width: 200px" />
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增操作类型
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="操作类型管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="操作类型编号" width="120" />
      <el-table-column prop="operation_type_name" label="操作类型名称" show-overflow-tooltip />
      <el-table-column prop="ex_fun_name" label="执行函数名" show-overflow-tooltip />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="150">
        <template #default="scope">
          <el-button link type="primary" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
          <el-button link type="danger" @click.prevent="onDelete(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { formatDateTime } from '@/utils/timeFormatter';
import { queryByPage, deleteData } from "./operationtype.js";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import BaseSearch from '@/components/BaseSearch/index.vue';
import BaseTable from '@/components/BaseTable/index.vue';

const router = useRouter();

// 分页参数
const pagination = ref({ page: 1, limit: 10 });
const total = ref(0);
const loading = ref(false);

// 搜索表单
const searchForm = reactive({ operation_type_name: null });

// 表格数据
const tableData = ref([]);

// 加载页面数据
const loadData = () => {
  loading.value = true;
  queryByPage({
    ...searchForm,
    page: pagination.value.page,
    pageSize: pagination.value.limit
  }).then((res: { data: { code: number; data: never[]; total: number; msg: string } }) => {
    if (res.data.code === 200) {
      tableData.value = res.data.data || [];
      total.value = res.data.total || 0;
    } else {
      ElMessage.error(res.data.msg || '查询失败');
    }
  }).catch((error: any) => {
    console.error('查询失败:', error);
    ElMessage.error('查询失败，请稍后重试');
  }).finally(() => {
    loading.value = false;
  });
};

// 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
  let params_data = {};
  if (index >= 0) {
    params_data = { id: tableData.value[index]["id"] };
  }
  router.push({ path: "/OperationTypeForm", query: params_data });
};

// 重置搜索
const resetSearch = () => {
  searchForm.operation_type_name = null;
  pagination.value.page = 1;
  loadData();
};

// 删除
const onDelete = (index: number) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(`确定要删除操作类型"${item.operation_type_name}"吗？`, '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
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
  }).catch(() => {});
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>
