<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>用例步骤管理</h3>
          <el-button type="primary" @click="onDataForm(-1)">
            <el-icon><Plus /></el-icon>
            新增步骤
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用例ID：">
          <el-input v-model="searchForm.api_case_info_id" placeholder="根据用例ID筛选" />
        </el-form-item>

        <el-form-item label="步骤描述：">
          <el-input v-model="searchForm.step_desc" placeholder="根据步骤描述筛选" />
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
        <el-table-column prop="id" label="步骤编号" width="100" show-overflow-tooltip />
        <el-table-column prop="api_case_info_id" label="用例ID" width="100" show-overflow-tooltip />
        <el-table-column prop="key_word_id" label="关键字ID" width="120" show-overflow-tooltip />
        <el-table-column prop="step_desc" label="步骤描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ref_variable" label="引用变量" width="150" show-overflow-tooltip />
        <el-table-column prop="run_order" label="执行顺序" width="100" align="center" sortable />
        <el-table-column prop="create_time" label="创建时间" width="180" show-overflow-tooltip>
          <template #default="scope">
            {{ formatDateTime(scope.row.create_time) }}
          </template>
        </el-table-column>

        <!-- 操作 -->
        <el-table-column fixed="right" label="操作" width="220">
          <template #default="scope">
            <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
              编辑
            </el-button>
            <el-button 
              link 
              type="success" 
              size="small" 
              @click.prevent="moveUp(scope.$index)"
              :disabled="scope.$index === 0"
            >
              上移
            </el-button>
            <el-button 
              link 
              type="success" 
              size="small" 
              @click.prevent="moveDown(scope.$index)"
              :disabled="scope.$index === tableData.length - 1"
            >
              下移
            </el-button>
            <el-button link type="danger" size="small" @click.prevent="onDelete(scope.$index)">
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
import { ref, reactive } from "vue";
import { formatDateTime } from '~/utils/timeFormatter';
import { queryByPage, deleteData, updateOrder } from "./apiinfocasestep.js";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';

const router = useRouter();

// 分页参数
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 搜索功能 - 筛选表单
const searchForm = reactive({ 
  api_case_info_id: null,
  step_desc: null 
});

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
  pageSize.value = val;
  loadData();
};

// 变更页码
const handleCurrentChange = (val: number) => {
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
    path: "/ApiInfoCaseStepForm",
    query: params_data,
  });
};

// 重置搜索
const resetSearch = () => {
  searchForm.api_case_info_id = null;
  searchForm.step_desc = null;
  currentPage.value = 1;
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
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-card {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
