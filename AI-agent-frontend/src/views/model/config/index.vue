<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives, computed } from 'vue'
import {
  NButton,
  NTag,
  NSpace,
  NPopconfirm,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NInputNumber,
  NDropdown,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import { formatDate, renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: 'AI模型配置' })

const vPermission = resolveDirective('permission')
const $table = ref(null)
const queryItems = ref({})
const selectedRowKeys = ref([])

// 是否有选中项
const hasSelected = computed(() => selectedRowKeys.value.length > 0)

const {
  modalVisible,
  modalTitle,
  modalAction,
  modalLoading,
  handleSave,
  modalForm,
  modalFormRef,
  handleEdit,
  handleDelete,
  handleAdd,
} = useCRUD({
  name: '模型',
  initForm: {
    name: '',
    display_name: '',
    provider: 'openai',
    model_type: 'chat',
    version: '',
    description: '',
    api_endpoint: '',
    api_key: '',
    max_tokens: 4096,
    temperature: 0.7,
  },
  doCreate: api.createModel,
  doUpdate: (data) => api.updateModel(data.id, data),
  doDelete: api.deleteModel,
  refresh: () => $table.value?.handleSearch(),
})

const providerOptions = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Anthropic', value: 'anthropic' },
  { label: 'DeepSeek', value: 'deepseek' },
  { label: '千问', value: 'qianwen' },
  { label: '百度', value: 'baidu' },
  { label: 'Google', value: 'google' },
  { label: '自定义', value: 'custom' },
]

const modelTypeOptions = [
  { label: '聊天模型', value: 'chat' },
  { label: '补全模型', value: 'completion' },
  { label: '嵌入模型', value: 'embedding' },
  { label: '图像模型', value: 'image' },
  { label: '音频模型', value: 'audio' },
  { label: '多模态', value: 'multimodal' },
]

const statusOptions = [
  { label: '激活', value: 'active' },
  { label: '未激活', value: 'inactive' },
  { label: '已弃用', value: 'deprecated' },
  { label: '维护中', value: 'maintenance' },
]

const statusTagType = {
  active: 'success',
  inactive: 'default',
  deprecated: 'warning',
  maintenance: 'info',
}

// 批量操作选项
const batchOptions = [
  {
    label: '批量激活',
    key: 'activate',
    icon: renderIcon('material-symbols:check-circle', { size: 18 }),
  },
  {
    label: '批量停用',
    key: 'deactivate',
    icon: renderIcon('material-symbols:cancel', { size: 18 }),
  },
  {
    label: '批量删除',
    key: 'delete',
    icon: renderIcon('material-symbols:delete-outline', { size: 18 }),
  },
]

