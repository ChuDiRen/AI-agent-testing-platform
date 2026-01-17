<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <!-- 搜索表单 -->
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="根据用户名筛选" />
        </el-form-item>
        <el-form-item label="邮箱">
            <el-input v-model="searchForm.email" placeholder="根据邮箱筛选" />
        </el-form-item>
        <el-form-item label="部门">
            <el-tree-select v-model="searchForm.dept_id" :data="deptOptions" :props="{ label: 'name', value: 'id' }"
                placeholder="选择部门" clearable check-strictly />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end"> <!-- 居右 type="flex" justify="end" -->
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>
    <!-- END 搜索表单 -->

      <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <!-- 数据列 -->
        <!-- 默认情况下，如果单元格内容过长，会占用多行显示。 若需要单行显示可以使用 show-overflow-tooltip -->
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="alias" label="姓名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column label="角色" width="200">
            <template #default="scope">
                <el-tag v-for="role in scope.row.roles" :key="role.id" type="info" style="margin: 2px">
                    {{ role.name }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column label="部门" width="150">
            <template #default="scope">
                {{ scope.row.dept?.name || '-' }}
            </template>
        </el-table-column>
        <el-table-column label="超级用户" width="100" align="center">
            <template #default="scope">
                <el-tag :type="scope.row.is_superuser ? 'success' : 'info'">
                    {{ scope.row.is_superuser ? '是' : '否' }}
                </el-tag>
            </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
            <template #default="scope">
                <el-switch v-model="scope.row.is_active" :active-value="true" :inactive-value="false"
                    @change="handleStatusChange(scope.row)" />
            </template>
        </el-table-column>
        <el-table-column prop="last_login" label="最后登录" width="180" />
        <el-table-column fixed="right" label="操作" width="280">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
                    编辑
                </el-button>
                <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
                    删除
                </el-button>
                <el-button v-if="!scope.row.is_superuser" link type="warning" size="small"
                    @click.prevent="onResetPassword(scope.$index)">
                    重置密码
                </el-button>
            </template>
        </el-table-column>
    </el-table>
    <!--END  数据表格 -->

    <!-- 分页 -->
    <div class="demo-pagination-block">
        <el-pagination 
        v-model:current-page="currentPage" 
        v-model:page-size="pageSize" 
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
    <!-- END 分页 -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import userApi from './userApi'
import deptApi from '../depts/deptApi'
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ username: "", email: "", dept_id: null })
const tableData = ref([])
const deptOptions = ref([])

const loadData = () => {
    let searchData = { ...searchForm }
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    userApi.queryByPage(searchData).then((res) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}

const loadDeptOptions = async () => {
    try {
        const res = await deptApi.queryTree()
        if (res.data.code === 200) {
            // 确保数据是数组格式，用于 el-tree-select
            const data = res.data.data
            deptOptions.value = Array.isArray(data) ? data : (data ? [data] : [])
        }
    } catch (error) {
        console.error('加载部门列表失败:', error)
        deptOptions.value = []
    }
}

onMounted(() => {
    loadData()
    loadDeptOptions()
})

const onDelete = (index) => {
    ElMessageBox.confirm('确定要删除该用户吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        userApi.deleteData(tableData.value[index]["id"]).then(() => {
            ElMessage.success('删除成功')
            loadData()
        })
    }).catch(() => {})
}

const handleStatusChange = async (row) => {
    try {
        const res = await userApi.updateData({
            id: row.id,
            username: row.username,
            email: row.email,
            is_active: row.is_active,
            role_ids: row.roles?.map((r) => r.id) || [],
            dept_id: row.dept?.id || null
        })
        if (res.data.code === 200) {
            ElMessage.success(row.is_active ? '已启用' : '已禁用')
        }
    } catch (error) {
        row.is_active = !row.is_active
        console.error('更新状态失败:', error)
    }
}

const onResetPassword = async (index) => {
    try {
        await ElMessageBox.confirm('确定要重置该用户密码为123456吗?', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        })
        const res = await userApi.resetPassword({ user_id: tableData.value[index]["id"] })
        if (res.data.code === 200) {
            ElMessage.success('密码已重置为123456')
        }
    } catch (error) {
        if (error !== 'cancel') {
            console.error('重置密码失败:', error)
        }
    }
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
        path: '/userForm',
        query: params_data
    })
}
</script>

<style scoped>
.demo-pagination-block{
    margin-top: 20px;
}
</style>