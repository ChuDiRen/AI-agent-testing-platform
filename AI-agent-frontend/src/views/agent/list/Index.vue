<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives, computed } from 'vue'
import {
  NButton,
  NTag,
  NSpace,
  NPopconfirm,
  NSwitch,
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

defineOptions({ name: 'AI代理列表' })

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
  name: '代理',
  initForm: {
    name: '',
    type: 'chat',
    description: '',
    config: {},
    version: '1.0.0',
  },
  doCreate: api.createAgent,
  doUpdate: (data) => api.updateAgent(data.id, data),
  doDelete: api.deleteAgent,
  refresh: () => $table.value?.handleSearch(),
})

const agentTypeOptions = [
  { label: '聊天', value: 'chat' },
  { label: '任务', value: 'task' },
  { label: '分析', value: 'analysis' },
  { label: '测试', value: 'testing' },
  { label: '自定义', value: 'custom' },
]

const agentStatusOptions = [
  { label: '未激活', value: 'inactive' },
  { label: '激活', value: 'active' },
  { label: '运行中', value: 'running' },
  { label: '已停止', value: 'stopped' },
  { label: '错误', value: 'error' },
  { label: '维护中', value: 'maintenance' },
]

const statusTagType = {
  inactive: 'default',
  active: 'success',
  running: 'info',
  stopped: 'warning',
  error: 'error',
  maintenance: 'warning',
}

// 批量操作选项
const batchOptions = [
  {
    label: '批量启动',
    key: 'start',
    icon: renderIcon('material-symbols:play-arrow', { size: 18 }),
  },
  {
    label: '批量停止',
    key: 'stop',
    icon: renderIcon('material-symbols:stop', { size: 18 }),
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
    title: '代理名称',
    key: 'name',
    width: 150,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '代理类型',
    key: 'type',
    width: 100,
    align: 'center',
    render(row) {
      const typeMap = {
        chat: '聊天',
        task: '任务',
        analysis: '分析',
        testing: '测试',
        custom: '自定义',
      }
      return h(NTag, { type: 'info' }, { default: () => typeMap[row.type] || row.type })
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      const statusMap = {
        inactive: '未激活',
        active: '激活',
        running: '运行中',
        stopped: '已停止',
        error: '错误',
        maintenance: '维护中',
      }
      return h(NTag, { type: statusTagType[row.status] || 'default' }, {
        default: () => statusMap[row.status] || row.status
      })
    },
  },
  {
    title: '版本',
    key: 'version',
    width: 80,
    align: 'center',
  },
  {
    title: '描述',
    key: 'description',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true },
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
    width: 280,
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
          [[vPermission, 'put/api/v1/agents/*']]
        ),
        row.status === 'stopped' || row.status === 'inactive'
          ? withDirectives(
              h(
                NButton,
                {
                  size: 'small',
                  type: 'success',
                  style: 'margin-right: 8px;',
                  onClick: () => handleStartAgent(row),
                },
                { default: () => '启动', icon: renderIcon('material-symbols:play-arrow', { size: 16 }) }
              ),
              [[vPermission, 'post/api/v1/agents/*/start']]
            )
          : withDirectives(
              h(
                NButton,
                {
                  size: 'small',
                  type: 'warning',
                  style: 'margin-right: 8px;',
                  onClick: () => handleStopAgent(row),
                },
                { default: () => '停止', icon: renderIcon('material-symbols:stop', { size: 16 }) }
              ),
              [[vPermission, 'post/api/v1/agents/*/stop']]
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
                [[vPermission, 'delete/api/v1/agents/*']]
              ),
            default: () => h('div', {}, '确定删除该代理吗?'),
          }
        ),
      ]
    },
  },
]

// 表单验证规则
const validateAgent = {
  name: [
    {
      required: true,
      message: '请输入代理名称',
      trigger: ['input', 'blur'],
    },
    {
      min: 1,
      max: 100,
      message: '代理名称长度应在1-100个字符之间',
      trigger: ['blur'],
    },
  ],
  type: [
    {
      required: true,
      message: '请选择代理类型',
      trigger: ['change', 'blur'],
    },
  ],
  version: [
    {
      required: true,
      message: '请输入版本号',
      trigger: ['input', 'blur'],
    },
    {
      trigger: ['blur'],
      validator: (rule, value, callback) => {
        const re = /^\d+\.\d+\.\d+$/
        if (value && !re.test(value)) {
          callback('版本号格式应为 x.y.z (如: 1.0.0)')
          return
        }
        callback()
      },
    },
  ],
}

async function handleStartAgent(row) {
  try {
    await api.startAgent(row.id)
    $message.success('代理启动成功')
    await $table.value?.handleSearch()
  } catch (error) {
    console.error('启动代理失败:', error)
  }
}

async function handleStopAgent(row) {
  try {
    await api.stopAgent(row.id)
    $message.success('代理已停止')
    await $table.value?.handleSearch()
  } catch (error) {
    console.error('停止代理失败:', error)
  }
}

// 批量操作处理
async function handleBatchAction(key) {
  if (!hasSelected.value) {
    $message.warning('请先选择要操作的代理')
    return
  }

  const ids = selectedRowKeys.value

  try {
    switch (key) {
      case 'start':
        await api.batchOperateAgents({ action: 'start', agent_ids: ids })
        $message.success(`成功启动 ${ids.length} 个代理`)
        break
      case 'stop':
        await api.batchOperateAgents({ action: 'stop', agent_ids: ids })
        $message.success(`成功停止 ${ids.length} 个代理`)
        break
      case 'delete':
        await api.batchOperateAgents({ action: 'delete', agent_ids: ids })
        $message.success(`成功删除 ${ids.length} 个代理`)
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
    const blob = await api.exportAgents(queryItems.value)
    const url = window.URL.createObjectURL(blob.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `agents_${formatDate(new Date(), 'YYYY-MM-DD_HHmmss')}.xlsx`
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
  <CommonPage show-footer title="AI代理列表">
    <template #action>
      <NSpace>
        <NButton v-permission="'post/api/v1/agents/'" type="primary" @click="handleAdd">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
          新增代理
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
      :get-data="api.getAgentList"
    >
      <template #queryBar>
        <QueryBarItem label="代理名称" :label-width="80">
          <NInput
            v-model:value="queryItems.keyword"
            clearable
            type="text"
            placeholder="请输入代理名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="代理类型" :label-width="80">
          <NSelect
            v-model:value="queryItems.type"
            clearable
            :options="agentTypeOptions"
            placeholder="请选择代理类型"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="80">
          <NSelect
            v-model:value="queryItems.status"
            clearable
            :options="agentStatusOptions"
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
        :label-width="80"
        :model="modalForm"
        :rules="validateAgent"
      >
        <NFormItem label="代理名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入代理名称" />
        </NFormItem>
        <NFormItem label="代理类型" path="type">
          <NSelect
            v-model:value="modalForm.type"
            :options="agentTypeOptions"
            placeholder="请选择代理类型"
          />
        </NFormItem>
        <NFormItem label="版本" path="version">
          <NInput v-model:value="modalForm.version" clearable placeholder="请输入版本号 (如: 1.0.0)" />
        </NFormItem>
        <NFormItem label="描述" path="description">
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入代理描述"
          />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped></style>
