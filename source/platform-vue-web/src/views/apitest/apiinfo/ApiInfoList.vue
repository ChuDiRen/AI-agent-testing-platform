<template>
  <div class="api-info-container">
    <h2>接口信息管理</h2>
    
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="项目：">
        <el-select v-model="searchForm.project_id" placeholder="选择项目" clearable style="width: 200px">
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id"/>     
        </el-select>
      </el-form-item>
      
      <el-form-item label="接口名称：">
        <el-input v-model="searchForm.api_name" placeholder="根据接口名称筛选" style="width: 200px"/>
      </el-form-item>
      
      <el-form-item label="请求方法：">
        <el-select v-model="searchForm.request_method" placeholder="选择请求方法" clearable style="width: 150px">
          <el-option v-for="method in methodList" :key="method" :label="method" :value="method"/>     
        </el-select>
      </el-form-item>
      
      <el-form-item label="接口分组：">
        <el-select v-model="searchForm.group_id" placeholder="选择分组" clearable style="width: 200px">
          <el-option label="未分组" :value="0"/>
          <el-option v-for="group in groupList" :key="group.id" :label="group.group_name" :value="group.id"/>     
        </el-select>
      </el-form-item>
      
      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增接口</el-button>
      </el-row>
    </el-form>
    <!-- END 搜索表单 -->

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%" max-height="500">
      <el-table-column prop="id" label="接口编号" width="80" show-overflow-tooltip />
      <el-table-column prop="api_name" label="接口名称" width="200" show-overflow-tooltip />
      <el-table-column prop="request_method" label="请求方法" width="100">
        <template #default="scope">
          <el-tag :type="getMethodTagType(scope.row.request_method)">
            {{ scope.row.request_method }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="request_url" label="请求地址" min-width="300" show-overflow-tooltip />
      <el-table-column prop="project_id" label="所属项目" width="120">
        <template #default="scope">
          {{ getProjectName(scope.row.project_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180" show-overflow-tooltip>
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
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { queryByPage, deleteData, getMethods } from './apiinfo.js';
import { queryByPage as getProjectList } from '../project/ApiProject.js';
import { queryGroupByPage } from '../apigroup/apiGroup.js';
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
  request_method: null,
  group_id: null
});

// 表格数据
const tableData = ref([]);

// 项目列表
const projectList = ref([]);

// 分组列表
const groupList = ref([]);

// 请求方法列表
const methodList = ref([]);

// 加载页面数据
const loadData = () => {
  let searchData = {
    ...searchForm,
    page: currentPage.value,
    pageSize: pageSize.value
  };
  
  queryByPage(searchData).then((res) => {
    if (res.data.code === 200) {
      tableData.value = res.data.data;
      total.value = res.data.total;
      ElMessage.success('查询成功');
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

// 加载分组列表
const loadGroupList = () => {
  queryGroupByPage({ page: 1, pageSize: 1000 }).then((res) => {
    if (res.data.code === 200) {
      groupList.value = res.data.data || [];
    }
  }).catch((error) => {
    console.error('加载分组列表失败:', error);
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

// 页面加载时执行
onMounted(() => {
  loadProjectList();
  loadMethodList();
  loadGroupList();
  loadData();
});
</script>

<style scoped>
.api-info-container {
  padding: 20px;
}

.demo-pagination-block {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
