<template>
  <div>
    <Breadcrumb />
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="角色名称">
            <el-input v-model="searchForm.name" placeholder="根据角色名称筛选" />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>

    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
            :show-overflow-tooltip="true" />
        <el-table-column fixed="right" label="操作" width="280">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
                    编辑
                </el-button>
                <el-button link type="success" size="small" @click.prevent="onPermission(scope.$index)">
                    设置权限
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
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import roleApi from './roleApi'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ "name": "" })
const tableData = ref([])

const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    roleApi.queryByPage(searchData).then((res) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}
loadData()

const columnList = ref([
    { prop: "id", label: '角色ID' },
    { prop: "name", label: '角色名称' },
    { prop: "desc", label: '角色描述' },
    { prop: "created_at", label: '创建时间' }
])

const onDelete = async (index) => {
    const roleId = tableData.value[index]["id"]
    const roleName = tableData.value[index]["name"]
    
    await confirmDelete(
        () => roleApi.deleteData(roleId),
        `确定要删除角色 "${roleName}" 吗？此操作不可恢复！`,
        '角色删除成功',
        loadData
    )
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
        path: '/roleForm',
        query: params_data
    })
}

// 设置权限 - 跳转到权限配置页面
const onPermission = (index) => {
    router.push({
        path: '/rolePermission',
        query: { id: tableData.value[index]["id"], name: tableData.value[index]["name"] }
    })
}

// 菜单配置
const onMenus = (index) => {
    router.push({
        path: '/roleMenu',
        query: { id: tableData.value[index]["id"], name: tableData.value[index]["name"] }
    })
}

// API配置
const onApis = (index) => {
    router.push({
        path: '/roleApi',
        query: { id: tableData.value[index]["id"], name: tableData.value[index]["name"] }
    })
}
</script>

<style scoped>
.demo-pagination-block {
    margin-top: 20px;
}
</style>