const columns = [
  {
    type: 'selection',
  },
  {
    title: '模型名称',
    key: 'name',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '显示名称',
    key: 'display_name',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '提供商',
    key: 'provider',
    width: 100,
    align: 'center',
    render(row) {
      const providerMap = {
        openai: 'OpenAI',
        anthropic: 'Anthropic',
        deepseek: 'DeepSeek',
        qianwen: '千问',
        baidu: '百度',
        google: 'Google',
        custom: '自定义',
      }
      return h(NTag, { type: 'info' }, { default: () => providerMap[row.provider] || row.provider })
    },
  },
  {
    title: '模型类型',
    key: 'model_type',
    width: 100,
    align: 'center',
    render(row) {
      const typeMap = {
        chat: '聊天',
        completion: '补全',
        embedding: '嵌入',
        image: '图像',
        audio: '音频',
        multimodal: '多模态',
      }
      return h('span', typeMap[row.model_type] || row.model_type)
    },
  },
  {
    title: '版本',
    key: 'version',
    width: 100,
    align: 'center',
  },
  {
    title: '最大令牌',
    key: 'max_tokens',
    width: 100,
    align: 'center',
  },
  {
    title: '温度',
    key: 'temperature',
    width: 80,
    align: 'center',
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      const statusMap = {
        active: '激活',
        inactive: '未激活',
        deprecated: '已弃用',
        maintenance: '维护中',
      }
      return h(NTag, { type: statusTagType[row.status] || 'default' }, {
        default: () => statusMap[row.status] || row.status
      })
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 150,
    align: 'center',
    render(row) {
      return h(
        NButton,
        { size: 'small', type: 'text', ghost: true },
        {
          default: () => formatDate(row.created_at),
          icon: renderIcon('mdi:update', { size: 16 }),
        }
      )
    },
  },
  {
    title: '操作',
    key: 'actions',
    width: 260,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'primary',
              style: 'margin-right: 8px;',
              onClick: () => handleEdit(row),
            },
            {
              default: () => '编辑',
              icon: renderIcon('material-symbols:edit', { size: 16 }),
            }
          ),
          [[vPermission, 'put/api/v1/model-configs/*']]
        ),
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'info',
              style: 'margin-right: 8px;',
              onClick: () => handleTestModel(row),
            },
            { default: () => '测试', icon: renderIcon('material-symbols:network-check', { size: 16 }) }
          ),
          [[vPermission, 'post/api/v1/model-configs/*/test']]
        ),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => handleDelete(row),
            onNegativeClick: () => {},
          },
          {
            trigger: () =>
              withDirectives(
                h(
                  NButton,
                  {
                    size: 'small',
                    type: 'error',
                  },
                  {
                    default: () => '删除',
                    icon: renderIcon('material-symbols:delete-outline', { size: 16 }),
                  }
                ),
                [[vPermission, 'delete/api/v1/model-configs/*']]
              ),
            default: () => h('div', {}, '确定删除该模型配置吗?'),
          }
        ),
      ]
    },
  },
]

// 表单验证规则
const validateModel = {
  name: [
    {
      required: true,
      message: '请输入模型名称',
      trigger: ['input', 'blur'],
    },
    {
      min: 1,
      max: 100,
      message: '模型名称长度应在1-100个字符之间',
      trigger: ['blur'],
    },
  ],
  provider: [
    {
      required: true,
      message: '请选择提供商',
      trigger: ['change', 'blur'],
    },
  ],
  model_type: [
    {
      required: true,
      message: '请选择模型类型',
      trigger: ['change', 'blur'],
    },
  ],
  api_endpoint: [
    {
      trigger: ['blur'],
      validator: (rule, value, callback) => {
        if (value && !value.startsWith('http://') && !value.startsWith('https://')) {
          callback('API端点必须以http://或https://开头')
          return
        }
        callback()
      },
    },
  ],
  max_tokens: [
    {
      type: 'number',
      required: true,
      message: '请输入最大令牌数',
      trigger: ['blur', 'change'],
    },
  ],
  temperature: [
    {
      type: 'number',
      required: true,
      message: '请输入温度参数',
      trigger: ['blur', 'change'],
    },
  ],
}

async function handleTestModel(row) {
  try {
    const result = await api.testModelConnection(row.id)
    if (result.code === 200) {
      $message.success('模型连接测试成功')
    }
  } catch (error) {
    console.error('模型测试失败:', error)
  }
}

// 批量操作处理
async function handleBatchAction(key) {
  if (!hasSelected.value) {
    $message.warning('请先选择要操作的模型')
    return
  }

  const ids = selectedRowKeys.value

  try {
    switch (key) {
      case 'activate':
        await api.batchUpdateAIModels({ model_ids: ids, status: 'active' })
        $message.success(`成功激活 ${ids.length} 个模型`)
        break
      case 'deactivate':
        await api.batchUpdateAIModels({ model_ids: ids, status: 'inactive' })
        $message.success(`成功停用 ${ids.length} 个模型`)
        break
      case 'delete':
        await api.batchDeleteAIModels({ model_ids: ids })
        $message.success(`成功删除 ${ids.length} 个模型`)
        break
    }
    selectedRowKeys.value = []
    await $table.value?.handleSearch()
  } catch (error) {
    console.error('批量操作失败:', error)
    $message.error('批量操作失败')
  }
}

