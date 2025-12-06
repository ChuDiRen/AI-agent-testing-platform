<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="关键字名称" prop="name">
        <el-input v-model="searchForm.name" placeholder="根据关键字名称筛选" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item label="操作类型" prop="operation_type_id">
        <el-select v-model="searchForm.operation_type_id" placeholder="选择所属类型" clearable style="width: 180px">
          <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>     
        </el-select>
      </el-form-item>
      <el-form-item label="执行引擎" prop="plugin_id">
        <el-select v-model="searchForm.plugin_id" placeholder="选择执行引擎" clearable style="width: 180px">
          <el-option v-for="plugin in pluginList" :key="plugin.id" :label="plugin.plugin_name" :value="plugin.id"/>     
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增关键字
        </el-button>
        <el-button type="success" @click="showSyncDialog">
          <el-icon><Refresh /></el-icon>
          从引擎同步
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="关键字管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="关键字编号" width="100" />
      <el-table-column prop="name" label="关键字名称" show-overflow-tooltip />
      <el-table-column prop="keyword_fun_name" label="关键字函数名" show-overflow-tooltip />
      <el-table-column prop="plugin_name" label="执行引擎" width="120">
        <template #default="scope">
          <el-tag v-if="scope.row.plugin_name" type="success" size="small">{{ scope.row.plugin_name }}</el-tag>
          <span v-else class="text-gray">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="120" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="是否启用" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_enabled === '1' ? 'success' : 'info'">
            {{ scope.row.is_enabled === '1' ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
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

    <!-- 同步关键字对话框 -->
    <el-dialog v-model="syncDialogVisible" title="从执行引擎同步关键字" width="450px">
      <el-form label-width="100px">
        <el-form-item label="执行引擎" required>
          <el-select v-model="syncForm.plugin_id" placeholder="选择执行引擎" style="width: 100%">
            <el-option v-for="plugin in pluginList" :key="plugin.id" :label="plugin.plugin_name" :value="plugin.id"/>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="syncDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="syncLoading" @click="doSync">同步</el-button>
      </template>
    </el-dialog>
  </div>
</template>
  
<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { formatDateTime } from '@/utils/timeFormatter';
import { queryByPage, deleteData, syncFromPlugin } from "./apiKeyWord.js";
import { queryAll } from "./operationType.js";
import { listEnabledPlugins } from "@/views/plugin/plugin.js";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Refresh } from '@element-plus/icons-vue';
import BaseSearch from '@/components/BaseSearch/index.vue';
import BaseTable from '@/components/BaseTable/index.vue';

const router = useRouter();

// 分页参数
const pagination = ref({ page: 1, limit: 10 });
const total = ref(0);
const loading = ref(false);

// 搜索表单
const searchForm = reactive({ name: null, operation_type_id: null, plugin_id: null });

// 表格数据
const tableData = ref([]);

// 操作类型列表
const operationTypeList = ref<Array<{id: number, operation_type_name: string}>>([]);

// 执行引擎列表
const pluginList = ref<Array<{id: number, plugin_name: string, plugin_code: string}>>([]);

// 同步对话框
const syncDialogVisible = ref(false);
const syncLoading = ref(false);
const syncForm = reactive({ plugin_id: null });

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
  router.push({ path: "/ApiKeyWordForm", query: params_data });
};

// 重置搜索
const resetSearch = () => {
  searchForm.name = null;
  searchForm.operation_type_id = null;
  searchForm.plugin_id = null;
  pagination.value.page = 1;
  loadData();
};

// 删除
const onDelete = (index: number) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(`确定要删除关键字"${item.name}"吗？`, '删除确认', {
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

// 加载操作类型
const getOperationTypeList = () => {
  queryAll().then((res: { data: { code: number; data: any; msg: string } }) => {
    if (res.data.code === 200) {
      operationTypeList.value = res.data.data || [];
    }
  }).catch((error: any) => {
    console.error('加载操作类型失败:', error);
  });
};

// 加载执行引擎列表
const getPluginList = () => {
  listEnabledPlugins('executor').then((res: { data: { code: number; data: any; msg: string } }) => {
    if (res.data.code === 200) {
      pluginList.value = res.data.data || [];
    }
  }).catch((error: any) => {
    console.error('加载执行引擎失败:', error);
  });
};

// 显示同步对话框
const showSyncDialog = () => {
  syncForm.plugin_id = null;
  syncDialogVisible.value = true;
};

// 执行同步
const doSync = () => {
  if (!syncForm.plugin_id) {
    ElMessage.warning('请选择执行引擎');
    return;
  }
  syncLoading.value = true;
  syncFromPlugin(syncForm.plugin_id)
    .then((res: { data: { code: number; msg: string; data: any } }) => {
      if (res.data.code === 200) {
        ElMessage.success(res.data.msg || '同步成功');
        syncDialogVisible.value = false;
        loadData();
        getOperationTypeList(); // 刷新操作类型列表（可能有新增）
      } else {
        ElMessage.error(res.data.msg || '同步失败');
      }
    })
    .catch((error: any) => {
      console.error('同步失败:', error);
      ElMessage.error('同步失败，请稍后重试');
    })
    .finally(() => {
      syncLoading.value = false;
    });
};

onMounted(() => {
  loadData();
  getOperationTypeList();
  getPluginList();
});
</script>


<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.el-select {  
  width: 200px;
}

.text-gray {
  color: #909399;
}
</style>