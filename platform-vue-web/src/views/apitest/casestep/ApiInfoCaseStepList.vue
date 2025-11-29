<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="用例ID" prop="api_case_info_id">
        <el-input v-model="searchForm.api_case_info_id" placeholder="根据用例ID筛选" clearable style="width: 150px" />
      </el-form-item>
      <el-form-item label="步骤描述" prop="step_desc">
        <el-input v-model="searchForm.step_desc" placeholder="根据步骤描述筛选" clearable style="width: 180px" />
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增步骤
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="用例步骤管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="步骤编号" width="90" />
      <el-table-column prop="api_case_info_id" label="用例ID" width="90" />
      <el-table-column prop="key_word_id" label="关键字ID" width="100" />
      <el-table-column prop="step_desc" label="步骤描述" min-width="180" show-overflow-tooltip />
      <el-table-column prop="ref_variable" label="引用变量" width="120" show-overflow-tooltip />
      <el-table-column prop="run_order" label="执行顺序" width="90" align="center" sortable />
      <el-table-column prop="create_time" label="创建时间" width="170">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="200">
        <template #default="scope">
          <el-button link type="primary" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
          <el-button link type="success" @click.prevent="moveUp(scope.$index)" :disabled="scope.$index === 0">上移</el-button>
          <el-button link type="success" @click.prevent="moveDown(scope.$index)" :disabled="scope.$index === tableData.length - 1">下移</el-button>
          <el-button link type="danger" @click.prevent="onDelete(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { formatDateTime } from '@/utils/timeFormatter';
import { queryByPage, deleteData, updateOrder } from "./apiinfocasestep.js";
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
const searchForm = reactive({ 
  api_case_info_id: null,
  step_desc: null 
});

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
  router.push({ path: "/ApiInfoCaseStepForm", query: params_data });
};

// 重置搜索
const resetSearch = () => {
  searchForm.api_case_info_id = null;
  searchForm.step_desc = null;
  pagination.value.page = 1;
  loadData();
};

// 删除
const onDelete = (index: number) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(
    `确定要删除步骤"${item.step_desc}"吗？`,
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

// 上移步骤
const moveUp = (index: number) => {
  if (index === 0) return;
  const currentItem = tableData.value[index];
  const prevItem = tableData.value[index - 1];
  
  // 交换顺序
  const tempOrder = currentItem.run_order;
  currentItem.run_order = prevItem.run_order;
  prevItem.run_order = tempOrder;
  
  // 更新顺序
  updateOrder([
    { id: currentItem.id, run_order: currentItem.run_order },
    { id: prevItem.id, run_order: prevItem.run_order }
  ]).then((res: { data: { code: number; msg: string } }) => {
    if (res.data.code === 200) {
      ElMessage.success('上移成功');
      loadData();
    } else {
      ElMessage.error(res.data.msg || '上移失败');
    }
  }).catch((error: any) => {
    console.error('上移失败:', error);
    ElMessage.error('上移失败，请稍后重试');
  });
};

// 下移步骤
const moveDown = (index: number) => {
  if (index === tableData.value.length - 1) return;
  const currentItem = tableData.value[index];
  const nextItem = tableData.value[index + 1];
  
  // 交换顺序
  const tempOrder = currentItem.run_order;
  currentItem.run_order = nextItem.run_order;
  nextItem.run_order = tempOrder;
  
  // 更新顺序
  updateOrder([
    { id: currentItem.id, run_order: currentItem.run_order },
    { id: nextItem.id, run_order: nextItem.run_order }
  ]).then((res: { data: { code: number; msg: string } }) => {
    if (res.data.code === 200) {
      ElMessage.success('下移成功');
      loadData();
    } else {
      ElMessage.error(res.data.msg || '下移失败');
    }
  }).catch((error: any) => {
    console.error('下移失败:', error);
    ElMessage.error('下移失败，请稍后重试');
  });
};

onMounted(() => {
  loadData();
});
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>