// 导出数据
async function handleExport() {
  try {
    $message.loading('正在导出数据...')
    const blob = await api.exportAIModels(queryItems.value)
    const url = window.URL.createObjectURL(blob.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `ai_models_${formatDate(new Date(), 'YYYY-MM-DD_HHmmss')}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    $message.success('数据导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    $message.error('导出失败')
  }
}

onMounted(() => {
  $table.value?.handleSearch()
})
</script>

<template>
  <CommonPage show-footer title="AI模型配置">
    <template #action>
      <NSpace>
        <NButton v-permission="'post/api/v1/model-configs/'" type="primary" @click="handleAdd">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
          新增模型
        </NButton>
        <NDropdown
          v-if="hasSelected"
          :options="batchOptions"
          @select="handleBatchAction"
        >
          <NButton type="info">
            <TheIcon icon="mdi:format-list-checks" :size="18" class="mr-5" />
            批量操作 ({{ selectedRowKeys.length }})
          </NButton>
        </NDropdown>
        <NButton type="success" @click="handleExport">
          <TheIcon icon="mdi:download" :size="18" class="mr-5" />
          导出数据
        </NButton>
      </NSpace>
    </template>

    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      v-model:checked-row-keys="selectedRowKeys"
      :columns="columns"
      :get-data="api.getModelList"
    >
      <template #queryBar>
        <QueryBarItem label="模型名称" :label-width="80">
          <NInput
            v-model:value="queryItems.keyword"
            clearable
            type="text"
            placeholder="请输入模型名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="提供商" :label-width="80">
          <NSelect
            v-model:value="queryItems.provider"
            clearable
            :options="providerOptions"
            placeholder="请选择提供商"
          />
        </QueryBarItem>
        <QueryBarItem label="模型类型" :label-width="80">
          <NSelect
            v-model:value="queryItems.model_type"
            clearable
            :options="modelTypeOptions"
            placeholder="请选择模型类型"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="80">
          <NSelect
            v-model:value="queryItems.status"
            clearable
            :options="statusOptions"
            placeholder="请选择状态"
          />
        </QueryBarItem>
      </template>
    </CrudTable>

    <CrudModal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      @save="handleSave"
    >
      <NForm
        ref="modalFormRef"
        label-placement="left"
        label-align="left"
        :label-width="100"
        :model="modalForm"
        :rules="validateModel"
      >
        <NFormItem label="模型名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入模型名称" />
        </NFormItem>
        <NFormItem label="显示名称" path="display_name">
          <NInput v-model:value="modalForm.display_name" clearable placeholder="请输入显示名称" />
        </NFormItem>
        <NFormItem label="提供商" path="provider">
          <NSelect
            v-model:value="modalForm.provider"
            :options="providerOptions"
            placeholder="请选择提供商"
          />
        </NFormItem>
        <NFormItem label="模型类型" path="model_type">
          <NSelect
            v-model:value="modalForm.model_type"
            :options="modelTypeOptions"
            placeholder="请选择模型类型"
          />
        </NFormItem>
        <NFormItem label="版本" path="version">
          <NInput v-model:value="modalForm.version" clearable placeholder="请输入版本" />
        </NFormItem>
        <NFormItem label="API端点" path="api_endpoint">
          <NInput v-model:value="modalForm.api_endpoint" clearable placeholder="请输入API端点URL (https://...)" />
        </NFormItem>
        <NFormItem label="API密钥" path="api_key">
          <NInput
            v-model:value="modalForm.api_key"
            type="password"
            show-password-on="mousedown"
            clearable
            placeholder="请输入API密钥"
          />
        </NFormItem>
        <NFormItem label="最大令牌" path="max_tokens">
          <NInputNumber
            v-model:value="modalForm.max_tokens"
            :min="1"
            :max="1000000"
            placeholder="请输入最大令牌数"
            style="width: 100%"
          />
        </NFormItem>
        <NFormItem label="温度参数" path="temperature">
          <NInputNumber
            v-model:value="modalForm.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            placeholder="请输入温度参数 (0-2)"
            style="width: 100%"
          />
        </NFormItem>
        <NFormItem label="描述" path="description">
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模型描述"
          />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped></style>
