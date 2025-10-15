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

defineOptions({ name: '测试用例管理' })

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
  name: '测试用例',
  initForm: {
    name: '',
    module: '',
    description: '',
    preconditions: '',
    test_steps: '',
    expected_result: '',
    priority: 'P3',
    test_type: 'functional',
    tags: '',
  },
  doCreate: api.createTestCase,
  doUpdate: (data) => api.updateTestCase(data.id, data),
  doDelete: api.deleteTestCase,
  refresh: () => $table.value?.handleSearch(),
})

const priorityOptions = [
  { label: 'P1 - 最高优先级', value: 'P1' },
  { label: 'P2 - 高优先级', value: 'P2' },
  { label: 'P3 - 中优先级', value: 'P3' },
  { label: 'P4 - 低优先级', value: 'P4' },
  { label: 'P5 - 最低优先级', value: 'P5' },
]

const testTypeOptions = [
  { label: '功能测试', value: 'functional' },
  { label: '性能测试', value: 'performance' },
  { label: '安全测试', value: 'security' },
  { label: 'UI测试', value: 'ui' },
  { label: 'API测试', value: 'api' },
  { label: '集成测试', value: 'integration' },
  { label: '单元测试', value: 'unit' },
]

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '待执行', value: 'pending' },
  { label: '执行中', value: 'running' },
  { label: '通过', value: 'passed' },
  { label: '失败', value: 'failed' },
  { label: '已跳过', value: 'skipped' },
  { label: '阻塞', value: 'blocked' },
]

const statusTagType = {
  draft: 'default',
  pending: 'warning',
  running: 'info',
  passed: 'success',
  failed: 'error',
  skipped: 'default',
  blocked: 'error',
}

const priorityTagType = {
  P1: 'error',
  P2: 'warning',
  P3: 'info',
  P4: 'default',
  P5: 'default',
}

// 批量操作选项
const batchOptions = [
  {
    label: '批量执行',
    key: 'execute',
    icon: renderIcon('material-symbols:play-arrow', { size: 18 }),
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
    title: '用例名称',
    key: 'name',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '所属模块',
    key: 'module',
    width: 120,
    align: 'center',
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    align: 'center',
    render(row) {
      return h(NTag, { type: priorityTagType[row.priority] || 'default' }, {
        default: () => row.priority
      })
    },
  },
  {
    title: '测试类型',
    key: 'test_type',
    width: 100,
    align: 'center',
    render(row) {
      const typeMap = {
        functional: '功能',
        performance: '性能',
        security: '安全',
        ui: 'UI',
        api: 'API',
        integration: '集成',
        unit: '单元',
      }
      return h(NTag, { type: 'info' }, { default: () => typeMap[row.test_type] || row.test_type })
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      const statusMap = {
        draft: '草稿',
        pending: '待执行',
        running: '执行中',
        passed: '通过',
        failed: '失败',
        skipped: '已跳过',
        blocked: '阻塞',
      }
      return h(NTag, { type: statusTagType[row.status] || 'default' }, {
        default: () => statusMap[row.status] || row.status
      })
    },
  },
  {
    title: '标签',
    key: 'tags',
    width: 120,
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
          [[vPermission, 'put/api/v1/test-cases/*']]
        ),
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'info',
              style: 'margin-right: 8px;',
              onClick: () => handleExecuteTest(row),
              disabled: row.status === 'running',
            },
            { default: () => '执行', icon: renderIcon('material-symbols:play-arrow', { size: 16 }) }
          ),
          [[vPermission, 'post/api/v1/test-cases/*/execute']]
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
                [[vPermission, 'delete/api/v1/test-cases/*']]
              ),
            default: () => h('div', {}, '确定删除该测试用例吗?'),
          }
        ),
      ]
    },
  },
]

// 表单验证规则
const validateTestCase = {
  name: [
    {
      required: true,
      message: '请输入用例名称',
      trigger: ['input', 'blur'],
    },
    {
      min: 1,
      max: 200,
      message: '用例名称长度应在1-200个字符之间',
      trigger: ['blur'],
    },
  ],
  priority: [
    {
      required: true,
      message: '请选择优先级',
      trigger: ['change', 'blur'],
    },
  ],
  test_type: [
    {
      required: true,
      message: '请选择测试类型',
      trigger: ['change', 'blur'],
    },
  ],
  test_steps: [
    {
      required: true,
      message: '请输入测试步骤',
      trigger: ['input', 'blur'],
    },
  ],
  expected_result: [
    {
      required: true,
      message: '请输入预期结果',
      trigger: ['input', 'blur'],
    },
  ],
}

