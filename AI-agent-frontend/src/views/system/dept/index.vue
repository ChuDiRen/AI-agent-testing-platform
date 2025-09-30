<template>
  <div class="dept-management">
    <div class="page-header">
      <h2>部门管理</h2>
      <NButton
        v-permission="['post/dept/create']"
        type="primary"
        @click="handleAdd"
      >
        <template #icon>
          <Icon name="mdi:plus" />
        </template>
        新建部门
      </NButton>
    </div>

    <!-- 查询栏 -->
    <NCard class="search-card">
      <NForm inline :model="queryForm" label-placement="left">
        <NFormItem label="部门名称">
          <NInput
            v-model:value="queryForm.name"
            placeholder="请输入部门名称"
            clearable
            @keydown.enter="handleSearch"
          />
        </NFormItem>
        <NFormItem>
          <NSpace>
            <NButton type="primary" @click="handleSearch">
              <template #icon>
                <Icon name="mdi:magnify" />
              </template>
              搜索
            </NButton>
            <NButton @click="handleReset">
              <template #icon>
                <Icon name="mdi:refresh" />
              </template>
              重置
            </NButton>
          </NSpace>
        </NFormItem>
      </NForm>
    </NCard>

    <!-- 数据表格 -->
    <NCard>
      <NDataTable
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :row-key="(row) => row.id"
        default-expand-all
      />
    </NCard>

    <!-- 新增/编辑弹窗 -->
    <NModal v-model:show="modalVisible" preset="dialog" :title="modalTitle" style="width: 500px">
      <NForm
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <NFormItem label="部门名称" path="name">
          <NInput v-model:value="formData.name" placeholder="请输入部门名称" />
        </NFormItem>
        <NFormItem label="父级部门" path="parent_id">
          <NTreeSelect
            v-model:value="formData.parent_id"
            :options="parentDeptOptions"
            key-field="id"
            label-field="name"
            placeholder="请选择父级部门"
            clearable
            default-expand-all
          />
        </NFormItem>
        <NFormItem label="部门描述" path="description">
          <NInput
            v-model:value="formData.description"
            type="textarea"
            placeholder="请输入部门描述"
            :rows="3"
          />
        </NFormItem>
        <NFormItem label="排序" path="order_num">
          <NInputNumber v-model:value="formData.order_num" placeholder="请输入排序号" />
        </NFormItem>
      </NForm>
      <template #action>
        <NSpace>
          <NButton @click="modalVisible = false">取消</NButton>
          <NButton type="primary" :loading="submitLoading" @click="handleSubmit">
            确定
          </NButton>
        </NSpace>
      </template>
    </NModal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, h, computed } from 'vue'
import { Icon } from '@iconify/vue'
import { formatDate } from '@/utils'
import api from '@/api'

defineOptions({ name: '部门管理' })

// 响应式数据
const loading = ref(false)
const tableData = ref([])
const modalVisible = ref(false)
const modalTitle = ref('')
const modalAction = ref('add')
const submitLoading = ref(false)
const formRef = ref()

// 查询表单
const queryForm = reactive({
  name: '',
})

// 表单数据
const formData = reactive({
  id: null,
  name: '',
  parent_id: 0,
  description: '',
  order_num: 0,
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' },
  ],
}

// 父级部门选项
const parentDeptOptions = computed(() => {
  const options = [{ id: 0, name: '根部门', children: [] }]
  
  const buildTree = (data, parentId = 0) => {
    return data
      .filter(item => item.parent_id === parentId && item.id !== formData.id)
      .map(item => ({
        id: item.id,
        name: item.name,
        children: buildTree(data, item.id)
      }))
  }
  
  // 扁平化数据用于构建树
  const flatData = []
  const flatten = (data) => {
    data.forEach(item => {
      flatData.push(item)
      if (item.children && item.children.length > 0) {
        flatten(item.children)
      }
    })
  }
  flatten(tableData.value)
  
  options[0].children = buildTree(flatData)
  return options
})

// 表格列配置
const columns = [
  { title: '部门名称', key: 'name', width: 200 },
  { title: '部门描述', key: 'description', ellipsis: { tooltip: true } },
  {
    title: '排序',
    key: 'order_num',
    width: 80,
    align: 'center',
  },
  {
    title: '创建时间',
    key: 'created_at',
    width: 180,
    render: (row) => formatDate(row.created_at),
  },
  {
    title: '操作',
    key: 'actions',
    width: 200,
    fixed: 'right',
    render: (row) => {
      return h('div', [
        h(NButton, 
          { 
            size: 'small', 
            type: 'primary', 
            style: 'margin-right: 8px',
            onClick: () => handleEdit(row) 
          },
          { default: () => '编辑' }
        ),
        h(NButton, 
          { 
            size: 'small', 
            type: 'info', 
            style: 'margin-right: 8px',
            onClick: () => handleAddChild(row) 
          },
          { default: () => '添加子部门' }
        ),
        h(NPopconfirm, 
          {
            onPositiveClick: () => handleDelete(row),
          },
          {
            trigger: () => h(NButton, 
              { size: 'small', type: 'error' },
              { default: () => '删除' }
            ),
            default: () => '确定删除该部门吗？',
          }
        ),
      ])
    },
  },
]

// 构建树形结构
const buildDeptTree = (data) => {
  const tree = []
  const map = new Map()
  
  // 先创建所有节点的映射
  data.forEach(item => {
    map.set(item.id, { ...item, children: [] })
  })
  
  // 构建树形结构
  data.forEach(item => {
    const node = map.get(item.id)
    if (item.parent_id === 0) {
      tree.push(node)
    } else {
      const parent = map.get(item.parent_id)
      if (parent) {
        parent.children.push(node)
      }
    }
  })
  
  return tree
}

// 获取部门列表
const getDeptList = async () => {
  try {
    loading.value = true
    const params = {
      ...queryForm,
    }
    const res = await api.getDepts(params)
    const deptData = res.data
    tableData.value = buildDeptTree(deptData)
  } catch (error) {
    window.$message?.error('获取部门列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  getDeptList()
}

// 重置
const handleReset = () => {
  Object.assign(queryForm, {
    name: '',
  })
  handleSearch()
}

// 新增
const handleAdd = () => {
  modalAction.value = 'add'
  modalTitle.value = '新增部门'
  Object.assign(formData, {
    id: null,
    name: '',
    parent_id: 0,
    description: '',
    order_num: 0,
  })
  modalVisible.value = true
}

// 添加子部门
const handleAddChild = (row) => {
  modalAction.value = 'add'
  modalTitle.value = '新增子部门'
  Object.assign(formData, {
    id: null,
    name: '',
    parent_id: row.id,
    description: '',
    order_num: 0,
  })
  modalVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  modalAction.value = 'edit'
  modalTitle.value = '编辑部门'
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    parent_id: row.parent_id,
    description: row.description,
    order_num: row.order_num,
  })
  modalVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true
    
    if (modalAction.value === 'add') {
      await api.createDept(formData)
      window.$message?.success('创建成功')
    } else {
      await api.updateDept(formData)
      window.$message?.success('更新成功')
    }
    
    modalVisible.value = false
    getDeptList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await api.deleteDept({ dept_id: row.id })
    window.$message?.success('删除成功')
    getDeptList()
  } catch (error) {
    window.$message?.error('删除失败')
  }
}

// 初始化
onMounted(() => {
  getDeptList()
})
</script>

<style scoped>
.dept-management {
  padding: 16px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}

.search-card {
  margin-bottom: 16px;
}
</style>
