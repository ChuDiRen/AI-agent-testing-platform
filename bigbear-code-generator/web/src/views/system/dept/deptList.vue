<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="部门名称">
          <el-input
            v-model="searchForm.dept_name"
            placeholder="请输入部门名称"
            clearable
            @clear="loadData"
            style="width: 200px"
          />
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
      title="部门管理"
      :data="tableData"
      :loading="loading"
      :show-pagination="false"
      :show-expand-toggle="true"
      row-key="id"
      :tree-props="{ children: 'children' }"
      @refresh="loadData"
    >
      <template #header>
        <el-button v-permission="'system:dept:view'" @click="loadData()">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" v-permission="'system:dept:add'" @click="onDataForm(-1, 0)">
          <el-icon><Plus /></el-icon>
          新增部门
        </el-button>
        <el-button type="success" @click="toggleExpandAll">
          <el-icon><DCaret v-if="!expandAll" /><UCaret v-else /></el-icon>
          {{ expandAll ? '收起' : '展开' }}全部
        </el-button>
      </template>

      <el-table-column prop="dept_name" label="部门名称" min-width="300">
        <template #default="scope">
          <div class="dept-name-cell">
            <el-icon class="dept-icon" :size="16"><OfficeBuilding /></el-icon>
            <span>{{ scope.row.dept_name }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="leader" label="负责人" width="120" align="center">
        <template #default="scope">
          <el-tag v-if="scope.row.leader" size="small" type="primary">{{ scope.row.leader }}</el-tag>
          <span v-else style="color: var(--el-text-color-placeholder);">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="联系电话" width="140" align="center">
        <template #default="scope">
          <span v-if="scope.row.phone">{{ scope.row.phone }}</span>
          <span v-else style="color: var(--el-text-color-placeholder);">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="order_num" label="排序" width="80" align="center">
        <template #default="scope">
          <el-tag size="small" type="info">{{ scope.row.order_num }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80" align="center">
        <template #default="scope">
          <el-tag v-if="scope.row.status === '0'" type="success" size="small">正常</el-tag>
          <el-tag v-else type="danger" size="small">停用</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180" align="center">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="220" align="center">
        <template #default="scope">
          <el-button link type="primary" size="small" v-permission="'system:dept:add'" @click.prevent="onDataForm(-1, scope.row.id)">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
          <el-button link type="warning" size="small" v-permission="'system:dept:edit'" @click.prevent="onDataForm(scope.row.id, null)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="danger" size="small" v-permission="'system:dept:delete'" @click.prevent="onDelete(scope.row.id, scope.row)">
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
import { getDeptTree, deleteData } from './dept'
import { formatDateTime } from '~/utils/timeFormatter'
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
    dept_name: '',
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
    getDeptTree().then((res) => {
        if (res.data.code === 200) {
            let data = res.data.data || []
            // 客户端筛选
            data = filterDeptTree(data)
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

// 客户端筛选部门树
const filterDeptTree = (deptList) => {
    return deptList.filter(dept => {
        let match = true
        if (searchForm.dept_name && !dept.dept_name.includes(searchForm.dept_name)) {
            match = false
        }
        if (searchForm.status && dept.status !== searchForm.status) {
            match = false
        }
        if (match && dept.children && dept.children.length > 0) {
            dept.children = filterDeptTree(dept.children)
            // 如果父节点不匹配，但子节点匹配，则显示父节点
            if (!dept.dept_name.includes(searchForm.dept_name) && dept.children.length > 0) {
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
    searchForm.dept_name = ''
    searchForm.status = ''
    loadData()
}

// 展开/收起全部
const toggleExpandAll = () => {
    expandAll.value = !expandAll.value
    setExpandAll(tableData.value, expandAll.value)
}

// 递归设置展开状态
const setExpandAll = (deptList, expanded) => {
    deptList.forEach(dept => {
        dept.expanded = expanded
        if (dept.children && dept.children.length > 0) {
            setExpandAll(dept.children, expanded)
        }
    })
}

// 打开表单 （编辑/新增）
// deptId: 要编辑的部门ID，-1表示新增
// parentId: 上级部门ID，用于新增时设置父部门
const onDataForm = (deptId, parentId) => {
    let params_data = {}
    if (deptId > 0) {
        // 编辑
        params_data = { id: deptId }
    } else if (parentId !== null) {
        // 新增子部门
        params_data = { parent_id: parentId }
    }
    router.push({
        path: '/deptForm',
        query: params_data
    })
}

// 删除数据
const onDelete = (deptId, dept) => {
    // 检查是否有子部门
    if (dept.children && dept.children.length > 0) {
        ElMessage.warning('该部门下有子部门，无法删除')
        return
    }
    
    ElMessageBox.confirm(
        `确定要删除部门"${dept.dept_name}"吗？`,
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(deptId).then((res) => {
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

.dept-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dept-icon {
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