async function handleExecuteTest(row) {
  try {
    await api.executeTestCase(row.id, {})
    $message.success('测试用例执行成功')
    await $table.value?.handleSearch()
  } catch (error) {
    console.error('执行测试用例失败:', error)
  }
}

// 批量操作处理
async function handleBatchAction(key) {
  if (!hasSelected.value) {
    $message.warning('请先选择要操作的测试用例')
    return
  }

  const ids = selectedRowKeys.value

  try {
    switch (key) {
      case 'execute':
        await api.batchExecuteTestCases({ test_case_ids: ids })
        $message.success(`成功执行 ${ids.length} 个测试用例`)
        break
      case 'delete':
        await api.batchDeleteTestCases({ test_case_ids: ids })
        $message.success(`成功删除 ${ids.length} 个测试用例`)
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
    const blob = await api.exportTestCases(queryItems.value)
    const url = window.URL.createObjectURL(blob.data)
    const a = document.createElement('a')
    a.href = url
    a.download = `test_cases_${formatDate(new Date(), 'YYYY-MM-DD_HHmmss')}.xlsx`
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
  <CommonPage show-footer title="测试用例管理">
    <template #action>
      <NSpace>
        <NButton v-permission="'post/api/v1/test-cases/'" type="primary" @click="handleAdd">
          <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
          新增用例
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
      :get-data="api.getTestCaseList"
    >
      <template #queryBar>
        <QueryBarItem label="用例名称" :label-width="80">
          <NInput
            v-model:value="queryItems.keyword"
            clearable
            type="text"
            placeholder="请输入用例名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="所属模块" :label-width="80">
          <NInput
            v-model:value="queryItems.module"
            clearable
            type="text"
            placeholder="请输入模块名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="优先级" :label-width="80">
          <NSelect
            v-model:value="queryItems.priority"
            clearable
            :options="priorityOptions"
            placeholder="请选择优先级"
          />
        </QueryBarItem>
        <QueryBarItem label="测试类型" :label-width="80">
          <NSelect
            v-model:value="queryItems.test_type"
            clearable
            :options="testTypeOptions"
            placeholder="请选择测试类型"
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
        :rules="validateTestCase"
      >
        <NFormItem label="用例名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入用例名称" />
        </NFormItem>
        <NFormItem label="所属模块" path="module">
          <NInput v-model:value="modalForm.module" clearable placeholder="请输入所属模块" />
        </NFormItem>
        <NFormItem label="优先级" path="priority">
          <NSelect
            v-model:value="modalForm.priority"
            :options="priorityOptions"
            placeholder="请选择优先级"
          />
        </NFormItem>
        <NFormItem label="测试类型" path="test_type">
          <NSelect
            v-model:value="modalForm.test_type"
            :options="testTypeOptions"
            placeholder="请选择测试类型"
          />
        </NFormItem>
        <NFormItem label="用例描述" path="description">
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入用例描述"
          />
        </NFormItem>
        <NFormItem label="前置条件" path="preconditions">
          <NInput
            v-model:value="modalForm.preconditions"
            type="textarea"
            :rows="2"
            placeholder="请输入前置条件"
          />
        </NFormItem>
        <NFormItem label="测试步骤" path="test_steps">
          <NInput
            v-model:value="modalForm.test_steps"
            type="textarea"
            :rows="3"
            placeholder="请输入测试步骤"
          />
        </NFormItem>
        <NFormItem label="预期结果" path="expected_result">
          <NInput
            v-model:value="modalForm.expected_result"
            type="textarea"
            :rows="2"
            placeholder="请输入预期结果"
          />
        </NFormItem>
        <NFormItem label="标签" path="tags">
          <NInput v-model:value="modalForm.tags" clearable placeholder="请输入标签，多个用逗号分隔" />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped></style>
