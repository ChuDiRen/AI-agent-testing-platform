<template>
  <div class="menu-management">
    <div class="page-header">
      <h2>菜单管理</h2>
      <NButton
        v-permission="['post/menu/create']"
        type="primary"
        @click="handleAdd"
      >
        <template #icon>
          <Icon name="mdi:plus" />
        </template>
        新建菜单
      </NButton>
    </div>

    <!-- 查询栏 -->
    <NCard class="search-card">
      <NForm inline :model="queryForm" label-placement="left">
        <NFormItem label="菜单名称">
          <NInput
            v-model:value="queryForm.name"
            placeholder="请输入菜单名称"
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
    <NModal v-model:show="modalVisible" preset="dialog" :title="modalTitle" style="width: 600px">
      <NForm
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-placement="left"
        label-width="100px"
      >
        <NFormItem label="菜单名称" path="name">
          <NInput v-model:value="formData.name" placeholder="请输入菜单名称" />
        </NFormItem>
        <NFormItem label="父级菜单" path="parent_id">
          <NTreeSelect
            v-model:value="formData.parent_id"
            :options="parentMenuOptions"
            key-field="id"
            label-field="name"
            placeholder="请选择父级菜单"
            clearable
            default-expand-all
          />
        </NFormItem>
        <NFormItem label="菜单路径" path="path">
          <NInput v-model:value="formData.path" placeholder="请输入菜单路径" />
        </NFormItem>
        <NFormItem label="组件路径" path="component">
          <NInput v-model:value="formData.component" placeholder="请输入组件路径" />
        </NFormItem>
        <NFormItem label="菜单图标" path="icon">
          <NInput v-model:value="formData.icon" placeholder="请输入图标名称">
            <template #prefix>
              <Icon v-if="formData.icon" :name="formData.icon" />
            </template>
          </NInput>
        </NFormItem>
        <NFormItem label="排序" path="order_num">
          <NInputNumber v-model:value="formData.order_num" placeholder="请输入排序号" />
        </NFormItem>
        <NFormItem label="重定向" path="redirect">
          <NInput v-model:value="formData.redirect" placeholder="请输入重定向路径" />
        </NFormItem>
        <NFormItem label="是否可见">
          <NSwitch v-model:value="formData.is_visible" />
        </NFormItem>
        <NFormItem label="是否缓存">
          <NSwitch v-model:value="formData.keep_alive" />
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
import api from '@/api'

defineOptions({ name: '菜单管理' })

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
  path: '',
  component: '',
  icon: '',
  order_num: 0,
  redirect: '',
  is_visible: true,
  keep_alive: false,
})

// 表单验证规则
const formRules = {
  name: [
    { required: true, message: '请输入菜单名称', trigger: 'blur' },
  ],
  path: [
    { required: true, message: '请输入菜单路径', trigger: 'blur' },
  ],
}

// 父级菜单选项
const parentMenuOptions = computed(() => {
  const options = [{ id: 0, name: '根菜单', children: [] }]
  
  const buildTree = (data, parentId = 0) => {
    return data
      .filter(item => item.parent_id === parentId && item.id !== formData.id)
      .map(item => ({
        id: item.id,
        name: item.name,
        children: buildTree(data, item.id)
      }))
  }
  
  options[0].children = buildTree(tableData.value)
  return options
})

// 表格列配置
const columns = [
  {
    title: '菜单名称',
    key: 'name',
    width: 200,
    render: (row) => {
      return h('div', { style: 'display: flex; align-items: center;' }, [
        row.icon && h(Icon, { name: row.icon, style: 'margin-right: 8px;' }),
        h('span', row.name)
      ])
    },
  },
  { title: '菜单路径', key: 'path', width: 200 },
  { title: '组件路径', key: 'component', width: 200, ellipsis: { tooltip: true } },
  {
    title: '排序',
    key: 'order_num',
    width: 80,
    align: 'center',
  },
  {
    title: '可见',
    key: 'is_visible',
    width: 80,
    align: 'center',
    render: (row) => h(NTag, 
      { type: row.is_visible ? 'success' : 'default', size: 'small' },
      { default: () => row.is_visible ? '是' : '否' }
    ),
  },
  {
    title: '缓存',
    key: 'keep_alive',
    width: 80,
    align: 'center',
    render: (row) => h(NTag, 
      { type: row.keep_alive ? 'success' : 'default', size: 'small' },
      { default: () => row.keep_alive ? '是' : '否' }
    ),
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
          { default: () => '添加子菜单' }
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
            default: () => '确定删除该菜单吗？',
          }
        ),
      ])
    },
  },
]

// 构建树形结构
const buildMenuTree = (data) => {
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

// 获取菜单列表
const getMenuList = async () => {
  try {
    loading.value = true
    const params = {
      page: 1,
      page_size: 9999,
      ...queryForm,
    }
    const res = await api.getMenus(params)
    const menuData = res.data.items || res.data
    tableData.value = buildMenuTree(menuData)
  } catch (error) {
    window.$message?.error('获取菜单列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  getMenuList()
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
  modalTitle.value = '新增菜单'
  Object.assign(formData, {
    id: null,
    name: '',
    parent_id: 0,
    path: '',
    component: '',
    icon: '',
    order_num: 0,
    redirect: '',
    is_visible: true,
    keep_alive: false,
  })
  modalVisible.value = true
}

// 添加子菜单
const handleAddChild = (row) => {
  modalAction.value = 'add'
  modalTitle.value = '新增子菜单'
  Object.assign(formData, {
    id: null,
    name: '',
    parent_id: row.id,
    path: '',
    component: '',
    icon: '',
    order_num: 0,
    redirect: '',
    is_visible: true,
    keep_alive: false,
  })
  modalVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  modalAction.value = 'edit'
  modalTitle.value = '编辑菜单'
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    parent_id: row.parent_id,
    path: row.path,
    component: row.component,
    icon: row.icon,
    order_num: row.order_num,
    redirect: row.redirect,
    is_visible: row.is_visible,
    keep_alive: row.keep_alive,
  })
  modalVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true
    
    if (modalAction.value === 'add') {
      await api.createMenu(formData)
      window.$message?.success('创建成功')
    } else {
      await api.updateMenu(formData)
      window.$message?.success('更新成功')
    }
    
    modalVisible.value = false
    getMenuList()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await api.deleteMenu({ menu_id: row.id })
    window.$message?.success('删除成功')
    getMenuList()
  } catch (error) {
    window.$message?.error('删除失败')
  }
}

// 初始化
onMounted(() => {
  getMenuList()
})
</script>

<style scoped>
.menu-management {
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
