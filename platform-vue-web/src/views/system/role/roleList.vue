<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>角色管理</h3>
          <el-button type="primary" @click="onDataForm(-1)">
            <el-icon><Plus /></el-icon>
            新增角色
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="角色名称">
          <el-input v-model="searchForm.role_name" placeholder="根据角色名称筛选" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    <!-- END 搜索表单 -->
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column prop="id" label="角色ID" show-overflow-tooltip />
        <el-table-column prop="role_name" label="角色名称" show-overflow-tooltip />
        <el-table-column prop="remark" label="角色描述" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" show-overflow-tooltip>
            <template #default="scope">
                {{ formatDateTime(scope.row.create_time) }}
            </template>
        </el-table-column>
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作" width="250">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
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
    </el-table>
    
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 权限分配对话框 -->
    <el-dialog v-model="menuDialogVisible" title="分配菜单权限" width="400px">
      <el-tree
        ref="menuTreeRef"
        :data="menuTree"
        show-checkbox
        node-key="menu_id"
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

const router = useRouter()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索功能 - 筛选表单
const searchForm = reactive({ "role_name": null })

// 表格列
const columnList = ref([
    { prop: "id", label: '角色ID' },
    { prop: "role_name", label: '角色名称' },
    { prop: "remark", label: '角色描述' },
    { prop: "create_time", label: '创建时间' }
])
// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

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
    })
}
loadData()

// 重置搜索
const resetSearch = () => {
    searchForm.role_name = null
    currentPage.value = 1
    loadData()
}

// 变更 页大小
const handleSizeChange = (val: number) => {
    console.log("页大小变化:" + val)
    pageSize.value = val
    loadData()
}
// 变更 页码
const handleCurrentChange = (val: number) => {
    console.log("页码变化:" + val)
    currentPage.value = val
    loadData()
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
    const menuIds = [...checkedKeys, ...halfCheckedKeys]
    
    await assignMenus({
        id: currentRoleId.value,
        menu_ids: menuIds
    })
    
    menuDialogVisible.value = false
    ElMessage.success('权限分配成功')
}
</script>

<style scoped>
@import '@/styles/common-list.css';
@import '@/styles/common-form.css';
</style>

