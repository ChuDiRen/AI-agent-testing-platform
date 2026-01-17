<template>
  <div>
    <Breadcrumb />
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="菜单名称">
            <el-input v-model="searchForm.name" placeholder="根据菜单名称筛选" />
        </el-form-item>
        <el-form-item label="菜单类型">
            <el-select v-model="searchForm.menu_type" placeholder="选择类型">
                <el-option label="目录" value="catalog" />
                <el-option label="菜单" value="menu" />
            </el-select>
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>

    <el-table :data="tableData" style="width: 100%;" row-key="id" :tree-props="{ children: 'children' }">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="菜单名称" width="200" />
        <el-table-column label="菜单类型" width="100">
            <template #default="scope">
                <el-tag :type="scope.row.menu_type === 'catalog' ? 'info' : 'success'">
                    {{ scope.row.menu_type === 'catalog' ? '目录' : '菜单' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column label="图标" width="80" align="center">
            <template #default="scope">
                <el-icon v-if="scope.row.icon" :size="20">
                    <component :is="scope.row.icon" />
                </el-icon>
            </template>
        </el-table-column>
        <el-table-column prop="path" label="访问路径" width="200" />
        <el-table-column prop="component" label="组件路径" width="200" />
        <el-table-column prop="redirect" label="跳转路径" width="150" />
        <el-table-column prop="order" label="排序" width="80" align="center" />
        <el-table-column label="隐藏" width="80" align="center">
            <template #default="scope">
                <el-switch v-model="scope.row.is_hidden" @change="handleToggleHidden(scope.row)" />
            </template>
        </el-table-column>
        <el-table-column label="保活" width="80" align="center">
            <template #default="scope">
                <el-switch v-model="scope.row.keepalive" @change="handleToggleKeepalive(scope.row)" />
            </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="250">
            <template #default="scope">
                <el-button v-if="scope.row.menu_type === 'catalog'" link type="success" size="small" 
                    @click.prevent="onAddChild(scope.row)">
                    添加子菜单
                </el-button>
                <el-button link type="primary" size="small" @click.prevent="onEdit(scope.row)">
                    编辑
                </el-button>
                <el-button v-if="!scope.row.children || scope.row.children.length === 0" 
                    link type="danger" size="small" @click.prevent="onDelete(scope.row)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import menuApi from './menuApi'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const searchForm = reactive({ "name": "", "menu_type": "" })
const tableData = ref([])

const loadData = async () => {
    try {
        const res = await menuApi.queryTree()
        if (res.data.code === 200) {
            // 确保数据是数组格式
            const data = res.data.data
            tableData.value = Array.isArray(data) ? data : (data ? [data] : [])
        }
    } catch (error) {
        console.error('加载菜单列表失败:', error)
        tableData.value = []
    }
}

onMounted(() => {
    loadData()
})

const onDelete = (row) => {
    ElMessageBox.confirm('确定要删除该菜单吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        menuApi.deleteData(row.id).then((res) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            }
        })
    }).catch(() => {})
}

const handleToggleHidden = async (row) => {
    try {
        const res = await menuApi.updateData(row)
        if (res.data.code === 200) {
            ElMessage.success(row.is_hidden ? '已隐藏' : '已显示')
        }
    } catch (error) {
        row.is_hidden = !row.is_hidden
        console.error('更新失败:', error)
    }
}

const handleToggleKeepalive = async (row) => {
    try {
        const res = await menuApi.updateData(row)
        if (res.data.code === 200) {
            ElMessage.success(row.keepalive ? '已开启保活' : '已关闭保活')
        }
    } catch (error) {
        row.keepalive = !row.keepalive
        console.error('更新失败:', error)
    }
}

const onDataForm = (index) => {
    router.push({
        path: '/menuForm',
        query: {}
    })
}

const onEdit = (row) => {
    router.push({
        path: '/menuForm',
        query: { id: row.id }
    })
}

const onAddChild = (row) => {
    router.push({
        path: '/menuForm',
        query: { parent_id: row.id }
    })
}
</script>

<style scoped>
.demo-pagination-block {
    margin-top: 20px;
}
</style>
