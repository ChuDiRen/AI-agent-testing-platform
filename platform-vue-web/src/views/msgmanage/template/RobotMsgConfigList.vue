<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="模板名称">
        <el-input v-model="searchForm.template_name" placeholder="请输入模板名称" clearable />
      </el-form-item>
      <el-form-item label="机器人">
        <el-select v-model="searchForm.robot_id" placeholder="请选择机器人" clearable filterable>
          <el-option
            v-for="robot in robotList"
            :key="robot.id"
            :label="robot.robot_name"
            :value="robot.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="消息类型">
        <el-select v-model="searchForm.msg_type" placeholder="请选择" clearable>
          <el-option label="文本消息" value="text" />
          <el-option label="Markdown" value="markdown" />
          <el-option label="卡片消息" value="card" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.is_enabled" placeholder="请选择" clearable>
          <el-option label="已启用" :value="true" />
          <el-option label="已禁用" :value="false" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="消息模板管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      v-model:pagination="paginationModel"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增模板
        </el-button>
      </template>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="template_name" label="模板名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="robot_name" label="机器人" width="150" show-overflow-tooltip />
      <el-table-column prop="msg_type" label="消息类型" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="getMsgTypeTag(row.msg_type)">
            {{ getMsgTypeName(row.msg_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="template_content" label="模板内容" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="template-preview">
            {{ getPreviewText(row.template_content) }}
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="is_enabled" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_enabled ? 'success' : 'info'">
            {{ row.is_enabled ? '已启用' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="240">
        <template #default="{ row, $index }">
          <el-button link type="success" @click="sendTest($index)">发送测试</el-button>
          <el-button link type="primary" @click="onDataForm($index)">编辑</el-button>
          <el-button link type="danger" @click="onDelete($index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 发送测试对话框 -->
    <el-dialog v-model="sendDialogVisible" title="发送测试消息" width="600px">
      <el-form :model="sendForm" label-width="100px">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #default>
            <div>模板中的变量将使用以下测试数据替换：</div>
            <div style="margin-top: 10px; font-family: monospace; font-size: 12px;">
              {{ JSON.stringify(sendForm.variables, null, 2) }}
            </div>
          </template>
        </el-alert>

        <el-form-item label="变量数据">
          <el-input
            v-model="sendForm.variablesJson"
            type="textarea"
            :rows="8"
            placeholder='请输入JSON格式的变量数据，例如：{"name": "张三", "result": "成功"}'
          />
        </el-form-item>

        <el-form-item label="发送方式">
          <el-radio-group v-model="sendForm.sendType">
            <el-radio value="sync">同步发送（立即）</el-radio>
            <el-radio value="async">异步发送（队列）</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="sendDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSend" :loading="sendLoading">
          发送
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { queryByPage, deleteData, sendMessage, sendToRabbitMQ } from './robotMsgConfig.js';
import { queryAll as queryAllRobots } from '../robot/robotConfig.js';
import { formatDateTime } from '@/utils/timeFormatter.js';
import BaseSearch from '@/components/BaseSearch/index.vue';
import BaseTable from '@/components/BaseTable/index.vue';

const router = useRouter();

// 搜索表单
const searchForm = reactive({
  template_name: '',
  robot_id: null,
  msg_type: '',
  is_enabled: null
});

// 机器人列表
const robotList = ref([]);

// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 分页模型（适配 BaseTable）
const paginationModel = computed({
  get: () => ({ page: currentPage.value, limit: pageSize.value }),
  set: (val) => {
    currentPage.value = val.page;
    pageSize.value = val.limit;
  }
});

// 表格数据
const tableData = ref([]);
const loading = ref(false);

// 发送对话框
const sendDialogVisible = ref(false);
const sendLoading = ref(false);
const currentTemplate = ref(null);
const sendForm = ref({
  variablesJson: '{\n  "test_name": "测试用例A",\n  "test_result": "通过",\n  "test_time": "2025-11-22 15:00:00"\n}',
  variables: {},
  sendType: 'sync'
});

// 加载机器人列表
const loadRobots = () => {
  queryAllRobots().then(res => {
    if (res.data.code === 200) {
      robotList.value = res.data.data || [];
    }
  }).catch(error => {
    console.error('加载机器人列表失败:', error);
  });
};

// 加载数据
const loadData = () => {
  loading.value = true;
  const searchData = {
    ...searchForm,
    page: currentPage.value,
    pageSize: pageSize.value
  };

  queryByPage(searchData).then(res => {
    if (res.data.code === 200) {
      tableData.value = res.data.data || [];
      total.value = res.data.total || 0;
    } else {
      ElMessage.error(res.data.msg || '查询失败');
    }
  }).catch(error => {
    console.error('查询失败:', error);
    ElMessage.error('查询失败，请稍后重试');
  }).finally(() => {
    loading.value = false;
  });
};

// 重置搜索
const resetSearch = () => {
  searchForm.template_name = '';
  searchForm.robot_id = null;
  searchForm.msg_type = '';
  searchForm.is_enabled = null;
  currentPage.value = 1;
  loadData();
};

// 初始加载
onMounted(() => {
  loadRobots();
  loadData();
});

// 打开表单
const onDataForm = (index) => {
  let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index].id
    };
  }
  router.push({
    path: '/RobotMsgConfigForm',
    query: params_data
  });
};

// 删除
const onDelete = (index) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(
    `确定要删除模板"${item.template_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteData(item.id).then(res => {
      if (res.data.code === 200) {
        ElMessage.success('删除成功');
        loadData();
      } else {
        ElMessage.error(res.data.msg || '删除失败');
      }
    }).catch(error => {
      console.error('删除失败:', error);
      ElMessage.error('删除失败，请稍后重试');
    });
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// 发送测试
const sendTest = (index) => {
  currentTemplate.value = tableData.value[index];
  sendDialogVisible.value = true;
  
  // 尝试解析变量
  try {
    sendForm.value.variables = JSON.parse(sendForm.value.variablesJson);
  } catch (e) {
    // 保持默认值
  }
};

// 确认发送
const confirmSend = () => {
  // 验证JSON格式
  try {
    sendForm.value.variables = JSON.parse(sendForm.value.variablesJson);
  } catch (e) {
    ElMessage.error('变量数据格式错误，请输入有效的JSON');
    return;
  }

  sendLoading.value = true;
  const requestData = {
    template_id: currentTemplate.value.id,
    variables: sendForm.value.variables
  };

  const apiCall = sendForm.value.sendType === 'sync' 
    ? sendMessage(requestData) 
    : sendToRabbitMQ(requestData);

  apiCall.then(res => {
    sendLoading.value = false;
    if (res.data.code === 200) {
      ElMessage.success(
        sendForm.value.sendType === 'sync' 
          ? '消息发送成功！' 
          : '消息已加入发送队列！'
      );
      sendDialogVisible.value = false;
    } else {
      ElMessage.error(res.data.msg || '发送失败');
    }
  }).catch(error => {
    sendLoading.value = false;
    console.error('发送失败:', error);
    ElMessage.error('发送失败，请稍后重试');
  });
};

// 辅助方法
const getMsgTypeName = (type) => {
  const map = {
    text: '文本',
    markdown: 'Markdown',
    card: '卡片'
  };
  return map[type] || type;
};

const getMsgTypeTag = (type) => {
  const map = {
    text: '',
    markdown: 'success',
    card: 'warning'
  };
  return map[type] || '';
};

const getPreviewText = (content) => {
  if (!content) return '-';
  return content.length > 50 ? content.substring(0, 50) + '...' : content;
};
</script>

<style scoped>
@import '~/styles/common-list.css';

.template-preview {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
</style>
