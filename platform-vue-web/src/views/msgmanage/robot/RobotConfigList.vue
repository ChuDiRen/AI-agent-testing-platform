<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="机器人名称">
        <el-input v-model="searchForm.robot_name" placeholder="请输入机器人名称" clearable />
      </el-form-item>
      <el-form-item label="机器人类型">
        <el-select v-model="searchForm.robot_type" placeholder="请选择" clearable>
          <el-option label="企业微信" value="wechat" />
          <el-option label="钉钉" value="dingtalk" />
          <el-option label="飞书" value="feishu" />
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
      title="机器人配置管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      v-model:pagination="paginationModel"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增机器人
        </el-button>
      </template>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="robot_name" label="机器人名称" show-overflow-tooltip />
      <el-table-column prop="robot_type" label="类型" width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="getRobotTypeTag(row.robot_type)">
            {{ getRobotTypeName(row.robot_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="webhook_url" label="Webhook地址" min-width="200" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_enabled"
            @change="handleToggleEnabled(row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="last_test_time" label="最后测试时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.last_test_time) || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="220">
        <template #default="{ row, $index }">
          <el-button link type="primary" @click="testRobot($index)">测试</el-button>
          <el-button link type="primary" @click="onDataForm($index)">编辑</el-button>
          <el-button link type="danger" @click="onDelete($index)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { queryByPage, deleteData, testConnection, toggleEnabled } from './robotConfig.js';
import { formatDateTime } from '@/utils/timeFormatter.js';
import BaseSearch from '@/components/BaseSearch/index.vue';
import BaseTable from '@/components/BaseTable/index.vue';

const router = useRouter();

// 搜索表单
const searchForm = reactive({
  robot_name: '',
  robot_type: '',
  is_enabled: null
});

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
  searchForm.robot_name = '';
  searchForm.robot_type = '';
  searchForm.is_enabled = null;
  currentPage.value = 1;
  loadData();
};

// 初始加载
loadData();

// 打开表单
const onDataForm = (index) => {
  let params_data = {};
  if (index >= 0) {
    params_data = {
      id: tableData.value[index].id
    };
  }
  router.push({
    path: '/RobotConfigForm',
    query: params_data
  });
};

// 删除
const onDelete = (index) => {
  const item = tableData.value[index];
  ElMessageBox.confirm(
    `确定要删除机器人"${item.robot_name}"吗？`,
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

// 测试机器人连接
const testRobot = (index) => {
  const item = tableData.value[index];
  const loading = ElMessage({
    message: '正在测试连接...',
    type: 'info',
    duration: 0
  });

  testConnection({
    robot_id: item.id,
    test_message: '这是一条测试消息，来自AI Agent Testing Platform'
  }).then(res => {
    loading.close();
    if (res.data.code === 200) {
      const result = res.data.data;
      ElMessage.success(`连接测试成功！响应时间: ${result.response_time}ms`);
      loadData(); // 刷新最后测试时间
    } else {
      ElMessage.error(res.data.msg || '测试失败');
    }
  }).catch(error => {
    loading.close();
    console.error('测试失败:', error);
    ElMessage.error('测试失败，请检查配置');
  });
};

// 辅助方法
const getRobotTypeName = (type) => {
  const map = {
    wechat: '企业微信',
    dingtalk: '钉钉',
    feishu: '飞书'
  };
  return map[type] || type;
};

const getRobotTypeTag = (type) => {
  const map = {
    wechat: 'success',
    dingtalk: 'primary',
    feishu: 'warning'
  };
  return map[type] || '';
};

// 启用/禁用机器人
const handleToggleEnabled = async (row) => {
  try {
    const res = await toggleEnabled(row.id, row.is_enabled);
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '操作成功');
    } else {
      ElMessage.error(res.data.msg || '操作失败');
      row.is_enabled = !row.is_enabled;
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message);
    row.is_enabled = !row.is_enabled;
  }
};
</script>

<style scoped>
@import '~/styles/common-list.css';
</style>
