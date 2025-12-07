<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="素材名称" prop="mate_name">
        <el-input v-model="searchForm.mate_name" placeholder="根据素材名称筛选" clearable style="width: 180px" />
      </el-form-item>
      <el-form-item label="所属项目" prop="project_id">
        <el-select v-model="searchForm.project_id" placeholder="选择所属项目" clearable style="width: 180px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>     
        </el-select>
      </el-form-item>
      <template #actions>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增素材
        </el-button>
      </template>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="素材管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <el-table-column prop="id" label="编号" width="80" />
      <el-table-column prop="mate_name" label="素材名称" show-overflow-tooltip />
      <el-table-column prop="object_url" label="素材路径" show-overflow-tooltip />
      <el-table-column prop="file_type" label="素材类型" width="100" />
      <el-table-column prop="create_time" label="上传时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="180">
        <template #default="scope">
          <el-button link type="primary" @click.prevent="onDownloadFile(scope.$index)">下载</el-button>
          <el-button link type="primary" @click.prevent="copyMaterialUrl(scope.$index)">复制链接</el-button>
          <el-button link type="danger" @click.prevent="onDelete(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { queryByPage, deleteData, downloadFile } from "./apiMeta.js";
import { queryAllProject } from "../project/apiProject.js";
import { formatDateTime } from '@/utils/timeFormatter';
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
const searchForm = reactive({ mate_name: null, project_id: null });

// 表格数据
const tableData = ref([]);

// 项目列表
const projectList = ref<Array<{id: number, project_name: string}>>([]);

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

// 加载项目列表
const getProjectList = () => {
  queryAllProject().then((res: { data: { code: number; data: any; msg: string } }) => {
    if (res.data.code === 200) {
      projectList.value = res.data.data || [];
    }
  }).catch((error: any) => {
    console.error('加载项目列表失败:', error);
  });
};

// 重置搜索
const resetSearch = () => {
  searchForm.mate_name = null;
  searchForm.project_id = null;
  pagination.value.page = 1;
  loadData();
};

// 打开表单
const onDataForm = (index: number) => {
  let params_data = {};
  if (index >= 0) {
    params_data = { id: tableData.value[index]["id"] };
  }
  router.push({ path: "/ApiMetaForm", query: params_data });
};

// 删除
const onDelete = (index: number) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(`确定要删除素材"${item.mate_name}"吗？`, '删除确认', {
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



// ====================================扩展： 下载/复制链接的功能========================================
// 下载文件 - 获取地址 打开链接
const onDownloadFile = (index: number) => {
  const id = tableData.value[index]["id"];

  // 调用接口获取下载地址
  downloadFile(id).then((res) => {
    if (res.data.code === 200) {
      const downloadUrl = res.data.data.downloadUrl;

      // 使用 window.open 打开下载链接
      window.open(downloadUrl, '_blank');
    } else {
      ElMessage.error('获取下载地址失败，文件不存在');
    }
  }).catch((err) => {
    ElMessage.error('请求失败：' + err.message);
  });
};

// 下载文件 - 获取地址 复制数据
const copyMaterialUrl = (index) => {
    const id = tableData.value[index]["id"];

  // 调用接口获取下载地址
  downloadFile(id).then((res) => {
    if (res.data.code === 200) {
      const downloadUrl = res.data.data.downloadUrl;

      //复制downloadUrl 到剪贴板
      navigator.clipboard.writeText(downloadUrl).then(() => {
        ElMessage.success('链接已复制到剪贴板');
      }).catch((err) => {
        ElMessage.error('复制失败：' + err.message);
      });

    } else {
      ElMessage.error('获取下载地址失败，文件不存在');
    }
  }).catch((err) => {
    ElMessage.error('请求失败：' + err.message);
  });
};

// ====================================END 扩展： 下载/复制链接的功能========================================

onMounted(() => {
  loadData();
  getProjectList();
});
</script>
  
<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

.page-container {
  width: 100%;
  overflow-x: hidden;
}

.page-card {
  width: 100%;
  box-sizing: border-box;
}

.search-form {
  width: 100%;
}

.search-input,
.search-select {
  width: 200px;
}

.table-wrapper {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

.responsive-table {
  min-width: 800px; /* 表格最小宽度，小于此宽度会出现滚动条 */
}

/* 平板适配 */
@media (max-width: 1024px) {
  .search-input,
  .search-select {
    width: 180px;
  }
  
  .responsive-table {
    min-width: 700px;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .responsive-form {
    display: flex;
    flex-direction: column;
  }
  
  .responsive-form :deep(.el-form-item) {
    margin-right: 0;
    margin-bottom: 12px;
    width: 100%;
  }
  
  .search-input,
  .search-select {
    width: 100%;
  }
  
  .search-buttons {
    display: flex;
    gap: 8px;
  }
  
  .search-buttons :deep(.el-button) {
    flex: 1;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .responsive-table {
    min-width: 600px;
  }
  
  .action-column {
    min-width: 150px;
  }
}

/* 小屏幕手机适配 */
@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .card-header h3 {
    margin: 0;
  }
  
  .card-header .el-button {
    width: 100%;
  }
  
  .responsive-table {
    min-width: 500px;
  }
  
  .pagination {
    overflow-x: auto;
  }
  
  .pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
  