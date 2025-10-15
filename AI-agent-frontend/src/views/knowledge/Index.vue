<script setup>
import { h, onMounted, ref, resolveDirective, withDirectives } from 'vue'
import {
  NButton,
  NTag,
  NSpace,
  NPopconfirm,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NUpload,
  NProgress,
  NSwitch,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudModal from '@/components/table/CrudModal.vue'
import CrudTable from '@/components/table/CrudTable.vue'

import { formatDate, renderIcon } from '@/utils'
import { useCRUD } from '@/composables'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: '知识库管理' })

const vPermission = resolveDirective('permission')
const $table = ref(null)
const queryItems = ref({})

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
  name: '知识库',
  initForm: {
    name: '',
    description: '',
    type: 'document',
    status: 'active',
    is_public: false,
    tags: [],
  },
  doCreate: api.createKnowledge,
  doUpdate: (data) => api.updateKnowledge(data.id, data),
  doDelete: api.deleteKnowledge,
  refresh: () => $table.value?.handleSearch(),
})

// 知识库类型选项
const typeOptions = [
  { label: '文档', value: 'document' },
  { label: 'API文档', value: 'api' },
  { label: '测试用例', value: 'test_case' },
  { label: '问答对', value: 'qa' },
  { label: '代码片段', value: 'code' },
  { label: '其他', value: 'other' },
]

// 状态选项
const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' },
  { label: '归档', value: 'archived' },
]

const statusTagType = {
  active: 'success',
  inactive: 'default',
  archived: 'warning',
}

const columns = [
  {
    title: '知识库名称',
    key: 'name',
    width: 200,
    align: 'center',
    ellipsis: { tooltip: true },
  },
  {
    title: '类型',
    key: 'type',
    width: 120,
    align: 'center',
    render(row) {
      const typeMap = {
        document: '文档',
        api: 'API文档',
        test_case: '测试用例',
        qa: '问答对',
        code: '代码片段',
        other: '其他',
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
        active: '启用',
        inactive: '禁用',
        archived: '归档',
      }
      return h(NTag, { type: statusTagType[row.status] || 'default' }, {
        default: () => statusMap[row.status] || row.status
      })
    },
  },
  {
    title: '文档数量',
    key: 'document_count',
    width: 100,
    align: 'center',
    render(row) {
      return row.document_count || 0
    },
  },
  {
    title: '公开',
    key: 'is_public',
    width: 80,
    align: 'center',
    render(row) {
      return h(NTag, { type: row.is_public ? 'success' : 'default', size: 'small' }, {
        default: () => row.is_public ? '是' : '否'
      })
    },
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 160,
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
    width: 300,
    align: 'center',
    fixed: 'right',
    render(row) {
      return [
        withDirectives(
          h(
            NButton,
            {
              size: 'small',
              type: 'info',
              style: 'margin-right: 8px;',
              onClick: () => handleManageDocuments(row),
            },
            {
              default: () => '文档管理',
              icon: renderIcon('mdi:file-document-multiple', { size: 16 }),
            }
          ),
          [[vPermission, 'get/api/v1/knowledge/*/documents']]
        ),
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
          [[vPermission, 'put/api/v1/knowledge/*']]
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
                [[vPermission, 'delete/api/v1/knowledge/*']]
              ),
            default: () => h('div', {}, '确定删除该知识库吗?'),
          }
        ),
      ]
    },
  },
]

// 表单验证规则
const validateKnowledge = {
  name: [
    {
      required: true,
      message: '请输入知识库名称',
      trigger: ['input', 'blur'],
    },
    {
      min: 1,
      max: 200,
      message: '知识库名称长度应在1-200个字符之间',
      trigger: ['blur'],
    },
  ],
  type: [
    {
      required: true,
      message: '请选择知识库类型',
      trigger: ['change', 'blur'],
    },
  ],
}

async function handleManageDocuments(row) {
  // 跳转到文档管理页面
  $message.info(`即将打开知识库 "${row.name}" 的文档管理界面`)
  // TODO: 实现文档管理功能
}

onMounted(() => {
  $table.value?.handleSearch()
})
</script>

<template>
  <CommonPage show-footer title="知识库管理">
    <template #action>
      <NButton v-permission="'post/api/v1/knowledge/'" type="primary" @click="handleAdd">
        <TheIcon icon="material-symbols:add" :size="18" class="mr-5" />
        新增知识库
      </NButton>
    </template>

    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getKnowledgeList"
    >
      <template #queryBar>
        <QueryBarItem label="知识库名称" :label-width="90">
          <NInput
            v-model:value="queryItems.keyword"
            clearable
            type="text"
            placeholder="请输入知识库名称"
            @keypress.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="类型" :label-width="60">
          <NSelect
            v-model:value="queryItems.type"
            clearable
            :options="typeOptions"
            placeholder="请选择类型"
          />
        </QueryBarItem>
        <QueryBarItem label="状态" :label-width="60">
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
        :rules="validateKnowledge"
      >
        <NFormItem label="知识库名称" path="name">
          <NInput v-model:value="modalForm.name" clearable placeholder="请输入知识库名称" />
        </NFormItem>
        <NFormItem label="知识库类型" path="type">
          <NSelect
            v-model:value="modalForm.type"
            :options="typeOptions"
            placeholder="请选择知识库类型"
          />
        </NFormItem>
        <NFormItem label="状态" path="status">
          <NSelect
            v-model:value="modalForm.status"
            :options="statusOptions"
            placeholder="请选择状态"
          />
        </NFormItem>
        <NFormItem label="公开访问" path="is_public">
          <NSwitch v-model:value="modalForm.is_public" />
        </NFormItem>
        <NFormItem label="描述" path="description">
          <NInput
            v-model:value="modalForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入知识库描述"
          />
        </NFormItem>
      </NForm>
    </CrudModal>
  </CommonPage>
</template>

<style scoped></style>

