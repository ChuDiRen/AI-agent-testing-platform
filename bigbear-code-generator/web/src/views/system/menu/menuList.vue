<template>
  <div class="page-container">
    <!-- 搜索和筛选区域 -->
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="菜单名称">
          <el-input
            v-model="searchForm.menu_name"
            placeholder="请输入菜单名称"
            clearable
            @clear="loadData"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="菜单类型">
          <el-select
            v-model="searchForm.menu_type"
            placeholder="请选择菜单类型"
            clearable
            @clear="loadData"
            style="width: 120px"
          >
            <el-option label="目录" value="M" />
            <el-option label="菜单" value="C" />
            <el-option label="按钮" value="F" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
            @clear="loadData"
            style="width: 120px"
          >
            <el-option label="正常" value="0" />
            <el-option label="停用" value="1" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <BaseTable
      title="菜单管理"
      :data="tableData"
      :loading="loading"
      :show-pagination="false"
      :show-expand-toggle="true"
      row-key="id"
      :tree-props="{ children: 'children' }"
      @refresh="loadData"
    >
      <template #header>
        <el-button v-permission="'system:menu:view'" @click="loadData()">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" v-permission="'system:menu:add'" @click="onDataForm(-1, 0)">
          <el-icon><Plus /></el-icon>
          新增菜单
        </el-button>
        <el-button type="success" @click="toggleExpandAll">
          <el-icon><DCaret v-if="!expandAll" /><UCaret v-else /></el-icon>
          {{ expandAll ? '收起' : '展开' }}全部
        </el-button>
      </template>

      <el-table-column prop="menu_name" label="菜单名称" min-width="180" show-overflow-tooltip>
        <template #default="scope">
          <div class="menu-name-cell">
            <el-icon v-if="scope.row.icon" class="menu-icon" :size="16">
              <component :is="scope.row.icon" />
            </el-icon>
            <span>{{ scope.row.menu_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="icon" label="图标" width="70" align="center">
        <template #default="scope">
          <el-icon v-if="scope.row.icon" :size="18">
            <component :is="scope.row.icon" />
          </el-icon>
          <span v-else style="color: var(--el-text-color-placeholder);">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="order_num" label="排序" width="70" align="center">
        <template #default="scope">
          <el-tag size="small" type="info">{{ scope.row.order_num }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="menu_type" label="类型" width="80" align="center">
        <template #default="scope">
          <el-tag v-if="scope.row.menu_type === 'M'" type="warning" size="small">目录</el-tag>
          <el-tag v-else-if="scope.row.menu_type === 'C'" type="primary" size="small">菜单</el-tag>
          <el-tag v-else type="success" size="small">按钮</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="perms" label="权限标识" min-width="180" show-overflow-tooltip>
        <template #default="scope">
          <el-tag v-if="scope.row.perms" size="small" type="warning">{{ scope.row.perms }}</el-tag>
          <span v-else style="color: var(--el-text-color-placeholder);">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="component" label="组件路径" min-width="180" show-overflow-tooltip>
        <template #default="scope">
          <span v-if="scope.row.component">{{ scope.row.component }}</span>
          <span v-else style="color: var(--el-text-color-placeholder);">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="visible" label="可见" width="70" align="center">
        <template #default="scope">
          <el-switch
            v-model="scope.row.visible"
            active-value="0"
            inactive-value="1"
            @change="updateVisible(scope.row)"
            :disabled="!hasPermission('system:menu:edit')"
          />
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="70" align="center">
        <template #default="scope">
          <el-tag v-if="scope.row.status === '0'" type="success" size="small">正常</el-tag>
          <el-tag v-else type="danger" size="small">停用</el-tag>
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="220" align="center">
        <template #default="scope">
          <el-button link type="primary" size="small" v-permission="'system:menu:add'" @click.prevent="onDataForm(-1, scope.row.id)">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button link type="warning" size="small" v-permission="'system:menu:edit'" @click.prevent="onDataForm(scope.row.id, null)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="danger" size="small" v-permission="'system:menu:delete'" @click.prevent="onDelete(scope.row.id, scope.row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { getMenuTree, deleteData, updateData } from './menu'
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseTable from '~/components/BaseTable/index.vue'
import { useUserStore } from '~/stores/index.js'

const router = useRouter()
const userStore = useUserStore()

// 表格数据
const tableData = ref([])
const loading = ref(false)
const expandAll = ref(false)

// 搜索表单
const searchForm = reactive({
    menu_name: '',
    menu_type: '',
    status: ''
})

// 权限检查
const hasPermission = (perm) => {
    const permissions = userStore.permissions || []
    return permissions.includes(perm)
}

// 加载页面数据（树形结构）
const loadData = () => {
    loading.value = true
    getMenuTree().then((res) => {
        if (res.data.code === 200) {
            let data = res.data.data || []
            // 客户端筛选
            data = filterMenuTree(data)
            tableData.value = data
            if (expandAll.value) {
                setExpandAll(tableData.value, true)
            }
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch((error) => {
        console.error('查询失败:', error)
        ElMessage.error('查询失败，请稍后重试')
    }).finally(() => {
        loading.value = false
    })
}

// 客户端筛选菜单树
const filterMenuTree = (menuList) => {
    return menuList.filter(menu => {
        let match = true
        if (searchForm.menu_name && !menu.menu_name.includes(searchForm.menu_name)) {
            match = false
        }
        if (searchForm.menu_type && menu.menu_type !== searchForm.menu_type) {
            match = false
        }
        if (searchForm.status && menu.status !== searchForm.status) {
            match = false
        }
        if (match && menu.children && menu.children.length > 0) {
            menu.children = filterMenuTree(menu.children)
            // 如果父节点不匹配，但子节点匹配，则显示父节点
            if (!menu.menu_name.includes(searchForm.menu_name) && menu.children.length > 0) {
                return true
            }
        }
        return match
    })
}

// 查询
const handleSearch = () => {
    loadData()
}

// 重置
const handleReset = () => {
    searchForm.menu_name = ''
    searchForm.menu_type = ''
    searchForm.status = ''
    loadData()
}

// 展开/收起全部
const toggleExpandAll = () => {
    expandAll.value = !expandAll.value
    setExpandAll(tableData.value, expandAll.value)
}

// 递归设置展开状态
const setExpandAll = (menuList, expanded) => {
    menuList.forEach(menu => {
        menu.expanded = expanded
        if (menu.children && menu.children.length > 0) {
            setExpandAll(menu.children, expanded)
        }
    })
}

// 更新可见性
const updateVisible = (row) => {
    updateData({
        id: row.id,
        visible: row.visible
    }).then(res => {
        if (res.data.code === 200) {
            ElMessage.success('更新成功')
        } else {
            ElMessage.error(res.data.msg || '更新失败')
            // 恢复原值
            row.visible = row.visible === '0' ? '1' : '0'
        }
    }).catch(() => {
        ElMessage.error('更新失败，请稍后重试')
        row.visible = row.visible === '0' ? '1' : '0'
    })
}

// 打开表单 （编辑/新增）
// menuId: 要编辑的菜单ID，-1表示新增
// parentId: 上级菜单ID，用于新增时设置父菜单
const onDataForm = (menuId, parentId) => {
    let params_data = {}
    if (menuId > 0) {
        // 编辑
        params_data = { id: menuId }
    } else if (parentId !== null) {
        // 新增子菜单
        params_data = { parent_id: parentId }
    }
    router.push({
        path: '/menuForm',
        query: params_data
    })
}

// 删除数据
const onDelete = (menuId, menu) => {
    // 检查是否有子菜单
    if (menu.children && menu.children.length > 0) {
        ElMessage.warning('该菜单下有子菜单，无法删除')
        return
    }
    
    ElMessageBox.confirm(
        `确定要删除菜单"${menu.menu_name}"吗？`,
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(menuId).then((res) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.msg || '删除失败')
            }
        }).catch(() => {
            ElMessage.error('删除失败，请稍后重试')
        })
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

loadData()
</script>

<style scoped>
.search-card {
  margin-bottom: 16px;
}

.search-form {
  margin-bottom: 0;
}

.menu-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-icon {
  color: var(--el-color-primary);
}

@media (max-width: 768px) {
  .search-form {
    display: block;
  }
  
  .search-form .el-form-item {
    margin-bottom: 12px;
  }
}
</style>

