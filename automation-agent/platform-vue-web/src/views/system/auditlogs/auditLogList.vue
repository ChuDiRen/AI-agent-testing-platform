<template>
  <div>
    <Breadcrumb />
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="根据用户名筛选" />
        </el-form-item>
        <el-form-item label="模块">
            <el-input v-model="searchForm.module" placeholder="根据模块筛选" />
        </el-form-item>
        <el-form-item label="请求方法">
            <el-select v-model="searchForm.method" placeholder="选择方法">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
            </el-select>
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="danger" @click="onClear()">清空日志</el-button>
        </el-row>
    </el-form>

    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
            :show-overflow-tooltip="true" />
        <el-table-column label="方法" width="80">
            <template #default="scope">
                <el-tag :type="getMethodType(scope.row.method)">{{ scope.row.method }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
            <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDetail(scope.$index)">
                    详情
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

    <el-dialog v-model="detailVisible" title="日志详情" width="60%">
        <el-descriptions :column="2" border>
            <el-descriptions-item label="ID">{{ currentLog.id }}</el-descriptions-item>
            <el-descriptions-item label="用户名">{{ currentLog.username }}</el-descriptions-item>
            <el-descriptions-item label="模块">{{ currentLog.module }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ currentLog.summary }}</el-descriptions-item>
            <el-descriptions-item label="方法">{{ currentLog.method }}</el-descriptions-item>
            <el-descriptions-item label="路径">{{ currentLog.path }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ currentLog.status }}</el-descriptions-item>
            <el-descriptions-item label="响应时间">{{ currentLog.response_time }}ms</el-descriptions-item>
            <el-descriptions-item label="IP地址" :span="2">{{ currentLog.ip }}</el-descriptions-item>
            <el-descriptions-item label="请求参数" :span="2">
                <pre>{{ currentLog.request_data }}</pre>
            </el-descriptions-item>
            <el-descriptions-item label="响应数据" :span="2">
                <pre>{{ currentLog.response_data }}</pre>
            </el-descriptions-item>
        </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import auditLogApi from './auditLogApi'
import Breadcrumb from "../Breadcrumb.vue"

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ "username": "", "module": "", "method": "" })
const tableData = ref([])
const detailVisible = ref(false)
const currentLog = ref({})

const getMethodType = (method) => {
    const types = { GET: '', POST: 'success', PUT: 'warning', DELETE: 'danger' }
    return types[method] || ''
}

const getStatusType = (status) => {
    if (status >= 200 && status < 300) return 'success'
    if (status >= 400 && status < 500) return 'warning'
    if (status >= 500) return 'danger'
    return 'info'
}

const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    auditLogApi.queryByPage(searchData).then((res) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}
loadData()

const columnList = ref([
    { prop: "id", label: '日志ID' },
    { prop: "username", label: '用户名' },
    { prop: "module", label: '模块' },
    { prop: "summary", label: '描述' },
    { prop: "response_time", label: '响应时间' }
])

const handleSizeChange = (val) => {
    pageSize.value = val
    loadData()
}

const handleCurrentChange = (val) => {
    currentPage.value = val
    loadData()
}

const onDetail = (index) => {
    currentLog.value = tableData.value[index]
    detailVisible.value = true
}

const onClear = async () => {
    try {
        await ElMessageBox.confirm('确定要清空所有日志吗?', '警告', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        const res = await auditLogApi.clearData()
        if (res.data.code === 200) {
            ElMessage.success('清空成功')
            loadData()
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('清空失败:', error)
        }
    }
}
</script>

<style scoped>
.demo-pagination-block {
    margin-top: 20px;
}
pre {
    background: #f5f5f5;
    padding: 10px;
    border-radius: 4px;
    max-height: 200px;
    overflow: auto;
}
</style>
