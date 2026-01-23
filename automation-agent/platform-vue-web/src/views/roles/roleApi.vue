<template>
  <div>
    <Breadcrumb />
    <el-card class="box-card">
        <template #header>
            <div class="card-header">
                <span>角色: {{ roleName }}</span>
                <el-button type="primary" @click="saveApis()">保存</el-button>
            </div>
        </template>
        <el-table :data="apiList" style="width: 100%">
            <el-table-column prop="path" label="API路径" width="250" />
            <el-table-column prop="method" label="方法" width="100">
                <template #default="scope">
                    <el-tag :type="getMethodType(scope.row.method)">{{ scope.row.method }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="summary" label="描述" />
            <el-table-column prop="tags" label="标签" width="120" />
            <el-table-column label="勾选" width="100">
                <template #default="scope">
                    <el-checkbox v-model="scope.row.checked" />
                </template>
            </el-table-column>
        </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import roleApi from './roleApi'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const apiList = ref([])
const roleId = router.currentRoute.value.query.id
const roleName = router.currentRoute.value.query.name || ''

const getMethodType = (method) => {
    const types = { GET: '', POST: 'success', PUT: 'warning', DELETE: 'danger', PATCH: 'info' }
    return types[method] || ''
}

const loadApis = async () => {
    const res = await roleApi.queryApis(roleId)
    if (res.data.data) {
        apiList.value = res.data.data
    }
}

const saveApis = () => {
    const api_ids = apiList.value.filter((a) => a.checked).map((a) => a.id)
    roleApi.updateApis({ id: roleId, api_ids }).then((res) => {
        if (res.data.code == 200) {
            router.push('/roleList')
        }
    })
}

onMounted(() => {
    loadApis()
})
</script>

<style scoped>
.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.box-card {
    margin: 20px;
}
</style>
