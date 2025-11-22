<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>接口信息管理</h3>
          <div>
            <el-button type="success" @click="showImportDialog">
              <el-icon><Upload /></el-icon>
              导入Swagger
            </el-button>
            <el-button type="primary" @click="onDataForm(-1)">
              <el-icon><Plus /></el-icon>
              新增接口
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="searchForm.project_id" placeholder="选择项目" clearable style="width: 180px">
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>     
          </el-select>
        </el-form-item>
        
        <el-form-item label="接口名称">
          <el-input v-model="searchForm.api_name" placeholder="根据接口名称筛选" clearable style="width: 180px"/>
        </el-form-item>
        
        <el-form-item label="请求方法">
          <el-select v-model="searchForm.request_method" placeholder="选择请求方法" clearable style="width: 180px">
            <el-option v-for="method in methodList" :key="method" :label="method" :value="method"/>     
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      <!-- END 搜索表单 -->

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%" max-height="600">
      <el-table-column prop="id" label="接口编号" width="100" />
      <el-table-column prop="api_name" label="接口名称" width="200" show-overflow-tooltip />
      <el-table-column prop="request_method" label="请求方法" width="120">
        <template #default="scope">
          <el-tag :type="getMethodTagType(scope.row.request_method)">
            {{ scope.row.request_method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="request_url" label="请求地址" min-width="300" show-overflow-tooltip />
      <el-table-column prop="project_id" label="所属项目" width="150">
        <template #default="scope">
          {{ getProjectName(scope.row.project_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="250">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
            编辑
          </el-button>
          <el-button link type="success" size="small" @click.prevent="onTestEditor(scope.$index)">
            测试
          </el-button>
          <el-button link type="info" size="small" @click.prevent="onViewHistory(scope.$index)">
            历史
          </el-button>
          <el-button link type="danger" size="small" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- END 数据表格 -->

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

    <!-- 导入Swagger对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入Swagger文档" width="600px">
      <el-form :model="importForm" label-width="120px">
        <el-form-item label="选择项目" required>
          <el-select v-model="importForm.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>
          </el-select>
        </el-form-item>
        
        <el-form-item label="导入方式">
          <el-radio-group v-model="importForm.importType">
            <el-radio label="url">URL导入</el-radio>
            <el-radio label="json">JSON导入</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item v-if="importForm.importType === 'url'" label="Swagger URL" required>
          <el-input 
            v-model="importForm.swagger_url" 
            placeholder="例如: https://petstore.swagger.io/v2/swagger.json"
            clearable
          />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            支持OpenAPI 2.0和3.0规范
          </div>
        </el-form-item>
        
        <el-form-item v-if="importForm.importType === 'json'" label="Swagger JSON" required>
          <el-input 
            v-model="importForm.swagger_json_text" 
            type="textarea"
            :rows="8"
            placeholder="粘贴Swagger JSON内容"
          />
        </el-form-item>
        
        <el-form-item label="覆盖已存在">
          <el-switch v-model="importForm.override_existing" />
          <div style="color: #909399; font-size: 12px; margin-top: 5px;">
            开启后将更新已存在的同名接口
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { queryByPage, deleteData, getMethods, importSwagger } from './apiinfo.js';
import { queryByPage as getProjectList } from '../project/apiProject.js';
import { formatDateTime } from '~/utils/timeFormatter';
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();

// 分页参数
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 搜索功能 - 筛选表单
const searchForm = reactive({
  project_id: null,
  api_name: null,
  request_method: null
});

// 表格数据
const tableData = ref([]);

// 项目列表
const projectList = ref([]);

// 请求方法列表
const methodList = ref([]);

// 导入对话框
const importDialogVisible = ref(false);
const importing = ref(false);
const importForm = reactive({
  project_id: null,
  importType: 'url',
  swagger_url: '',
  swagger_json_text: '',
  override_existing: false
});

// 重置搜索
const resetSearch = () => {
  searchForm.project_id = null;
  searchForm.api_name = null;
  searchForm.request_method = null;
  currentPage.value = 1;
  loadData();
};

// 加载页面数据
const loadData = () => {
  let searchData = {
    ...searchForm,
    page: currentPage.value,
    pageSize: pageSize.value
  };

  queryByPage(searchData).then((res) => {
    if (res.data.code === 200) {
      tableData.value = res.data.data || [];
      total.value = res.data.total || 0;
    } else {
      ElMessage.error(res.data.msg || '查询失败');
    }
  }).catch((error) => {
    console.error('查询失败:', error);
    ElMessage.error('查询失败，请稍后重试');
  });
};

// 加载项目列表
const loadProjectList = () => {
  getProjectList({ page: 1, pageSize: 1000 }).then((res) => {
    if (res.data.code === 200) {
      projectList.value = res.data.data;
    }
  }).catch((error) => {
    console.error('加载项目列表失败:', error);
  });
};

// 加载请求方法列表
const loadMethodList = () => {
  getMethods().then((res) => {
    if (res.data.code === 200) {
      methodList.value = res.data.data;
    }
  }).catch((error) => {
    console.error('加载请求方法失败:', error);
  });
};

// 获取项目名称
const getProjectName = (projectId) => {
  const project = projectList.value.find(p => p.id === projectId);
  return project ? project.project_name : '未知项目';
};

// 获取请求方法标签类型
const getMethodTagType = (method) => {
  const typeMap = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  };
  return typeMap[method] || '';
};

// 新增/编辑数据
const onDataForm = (index) => {
  if (index === -1) {
    // 新增
    router.push("/ApiInfoForm");
  } else {
    // 编辑
    const item = tableData.value[index];
    router.push(`/ApiInfoForm?id=${item.id}`);
  }
};

// 测试编辑器
const onTestEditor = (index) => {
  const item = tableData.value[index];
  router.push(`/ApiInfoEditor?id=${item.id}`);
};

// 查看历史
const onViewHistory = (index) => {
  const item = tableData.value[index];
  router.push(`/ApiTestHistory?api_info_id=${item.id}`);
};

// 删除数据
const onDelete = (index) => {
  const item = tableData.value[index];
  
  ElMessageBox.confirm(
    `确定要删除接口"${item.api_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteData(item.id).then((res) => {
      if (res.data.code === 200) {
        ElMessage.success('删除成功');
        loadData();
      } else {
        ElMessage.error(res.data.msg || '删除失败');
      }
    }).catch((error) => {
      console.error('删除失败:', error);
      ElMessage.error('删除失败，请稍后重试');
    });
  }).catch(() => {
    // 用户取消删除
  });
};

// 分页大小改变
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1;
  loadData();
};

// 当前页改变
const handleCurrentChange = (val) => {
  currentPage.value = val;
  loadData();
};

// 显示导入对话框
const showImportDialog = () => {
  importForm.project_id = searchForm.project_id || null;
  importForm.importType = 'url';
  importForm.swagger_url = '';
  importForm.swagger_json_text = '';
  importForm.override_existing = false;
  importDialogVisible.value = true;
};

// 执行导入
const handleImport = async () => {
  // 验证
  if (!importForm.project_id) {
    ElMessage.warning('请选择项目');
    return;
  }
  
  if (importForm.importType === 'url' && !importForm.swagger_url) {
    ElMessage.warning('请输入Swagger URL');
    return;
  }
  
  if (importForm.importType === 'json' && !importForm.swagger_json_text) {
    ElMessage.warning('请粘贴Swagger JSON内容');
    return;
  }
  
  try {
    importing.value = true;
    
    const requestData: any = {
      project_id: importForm.project_id,
      override_existing: importForm.override_existing
    };
    
    if (importForm.importType === 'url') {
      requestData.swagger_url = importForm.swagger_url;
    } else {
      try {
        requestData.swagger_json = JSON.parse(importForm.swagger_json_text);
      } catch (e) {
        ElMessage.error('JSON格式错误,请检查');
        return;
      }
    }
    
    const res = await importSwagger(requestData);
    
    if (res.data.code === 200) {
      const result = res.data.data;
      ElMessage.success(`导入完成! 成功:${result.imported_apis}, 跳过:${result.skipped_apis}, 失败:${result.failed_apis}`);
      importDialogVisible.value = false;
      loadData(); // 刷新列表
    } else {
      ElMessage.error(res.data.msg || '导入失败');
    }
  } catch (error) {
    console.error('导入失败:', error);
    ElMessage.error('导入失败: ' + (error.message || '未知错误'));
  } finally {
    importing.value = false;
  }
};

// 页面加载时执行
onMounted(() => {
  loadProjectList();
  loadMethodList();
  loadData();
});
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

/* 优化搜索表单间距 */
.search-form {
  :deep(.el-form-item) {
    margin-right: 24px;
  }
}
</style>
