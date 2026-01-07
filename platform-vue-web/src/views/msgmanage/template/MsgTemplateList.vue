<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="loadData" @reset="resetSearch">
      <el-form-item label="模板编码">
        <el-input v-model="searchForm.template_code" placeholder="请输入模板编码" clearable />
      </el-form-item>
      <el-form-item label="模板名称">
        <el-input v-model="searchForm.template_name" placeholder="请输入模板名称" clearable />
      </el-form-item>
      <el-form-item label="模板类型">
        <el-select v-model="searchForm.template_type" placeholder="请选择" clearable>
          <el-option
            v-for="type in templateTypes"
            :key="type.value"
            :label="type.label"
            :value="type.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="渠道类型">
        <el-select v-model="searchForm.channel_type" placeholder="请选择" clearable>
          <el-option
            v-for="channel in channelTypes"
            :key="channel.value"
            :label="channel.label"
            :value="channel.value"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="请选择" clearable>
          <el-option label="已启用" :value="1" />
          <el-option label="已禁用" :value="0" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="消息模板管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      :pagination="paginationModel"
      @update:pagination="paginationModel = $event"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="onAdd">
          <el-icon><Plus /></el-icon>
          新增模板
        </el-button>
      </template>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="template_code" label="模板编码" width="180" show-overflow-tooltip />
      <el-table-column prop="template_name" label="模板名称" width="150" show-overflow-tooltip />
      <el-table-column prop="template_type" label="类型" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getTypeTag(row.template_type)">
            {{ getTypeName(row.template_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="channel_type" label="渠道" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getChannelTag(row.channel_type)" effect="plain">
            {{ getChannelName(row.channel_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" width="150" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="content-preview">{{ row.content }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.status"
            :active-value="1"
            :inactive-value="0"
            @change="handleStatusChange(row)"
          />
        </template>
      </el-table-column>
      <el-table-column prop="created_time" label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_time) }}
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="220">
        <template #default="{ row }">
          <el-button link type="primary" @click="onPreview(row)">预览</el-button>
          <el-button link type="primary" @click="onEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="模板预览"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="模板名称">{{ currentTemplate.template_name }}</el-descriptions-item>
        <el-descriptions-item label="模板编码">{{ currentTemplate.template_code }}</el-descriptions-item>
        <el-descriptions-item label="变量列表">
          <el-tag
            v-for="(variable, index) in currentTemplate.variables"
            :key="index"
            size="small"
            style="margin-right: 5px; margin-bottom: 5px"
          >
            {{ '{' + '{' + variable.name + '}' + '}' + ': ' + variable.desc }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="示例参数">
          <pre class="json-preview">{{ JSON.stringify(currentTemplate.example_params, null, 2) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="替换后标题">
          <div class="preview-content">{{ previewData.title }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="替换后内容">
          <pre class="preview-content">{{ previewData.content }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import {
  queryByPage,
  deleteData,
  updateData,
  previewTemplate,
  getTemplateTypes,
  getChannelTypes
} from './template.js';
import { formatDateTime } from '~/utils/timeFormatter.js';
import BaseSearch from '~/components/BaseSearch/index.vue';
import BaseTable from '~/components/BaseTable/index.vue';

const router = useRouter();

// 搜索表单
const searchForm = reactive({
  template_code: '',
  template_name: '',
  template_type: '',
  channel_type: '',
  status: null
});

// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 分页模型
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

// 模板类型和渠道类型
const templateTypes = ref([]);
const channelTypes = ref([]);

// 预览相关
const previewVisible = ref(false);
const currentTemplate = ref({});
const previewData = ref({
  title: '',
  content: ''
});

// 加载类型和渠道数据
const loadTypesAndChannels = async () => {
  try {
    const [typesRes, channelsRes] = await Promise.all([
      getTemplateTypes(),
      getChannelTypes()
    ]);

    if (typesRes.data.code === 200) {
      templateTypes.value = typesRes.data.data || [];
    }
    if (channelsRes.data.code === 200) {
      channelTypes.value = channelsRes.data.data || [];
    }
  } catch (error) {
    console.error('加载类型数据失败:', error);
  }
};

// 加载数据
const loadData = () => {
  loading.value = true;
  const searchData = {
    ...searchForm,
    page: currentPage.value,
    page_size: pageSize.value
  };

  queryByPage(searchData).then(res => {
    if (res.data.code === 200) {
      tableData.value = res.data.data?.list || [];
      total.value = res.data.data?.total || 0;
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
  searchForm.template_code = '';
  searchForm.template_name = '';
  searchForm.template_type = '';
  searchForm.channel_type = '';
  searchForm.status = null;
  currentPage.value = 1;
  loadData();
};

// 新增模板
const onAdd = () => {
  router.push({ path: '/MsgTemplateForm' });
};

// 编辑模板
const onEdit = (row) => {
  router.push({
    path: '/MsgTemplateForm',
    query: { id: row.id }
  });
};

// 删除模板
const onDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除模板"${row.template_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deleteData(row.id).then(res => {
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

// 预览模板
const onPreview = async (row) => {
  currentTemplate.value = row;
  try {
    const res = await previewTemplate({
      template_code: row.template_code,
      params: row.example_params || {}
    });
    if (res.data.code === 200) {
      previewData.value = res.data.data;
      previewVisible.value = true;
    } else {
      ElMessage.error(res.data.msg || '预览失败');
    }
  } catch (error) {
    console.error('预览失败:', error);
    ElMessage.error('预览失败，请稍后重试');
  }
};

// 状态切换
const handleStatusChange = async (row) => {
  try {
    const res = await updateData({
      id: row.id,
      status: row.status
    });
    if (res.data.code === 200) {
      ElMessage.success(row.status === 1 ? '已启用' : '已禁用');
    } else {
      ElMessage.error(res.data.msg || '操作失败');
      row.status = row.status === 1 ? 0 : 1;
    }
  } catch (error) {
    console.error('状态切换失败:', error);
    ElMessage.error('操作失败，请稍后重试');
    row.status = row.status === 1 ? 0 : 1;
  }
};

// 辅助方法
const getTypeName = (type) => {
  const item = templateTypes.value.find(t => t.value === type);
  return item?.label || type;
};

const getTypeTag = (type) => {
  const map = {
    verify: 'success',
    notify: 'primary',
    marketing: 'warning',
    warning: 'danger',
    system: 'info'
  };
  return map[type] || '';
};

const getChannelName = (channel) => {
  const item = channelTypes.value.find(c => c.value === channel);
  return item?.label || channel;
};

const getChannelTag = (channel) => {
  const map = {
    system: '',
    email: 'success',
    sms: 'warning',
    wechat: 'primary',
    dingtalk: 'danger'
  };
  return map[channel] || '';
};

// 初始化
onMounted(() => {
  loadTypesAndChannels();
  loadData();
});
</script>

<style scoped>
.content-preview {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.json-preview {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  margin: 0;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.preview-content {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
}
</style>
