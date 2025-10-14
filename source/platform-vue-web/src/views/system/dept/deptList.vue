<template>
    <!-- 操作按钮 -->
    <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">刷新</el-button>
        <el-button type="warning" @click="onDataForm(-1, 0)">新增部门</el-button>
    </el-row>
    <!-- 数据表格 - 树形展示 -->
    <el-table
        :data="tableData"
        row-key="dept_id"
        style="width: 100%"
        default-expand-all
        :tree-props="{ children: 'children' }"
    >
        <el-table-column prop="dept_name" label="部门名称" width="300" />
        <el-table-column prop="order_num" label="排序" width="120" />
        <el-table-column prop="create_time" label="创建时间" />
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作" width="220">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(-1, scope.row.dept_id)">
                    新增
                </el-button>
                <el-button link type="warning" size="small" @click.prevent="onDataForm(scope.row.dept_id, null)">
                    编辑
                </el-button>
                <el-button link type="danger" size="small" @click.prevent="onDelete(scope.row.dept_id)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getDeptTree, deleteData } from './dept'
import { useRouter } from "vue-router"

const router = useRouter()

// 表格数据
const tableData = ref([])

// 加载页面数据（树形结构）
const loadData = () => {
    getDeptTree().then((res: { data: { data: never[]; msg: string }; }) => {
        tableData.value = res.data.data
    })
}
loadData()

// 打开表单 （编辑/新增）
// deptId: 要编辑的部门ID，-1表示新增
// parentId: 上级部门ID，用于新增时设置父部门
const onDataForm = (deptId: number, parentId: number | null) => {
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
const onDelete = (deptId: number) => {
    deleteData(deptId).then((res: {}) => {
        loadData()
    })
}
</script>

<style scoped>
.mb-4 {
    margin-bottom: 16px;
}
</style>

