<template>
  <div class="page-container">
    <BaseSearch 
      :model="searchForm" 
      @search="loadData" 
      @reset="resetSearch"
    >
      <el-form-item label="角色名称">
        <el-input v-model="searchForm.role_name" placeholder="根据角色名称筛选" />
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="角色管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
      </template>

      <el-table-column prop="id" label="角色ID" width="100" />
      <el-table-column prop="role_name" label="角色名称" width="150" show-overflow-tooltip />
      <el-table-column prop="remark" label="角色描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="280">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDataView(scope.$index)">
            查看
          </el-button>
          <el-button link type="success" size="small" @click.prevent="onDataForm(scope.$index)">
            编辑
          </el-button>
          <el-button link type="warning" size="small" @click.prevent="onAssignMenus(scope.$index)">
            分配权限
          </el-button>
          <el-button link type="danger" size="small" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 权限分配对话框 -->
    <el-dialog v-model="menuDialogVisible" title="分配菜单权限" width="400px">
      <el-tree
        ref="menuTreeRef"
        :data="menuTree"
        show-checkbox
        node-key="id"
        :props="{ children: 'children', label: 'menu_name' }"
        default-expand-all
      />
      <template #footer>
        <el-button @click="menuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMenus">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryByPage, deleteData, assignMenus, getRoleMenus } from './role'
import { getMenuTree } from '../menu/menu'
import { formatDateTime } from '~/utils/timeFormatter'
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = reactive({
  page: 1,
  limit: 10
})
const total = ref(0)
const loading = ref(false)

// 搜索功能 - 筛选表单
const searchForm = reactive({ "role_name": null })

// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    loading.value = true
    let searchData = { ...searchForm }
    searchData["page"] = pagination.page
    searchData["pageSize"] = pagination.limit

    queryByPage(searchData).then((res: { data: { code: number; data: never[]; total: number; msg: string }; }) => {
        if (res.data.code === 200) {
            tableData.value = res.data.data || []
            total.value = res.data.total || 0
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch((error: any) => {
        console.error('查询失败:', error)
        ElMessage.error('查询失败，请稍后重试')
    }).finally(() => {
        loading.value = false
    })
}
loadData()

// 重置搜索
const resetSearch = () => {
    searchForm.role_name = null
    pagination.page = 1
    loadData()
}

// 查看角色详情
const onDataView = (index: number) => {
    const item = tableData.value[index]
    router.push({
        path: '/roleForm',
        query: {
            id: item.id,
            view: 'true' // 标记为查看模式
        }
    })
}

// 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: '/roleForm',
        query: params_data
    })
}

// 删除数据
const onDelete = (index: number) => {
    const item = tableData.value[index]
    ElMessageBox.confirm(
        `确定要删除角色"${item.role_name}"吗？`,
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(item.id).then((res: { data: { code: number; msg: string } }) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.msg || '删除失败')
            }
        }).catch((error: any) => {
            console.error('删除失败:', error)
            ElMessage.error('删除失败，请稍后重试')
        })
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

// 权限分配相关
const menuDialogVisible = ref(false)
const menuTreeRef = ref(null)
const menuTree = ref([])
const currentRoleId = ref(null)

// 打开权限分配对话框
const onAssignMenus = async (index: number) => {
    currentRoleId.value = tableData.value[index]["id"]
    
    // 加载菜单树
    const menuRes = await getMenuTree()
    if (menuRes.data.code === 200) {
        menuTree.value = menuRes.data.data
    }
    
    // 加载角色已有权限
    const roleMenuRes = await getRoleMenus(currentRoleId.value)
    if (roleMenuRes.data.code === 200) {
        menuTreeRef.value?.setCheckedKeys(roleMenuRes.data.data)
    }
    
    menuDialogVisible.value = true
}

// 保存菜单权限
const handleSaveMenus = async () => {
    const checkedKeys = menuTreeRef.value.getCheckedKeys()
    const halfCheckedKeys = menuTreeRef.value.getHalfCheckedKeys()
    // 合并全选和半选的节点，并过滤掉null值，确保都是整数
    const menuIds = [...checkedKeys, ...halfCheckedKeys].filter(id => id !== null && id !== undefined)
    
    try {
        const res = await assignMenus({
            id: currentRoleId.value,
            menu_ids: menuIds
        })
        
        if (res.data.code === 200) {
            menuDialogVisible.value = false
            ElMessage.success('权限分配成功')
        } else {
            ElMessage.error(res.data.msg || '权限分配失败')
        }
    } catch (error) {
        console.error('分配权限失败:', error)
        ElMessage.error('分配权限失败，请稍后重试')
    }
}
</script>

<style scoped>
/* 移除原有的样式引用 */
</style>

