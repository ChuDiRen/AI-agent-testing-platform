<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
      <!-- 面包屑导航 -->
      <Breadcrumb />
      <!-- 搜索表单 -->
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-row class="mb-4" type="flex" justify="end">
          <el-button type="warning" @click="onDataForm(-1)">新增项目</el-button>
        </el-row>
      </el-form>
      <!-- END搜索表单 -->

      <!-- 数据表格 -->
      <el-table :data="tableData" style="width: 100%" max-height="500">
        <!-- 数据列 -->
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop" :show-overflow-tooltip="true" />
        <!-- END数据列 -->

        <!-- 操作 -->
        <el-table-column fixed="right" label="操作">
          <template #default="scope">
            <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click.prevent="showDbBaseManage(scope.$index)">
              数据库配置
            </el-button>
            <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <!-- END操作 -->
      <!-- END 数据表格 -->

      <!-- 分页 -->
      <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      <!-- END 分页 -->

      <!-- 弹窗 - 增加功能：数据库配置 弹窗加载执行记录 -->
      <el-dialog v-model="DbBaseManageDialogFormVisible" style="width: 1100px">
        <el-form-item>
          <!-- 数据库数据信息显示 -->
          <el-table :data="DbBaseManageList" style="width: 100%" max-height="300">
            <el-table-column prop="name" label="连接名" style="width: 10%" />
            <el-table-column prop="ref_name" label="引用变量" style="width: 20%" :show-overflow-tooltip="true" />
            <el-table-column prop="db_info" label="数据库连接信息" style="width: 40%" :show-overflow-tooltip="true" />
            <el-table-column prop="is_enabled" label="是否启用" style="width: 10%" :show-overflow-tooltip="true">
              <template #default="scope">
                {{ scope.row.is_enabled === true ? '是' : scope.row.is_enabled === false ? '否' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="db_type" label="数据库类型" style="width: 10%" :show-overflow-tooltip="true" />
            
            <el-table-column label="操作" style="width: 5%" :show-overflow-tooltip="true">
              <el-button link type="primary" size="small" @click.prevent="upDataDbinfo(scope.$index)">修改是否启动</el-button>
              <el-button link type="primary" size="small" @click.prevent="onDeleteDb(scope.$index)">删除</el-button>
            </el-table-column>
          </el-table>

          <!-- 数据库添加数据信息 -->
          <div class="input-group" style="width: 100%">
            <el-input v-model="dbRuleForm.name" placeholder="连接名" style="width: 15%"/>
            <el-input v-model="dbRuleForm.ref_name" placeholder="引用变量" style="width: 15%"/>
            <el-input v-model="dbRuleForm.db_info" placeholder="数据库连接信息，如：{host: 主机IP/服务器, port: 端口号, username: 用户名, password: 密码, database: 数据库名}" style="width: 30%"/>
            <el-select v-model="dbRuleForm.is_enabled" placeholder="是否启用" style="width: 20%">
              <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-select v-model="dbRuleForm.db_type" placeholder="数据库类型" style="width: 10%">
              <el-option v-for="item in optionsDbType" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
            <el-button style="width: 10%" type="primary" @click="onAddDbinfo">添加</el-button>
          </div> 
        </el-form-item>
      </el-dialog>
    </div>

    <!-- 表单视图 -->
    <div v-else>
      <!-- 面包屑导航 -->
      <Breadcrumb />
      <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="项目编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="project_name" prop="project_name">
          <el-input v-model="ruleForm.project_name" placeholder="请输入项目名称"/>
        </el-form-item>
        <el-form-item label="project_desc" prop="project_desc">
          <el-input v-model="ruleForm.project_desc" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
          <el-button @click="resetForm(ruleFormRef)">清空</el-button>
          <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue";

// API接口
import { queryByPage, deleteData, queryById, insertData, updateData } from "@/api/ApiProject";
import { queryByPage as queryByPageList, updateData as updateDbData, insertData as insertDbData, deleteData as deleteDbData } from "@/api/DbBaseManage.js";

const router = useRouter();
const { confirmDelete } = useDeleteConfirm();

// 视图控制
const currentView = ref('list')

// ========== 列表相关数据 ==========
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const searchForm = reactive({});

const columnList = ref([
  { prop: "id", label: "项目编号" },
  { prop: "project_name", label: "项目名称" },
  { prop: "project_desc", label: "项目描述" },
  { prop: "created_at", label: "创建时间" },
  { prop: "updated_at", label: "更新时间" },
]);

const tableData = ref([]);

const loadData = () => {
  let searchData = searchForm;
  searchData["page"] = currentPage.value;
  searchData["pageSize"] = pageSize.value;

  queryByPage(searchData).then((res) => {
    tableData.value = res.data.data;
    total.value = res.data.total;
  });
};

const handleSizeChange = (val) => {
  pageSize.value = val;
  loadData();
};

const handleCurrentChange = (val) => {
  currentPage.value = val;
  loadData();
};

const onDataForm = (index) => {
  currentView.value = 'form'
  if (index >= 0) {
    loadFormData(tableData.value[index]["id"])
  } else {
    resetForm()
  }
}

const onDelete = async (index) => {
  const projectId = tableData.value[index]["id"];
  const projectName = tableData.value[index]["project_name"];
  
  await confirmDelete(
    () => deleteData(projectId),
    `确定要删除项目 "${projectName}" 吗？此操作不可恢复！`,
    '项目删除成功',
    loadData
  );
};

// ========== 表单相关数据 ==========
const ruleFormRef = ref();
const ruleForm = reactive({
  id: 0,
  project_name: '',
  project_desc: ''
});

const rules = reactive({
  project_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  project_desc: [
    { required: true, message: '必填项', trigger: 'blur' }
  ]
});

const loadFormData = async (id) => {
  const res = await queryById(id);
  ruleForm.id = res.data.data.id;
  ruleForm.project_name = res.data.data.project_name;
  ruleForm.project_desc = res.data.data.project_desc;
};

const resetForm = () => {
  ruleForm.id = 0;
  ruleForm.project_name = '';
  ruleForm.project_desc = '';
};

const submitForm = async (form) => {
  if (!form) return;
  await form.validate((valid, fields) => {
    if (!valid) return;
    
    if (ruleForm.id > 0) {
      updateData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('更新成功')
          currentView.value = 'list'
          loadData()
        }
      });
    } else {
      insertData(ruleForm).then((res) => {
        if (res.data.code == 200) {
          Message.success('添加成功')
          currentView.value = 'list'
          loadData()
        }
      });
    }
  });
};

