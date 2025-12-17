<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch 
      :model="searchForm" 
      @search="handleSearch" 
      @reset="resetSearch"
    >
      <el-form-item label="项目名称">
        <el-input v-model="searchForm.project_name" placeholder="请输入项目名称" clearable />
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable 
      title="项目管理"
      :data="tableData" 
      :total="total" 
      :loading="loading"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增项目
        </el-button>
      </template>

      <el-table-column prop="id" label="项目编号" width="100" />
      <el-table-column prop="project_name" label="项目名称" show-overflow-tooltip />
      <el-table-column prop="project_desc" label="项目描述" show-overflow-tooltip />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="220">
        <template #default="scope">
          <el-button link type="primary" @click.prevent="onDataForm(scope.$index)">编辑</el-button>
          <el-button link type="primary" @click.prevent="showDbBaseManage(scope.$index)">数据库配置</el-button>
          <el-button link type="danger" @click.prevent="onDelete(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 弹窗 - 数据库配置 -->
    <el-dialog 
      v-model="DbBaseManageDialogFormVisible" 
      title="数据库配置管理" 
      width="90%" 
      :close-on-click-modal="false"
      class="db-config-dialog"
    >
      <!-- 已配置的数据库列表 -->
      <div class="db-list-section">
        <h4 class="section-title">已配置数据库</h4>
        <el-table 
          :data="DbBaseManageList" 
          style="width: 100%" 
          max-height="350"
          :empty-text="'暂无数据库配置，请在下方添加'"
        >
          <el-table-column prop="name" label="连接名" width="120" />
          <el-table-column prop="ref_name" label="引用变量" width="140" :show-overflow-tooltip="true" />
          <el-table-column prop="db_info" label="数据库连接信息" min-width="300" :show-overflow-tooltip="true" />
          <el-table-column prop="db_type" label="数据库类型" width="120" align="center" />
          <el-table-column prop="is_enabled" label="状态" width="100" align="center">
            <template #default="scope">
              <el-tag :type="scope.row.is_enabled === '1' ? 'success' : 'info'" size="small">
                {{ scope.row.is_enabled === "1" ? '已启用' : '已禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="scope">
              <el-button 
                link 
                :type="scope.row.is_enabled === '1' ? 'warning' : 'success'" 
                size="small" 
                @click.prevent="upDataDbinfo(scope.$index)"
              >
                {{ scope.row.is_enabled === '1' ? '禁用' : '启用' }}
              </el-button>
              <el-button link type="danger" size="small" @click.prevent="onDeleteDb(scope.$index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 添加新数据库配置 -->
      <div class="db-form-section">
        <h4 class="section-title">添加数据库配置</h4>
        <el-form :model="ruleForm" label-width="120px" label-position="right">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="连接名" required>
                <el-input 
                  v-model="ruleForm.name" 
                  placeholder="请输入连接名称，如：测试库" 
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="引用变量" required>
                <el-input 
                  v-model="ruleForm.ref_name" 
                  placeholder="请输入引用变量，如：test_db" 
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="数据库类型" required>
                <el-select 
                  v-model="ruleForm.db_type" 
                  placeholder="请选择数据库类型" 
                  style="width: 100%"
                  clearable
                >
                  <el-option v-for="item in optionsDbType" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="是否启用" required>
                <el-select 
                  v-model="ruleForm.is_enabled" 
                  placeholder="请选择是否启用" 
                  style="width: 100%"
                  clearable
                >
                  <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="数据库连接信息" required>
            <el-input 
              v-model="ruleForm.db_info" 
              type="textarea"
              :rows="3"
              placeholder='请输入数据库连接信息（JSON格式），例如：&#10;{&#10;  "host": "127.0.0.1",&#10;  "port": 3306,&#10;  "username": "root",&#10;  "password": "password",&#10;  "database": "test_db"&#10;}' 
              clearable
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="onAddDbinfo" :icon="Plus">
              添加配置
            </el-button>
            <el-button @click="resetForm">
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="DbBaseManageDialogFormVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>
  
<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { queryByPage, deleteData } from "./apiProject.js";
import { formatDateTime } from '~/utils/timeFormatter';
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import BaseTable from '~/components/BaseTable/index.vue';
import BaseSearch from '~/components/BaseSearch/index.vue';

const router = useRouter(); 

// 分页参数
const pagination = ref({ page: 1, limit: 10 });
const total = ref(0);
const loading = ref(false);

// 搜索表单
const searchForm = reactive({
  project_name: null as string | null
});

// 表格数据
const tableData = ref([]);

// 加载页面数据
const loadData = () => {
  loading.value = true;
  const params: any = {
    page: pagination.value.page,
    pageSize: pagination.value.limit
  };
  // 添加搜索条件
  if (searchForm.project_name) {
    params.project_name = searchForm.project_name;
  }
  
  queryByPage(params).then((res: { data: { code: number; data: never[]; total: number; msg: string } }) => {
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

// 搜索
const handleSearch = () => {
  pagination.value.page = 1; // 搜索时重置到第一页
  loadData();
};

// 重置搜索
const resetSearch = () => {
  searchForm.project_name = null;
  pagination.value.page = 1;
  loadData();
};

// 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
  let params_data = {};
  if (index >= 0) {
    params_data = { id: tableData.value[index]["id"] };
  }
  router.push({ path: "/ApiProjectForm", query: params_data });
};

// 删除项目
const onDelete = (index: number) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(`确定要删除项目"${item.project_name}"吗？`, '删除确认', {
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


// ---------------------扩展：数据库展示弹窗-------------------------------

// 11. 增加功能：数据库相关的操作
import { queryByPage as queryByPageList } from "./dbBase.js"; // 不同页面不同的接口
import { updateData } from "./dbBase.js"; // 不同页面不同的接口
import { insertData } from "./dbBase.js"; // 不同页面不同的接口
import { deleteData as deleteDbData } from "./dbBase.js"; // 不同页面不同的接口

const DbBaseManageList = ref([] as any[]); // 数据库数据列表数据
const currentApiHistoryPage = ref(1) // 页码
const DbBaseManageDialogFormVisible = ref(false) // 是否展示弹窗
const currentProjectId = ref(0) // 当前展示的执行记录关联的 ProjectId


// 11-1 显示当前弹窗信息
const showDbBaseManage = (index: number) => {
    DbBaseManageDialogFormVisible.value = true
    currentProjectId.value = tableData.value[index]["id"]
    loadDbBaseManage(currentProjectId.value)
}

// 11-2 加载当中项目的数据
const loadDbBaseManage = (index: number) => {
    let searchData = {}
    searchData["project_id"] = index
    searchData["page"] = currentApiHistoryPage.value
    searchData["pageSize"] = 100
    queryByPageList(searchData).then((res: { data: { data: never[]; total: number; msg: string } }) => {
        DbBaseManageList.value = res.data.data
    })
}

// 11-3 数据库信息-提交表单-表单数据
const ruleForm =reactive({
  id:0,
  project_id: currentProjectId.value,
  name: "",
  db_info:"",
  ref_name:"",
  db_type: "",
  is_enabled:"1", // 默认值 1
}); 

// 11-4 下拉列表的值-是否启动
const options = [
  {
    value: '1',
    label: '是',
  },
  {
    value: '0',
    label: '否',
  }
]

// 11-5 下拉列表的值-数据库类型
const optionsDbType = [
  {
    value: 'Mysql',
    label: 'Mysql',
  },
  {
    value: 'Oracle',
    label: 'Oracle',
  }
]


// 11-6  添加-数据库数据
const onAddDbinfo = (index: number) => {
  // 验证必填字段
  if (!ruleForm.name || !ruleForm.ref_name || !ruleForm.db_info || !ruleForm.db_type) {
    ElMessage.warning('请填写所有必填字段');
    return;
  }

  // 验证 JSON 格式
  try {
    JSON.parse(ruleForm.db_info);
  } catch (e) {
    ElMessage.error('数据库连接信息格式错误，请输入有效的 JSON 格式');
    return;
  }

  // 添加数据的时候，设置项目对应的值
  ruleForm.project_id = currentProjectId.value;

  insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
    if (res.data.code == 200) {
      ElMessage.success('数据库配置添加成功');
      loadDbBaseManage(currentProjectId.value);
      resetForm(); // 重置表单
    } else {
      ElMessage.error(res.data.msg || '添加失败');
    }
  }).catch((error: any) => {
    console.error('添加失败:', error);
    ElMessage.error('添加失败，请稍后重试');
  });
};

// 重置表单
const resetForm = () => {
  ruleForm.name = "";
  ruleForm.ref_name = "";
  ruleForm.db_info = "";
  ruleForm.is_enabled = "1";
  ruleForm.db_type = "";
};

// 11-7 修改-数据库数据
// 修改的变量
const UpDataruleForm =reactive({
  id:0,
  project_id: currentProjectId.value,
  name: "",
  db_info:"",
  ref_name:"",
  db_type: "",
  is_enabled:"1", // 默认值 1
}); 

// 修改的方法
const upDataDbinfo = (index: number) => {
  const dbItem = DbBaseManageList.value[index];
  const newStatus = dbItem.is_enabled === '1' ? '0' : '1';
  const action = newStatus === '1' ? '启用' : '禁用';

  UpDataruleForm.id = dbItem.id;
  UpDataruleForm.project_id = dbItem.project_id;
  UpDataruleForm.name = dbItem.name;
  UpDataruleForm.ref_name = dbItem.ref_name;
  UpDataruleForm.db_info = dbItem.db_info;
  UpDataruleForm.db_type = dbItem.db_type;
  UpDataruleForm.is_enabled = newStatus;
    
  updateData(UpDataruleForm).then((res: { data: { code: number; msg: string; }; }) => {
    if (res.data.code == 200) {
      ElMessage.success(`${action}成功`);
      loadDbBaseManage(currentProjectId.value);
    } else {
      ElMessage.error(res.data.msg || `${action}失败`);
    }
  }).catch((error: any) => {
    console.error(`${action}失败:`, error);
    ElMessage.error(`${action}失败，请稍后重试`);
  });
};

// 11-8 删除数据库
const onDeleteDb = (index: number) => {
  const dbItem = DbBaseManageList.value[index];
  ElMessageBox.confirm(
    `确定要删除数据库配置"${dbItem.name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteDbData(dbItem.id).then((res: { data: { code: number; msg: string } }) => {
      if (res.data?.code == 200 || res) {
        ElMessage.success('删除成功');
        loadDbBaseManage(currentProjectId.value);
      }
    }).catch((error: any) => {
      console.error('删除失败:', error);
      ElMessage.error('删除失败，请稍后重试');
    });
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// ---------------------  END扩展：数据库展示弹窗-------------------------------
</script>
  
<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

/* 数据库配置对话框样式 */
.db-config-dialog :deep(.el-dialog__body) {
  padding: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

/* 列表区域 */
.db-list-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

/* 表单区域 */
.db-form-section {
  padding: 20px;
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

/* 区块标题 */
.section-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  border-left: 4px solid #409eff;
  padding-left: 12px;
}

/* 优化表单项间距 */
.db-form-section :deep(.el-form-item) {
  margin-bottom: 20px;
}

/* 优化按钮样式 */
.db-form-section :deep(.el-button) {
  min-width: 100px;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .db-config-dialog {
    width: 95% !important;
  }
  
  .db-list-section,
  .db-form-section {
    padding: 12px;
  }
}
</style>
