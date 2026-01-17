<template>
  <div>
    <Breadcrumb />
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="部门名称">
            <el-input v-model="searchForm.name" placeholder="根据部门名称筛选" />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>

    <el-table :data="tableData" style="width: 100%;" row-key="id" :tree-props="{ children: 'children' }">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="部门名称" />
        <el-table-column prop="desc" label="备注" />
        <el-table-column prop="order" label="排序" width="100" align="center" />
        <el-table-column fixed="right" label="操作" width="200">
            <template #default="scope">
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
import deptApi from './deptApi'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const searchForm = reactive({ "name": "" })
const tableData = ref([])

const loadData = async () => {
    try {
        const params = searchForm.name ? { name: searchForm.name } : {}
        const res = await deptApi.queryTree(params)
        if (res.data.code === 200) {
            // 确保数据是数组格式
            const data = res.data.data
            tableData.value = Array.isArray(data) ? data : (data ? [data] : [])
        }
    } catch (error) {
        console.error('加载部门列表失败:', error)
        tableData.value = []
    }
}

onMounted(() => {
    loadData()
})

const onDelete = (row) => {
    ElMessageBox.confirm('确定要删除该部门吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        deptApi.deleteData(row.id).then((res) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            }
        })
    }).catch(() => {})
}

const onDataForm = (index) => {
    router.push({
        path: '/deptForm',
        query: {}
    })
}

const onEdit = (row) => {
    router.push({
        path: '/deptForm',
        query: { id: row.id }
    })
}
</script>

<style scoped>
.demo-pagination-block {
    margin-top: 20px;
}
</style>
