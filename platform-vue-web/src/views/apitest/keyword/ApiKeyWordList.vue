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
      <template #actions>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增关键字
        </el-button>
        <el-button type="success" @click="onBatchImport">
          <el-icon><Upload /></el-icon>
          批量导入
        </el-button>
        <el-button type="warning" @click="onBatchExport">
          <el-icon><Download /></el-icon>
          批量导出
        </el-button>
        <el-button type="danger" @click="onBatchDelete" :disabled="selectedRows.length === 0">
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="关键字库"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
    >
      <el-table-column type="selection" width="55" @selection-change="handleSelectionChange" />
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="关键字名称" show-overflow-tooltip>
        <template #default="scope">
          <span class="keyword-name">{{ scope.row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="keyword_fun_name" label="函数名" show-overflow-tooltip>
        <template #default="scope">
          <code class="func-name">{{ scope.row.keyword_fun_name }}</code>
        </template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="120" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.is_enabled === '1' ? 'success' : 'info'" size="small">
            {{ scope.row.is_enabled === '1' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="170">
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
import { formatDateTime } from '~/utils/timeFormatter';
import { queryByPage, deleteData, batchDelete, batchImport, batchExport } from "./apiKeyWord.js";
import { queryAll } from "./operationType.js";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Upload, Download, Delete } from '@element-plus/icons-vue';
import BaseSearch from '~/components/BaseSearch/index.vue';
import BaseTable from '~/components/BaseTable/index.vue';

const router = useRouter();

// 分页参数
const pagination = ref({ page: 1, limit: 10 });
const total = ref(0);
const loading = ref(false);

// 搜索表单
const searchForm = reactive({ name: null, operation_type_id: null });

// 表格数据
const tableData = ref([]);

// 操作类型列表
const operationTypeList = ref<Array<{id: number, operation_type_name: string}>>([]);

// 选中的行数据
const selectedRows = ref([]);

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

onMounted(() => {
  loadData();
  getOperationTypeList();
});

// 处理表格选择变化
const handleSelectionChange = (selection: any[]) => {
  selectedRows.value = selection;
};

// 批量删除
const onBatchDelete = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的记录');
    return;
  }
  
  ElMessageBox.confirm(`确定要删除选中的${selectedRows.value.length}条记录吗？`, '批量删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    const ids = selectedRows.value.map(row => row.id).join(',');
    batchDelete(ids).then((res: { data: { code: number; msg: string } }) => {
      if (res.data.code === 200) {
        ElMessage.success(res.data.msg || '批量删除成功');
        selectedRows.value = [];
        loadData();
      } else {
        ElMessage.error(res.data.msg || '批量删除失败');
      }
    }).catch((error: any) => {
      console.error('批量删除失败:', error);
      ElMessage.error('批量删除失败，请稍后重试');
    });
  }).catch(() => {});
};

// 批量导入
const onBatchImport = () => {
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = '.json,.csv';
  input.onchange = (e: any) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (e: any) => {
      const content = e.target.result;
      batchImport(content).then((res: { data: { code: number; msg: string } }) => {
        if (res.data.code === 200) {
          ElMessage.success(res.data.msg || '批量导入成功');
          loadData();
        } else {
          ElMessage.error(res.data.msg || '批量导入失败');
        }
      }).catch((error: any) => {
        console.error('批量导入失败:', error);
        ElMessage.error('批量导入失败，请稍后重试');
      });
    };
    reader.readAsText(file);
  };
  input.click();
};

// 批量导出
const onBatchExport = () => {
  const ids = selectedRows.value.length > 0 ? selectedRows.value.map(row => row.id).join(',') : null;
  
  // 直接导出JSON格式
  batchExport(ids, 'json').then((res: { data: { code: number; data: any; msg: string } }) => {
    if (res.data.code === 200) {
      downloadFile(res.data.data.content, res.data.data.filename);
      ElMessage.success('导出成功');
    } else {
      ElMessage.error(res.data.msg || '导出失败');
    }
  }).catch((error: any) => {
    console.error('导出失败:', error);
    ElMessage.error('导出失败，请稍后重试');
  });
};

// 下载文件
const downloadFile = (content: string, filename: string) => {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
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

.keyword-name {
  font-weight: 500;
}

.func-name {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
}
</style>