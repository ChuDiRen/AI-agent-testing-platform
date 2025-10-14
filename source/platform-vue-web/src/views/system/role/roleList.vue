<template>
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="角色名称">
            <el-input v-model="searchForm.role_name" placeholder="根据角色名称筛选" />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增角色</el-button>
        </el-row>
    </el-form>
    <!-- END 搜索表单 -->
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
            :show-overflow-tooltip="true" />
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
    <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
    </div>
    <!-- END 分页 -->

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
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryByPage, deleteData, assignMenus, getRoleMenus } from './role'
import { getMenuTree } from '../menu/menu'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'

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

    queryByPage(searchData).then((res: { data: { data: never[]; total: number; msg: string }; }) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}
loadData()

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
    deleteData(tableData.value[index]["id"]).then((res: {}) => {
        loadData()
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
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}
</style>