const resetFormFields = (form) => {
  if (!form) return;
  form.resetFields();
};

const closeForm = () => {
  currentView.value = 'list'
  loadData()
};

// ========== 数据库配置相关 ==========
const DbBaseManageList = ref([]);
const currentApiHistoryPage = ref(1)
const DbBaseManageDialogFormVisible = ref(false)
const currentProjectId = ref(0)

const showDbBaseManage = (index) => {
  DbBaseManageDialogFormVisible.value = true
  currentProjectId.value = tableData.value[index]["id"]
  loadDbBaseManage(currentProjectId.value)
}

const loadDbBaseManage = (index) => {
  let searchData = {}
  searchData["project_id"] = index
  searchData["page"] = currentApiHistoryPage.value
  searchData["pageSize"] = 100
  queryByPageList(searchData).then((res) => {
    DbBaseManageList.value = res.data.data
  })
}

const dbRuleForm = reactive({
  id: 0,
  project_id: currentProjectId.value,
  name: "",
  db_info: "",
  ref_name: "",
  db_type: "",
  is_enabled: true,
});

const options = [
  { value: true, label: '是' },
  { value: false, label: '否' }
]

const optionsDbType = [
  { value: 'Mysql', label: 'Mysql' },
  { value: 'Oracle', label: 'Oracle' }
]

const onAddDbinfo = () => {
  dbRuleForm.project_id = currentProjectId.value
  insertDbData(dbRuleForm).then((res) => {
    if (res.data.code == 200) {
      loadDbBaseManage(currentProjectId.value)
      dbRuleForm.name = ""
      dbRuleForm.ref_name = ""
      dbRuleForm.db_info = ""
      dbRuleForm.is_enabled = true
      dbRuleForm.db_type = ""
    }
  });
};

const upDataDbinfo = (index) => {
  const updateData = {
    id: DbBaseManageList.value[index].id,
    project_id: DbBaseManageList.value[index].project_id,
    name: DbBaseManageList.value[index].name,
    ref_name: DbBaseManageList.value[index].ref_name,
    db_info: DbBaseManageList.value[index].db_info,
    db_type: DbBaseManageList.value[index].db_type,
    is_enabled: !DbBaseManageList.value[index].is_enabled,
  }
  
  updateDbData(updateData).then((res) => {
    if (res.data.code == 200) {
      loadDbBaseManage(currentProjectId.value)
    }
  });
};

const onDeleteDb = async (index) => {
  const dbId = DbBaseManageList.value[index]["id"];
  const dbName = DbBaseManageList.value[index]["name"];
  
  await confirmDelete(
    () => deleteDbData(dbId),
    `确定要删除数据库配置 "${dbName}" 吗？`,
    '数据库配置删除成功',
    () => loadDbBaseManage(currentProjectId.value)
  );
};

// ========== 初始化 ==========
loadData()
</script>

<style scoped>
.demo-pagination-block .demo-pagination-block {
  margin-top: 10px;
}
.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}
.input-group {
  margin-top: 16px;
}
</style>
