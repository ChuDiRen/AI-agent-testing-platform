<template>
    <!-- 操作按钮 -->
    <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">刷新</el-button>
        <el-button type="warning" @click="onDataForm(-1, 0)">新增菜单</el-button>
    </el-row>
    <!-- 数据表格 - 树形展示 -->
    <el-table
        :data="tableData"
        row-key="menu_id"
        style="width: 100%"
        default-expand-all
        :tree-props="{ children: 'children' }"
    >
        <el-table-column prop="menu_name" label="菜单名称" width="200" />
        <el-table-column prop="icon" label="图标" width="100" />
        <el-table-column prop="type" label="类型" width="80">
            <template #default="scope">
                <el-tag :type="scope.row.type === '0' ? 'primary' : 'success'">
                    {{ scope.row.type === '0' ? '菜单' : '按钮' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="path" label="路由路径" show-overflow-tooltip />
        <el-table-column prop="component" label="组件路径" show-overflow-tooltip />
        <el-table-column prop="perms" label="权限标识" show-overflow-tooltip />
        <el-table-column prop="order_num" label="排序" width="80" />
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作" width="220">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(-1, scope.row.menu_id)">
                    新增
                </el-button>
                <el-button link type="warning" size="small" @click.prevent="onDataForm(scope.row.menu_id, null)">
                    编辑
                </el-button>
                <el-button link type="danger" size="small" @click.prevent="onDelete(scope.row.menu_id)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getMenuTree, deleteData } from './menu'
import { useRouter } from "vue-router"

const router = useRouter()

// 表格数据
const tableData = ref([])

// 加载页面数据（树形结构）
const loadData = () => {
    getMenuTree().then((res: { data: { data: never[]; msg: string }; }) => {
        tableData.value = res.data.data
    })
}
loadData()

// 打开表单 （编辑/新增）
// menuId: 要编辑的菜单ID，-1表示新增
// parentId: 上级菜单ID，用于新增时设置父菜单
const onDataForm = (menuId: number, parentId: number | null) => {
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
const onDelete = (menuId: number) => {
    deleteData(menuId).then((res: {}) => {
        loadData()
    })
}
</script>

<style scoped>
.mb-4 {
    margin-bottom: 16px;
}
</style>

