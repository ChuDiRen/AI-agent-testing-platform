<template>
  <div>
    <Breadcrumb />
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="API路径">
            <el-input v-model="searchForm.path" placeholder="根据路径筛选" />
        </el-form-item>
        <el-form-item label="请求方法">
            <el-select v-model="searchForm.method" placeholder="选择方法">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
            </el-select>
        </el-form-item>
        <el-form-item label="标签">
            <el-input v-model="searchForm.tags" placeholder="根据标签筛选" />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="handleRefresh">刷新API</el-button>
            <el-button type="success" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>

    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
            :show-overflow-tooltip="true" />
        <el-table-column label="方法" width="100">
            <template #default="scope">
                <el-tag :type="getMethodType(scope.row.method)">{{ scope.row.method }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
                    编辑
                </el-button>
                <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>

    <div class="demo-pagination-block">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import apiApi from './apiApi'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ "path": "", "method": "", "tags": "" })
const tableData = ref([])

const getMethodType = (method) => {
    const types = { GET: 'success', POST: 'primary', PUT: 'warning', DELETE: 'danger', PATCH: 'info' }
    return types[method] || 'info'
}

const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    apiApi.queryByPage(searchData).then((res) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}
loadData()

const columnList = ref([
    { prop: "id", label: 'API ID' },
    { prop: "path", label: 'API路径' },
    { prop: "summary", label: '描述' },
    { prop: "tags", label: '标签' },
    { prop: "created_at", label: '创建时间' }
])

const handleRefresh = async () => {
    try {
        await ElMessageBox.confirm('此操作会根据后端路由进行更新，确定继续刷新API操作？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        const res = await apiApi.refreshApi()
        if (res.data.code === 200) {
            ElMessage.success('刷新成功')
            loadData()
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('刷新失败:', error)
        }
    }
}

const onDelete = (index) => {
    ElMessageBox.confirm('确定要删除该API吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        apiApi.deleteData(tableData.value[index]["id"]).then(() => {
            ElMessage.success('删除成功')
            loadData()
        })
    }).catch(() => {})
}

const handleSizeChange = (val) => {
    pageSize.value = val
    loadData()
}

const handleCurrentChange = (val) => {
    currentPage.value = val
    loadData()
}

const onDataForm = (index) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: '/apiForm',
        query: params_data
    })
}
</script>

<style scoped>
.demo-pagination-block {
    margin-top: 20px;
}
</style>
