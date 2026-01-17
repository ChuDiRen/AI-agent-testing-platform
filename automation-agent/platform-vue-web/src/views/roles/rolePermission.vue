<template>
    <div class="role-permission-container">
        <Breadcrumb />
        <el-card>
            <template #header>
                <span>角色权限设置 - {{ roleName }}</span>
            </template>

            <el-tabs v-model="activeTab">
                <el-tab-pane label="菜单权限" name="menu">
                    <el-input v-model="menuFilterText" placeholder="筛选菜单" clearable style="margin-bottom: 20px; width: 300px" />
                    <el-tree ref="menuTreeRef" :data="menuOptions" :props="{ label: 'name', children: 'children' }"
                        :filter-node-method="filterMenuNode" node-key="id" show-checkbox default-expand-all
                        :default-checked-keys="checkedMenuIds" />
                </el-tab-pane>
                <el-tab-pane label="接口权限" name="api">
                    <el-input v-model="apiFilterText" placeholder="筛选接口" clearable style="margin-bottom: 20px; width: 300px" />
                    <el-tree ref="apiTreeRef" :data="apiOptions" :props="{ label: 'summary', children: 'children' }"
                        :filter-node-method="filterApiNode" node-key="unique_id" show-checkbox default-expand-all
                        :default-checked-keys="checkedApiIds" />
                </el-tab-pane>
            </el-tabs>

            <div style="margin-top: 20px">
                <el-button type="primary" @click="handleSave">保存</el-button>
                <el-button @click="handleCancel">取消</el-button>
            </div>
        </el-card>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import menuApi from '../menus/menuApi'
import apiApi from '../apis/apiApi'
import roleApi from './roleApi'
import Breadcrumb from '../Breadcrumb.vue'

const router = useRouter()
const route = useRoute()

const activeTab = ref('menu')
const roleName = ref('')
const roleId = ref(0)
const menuTreeRef = ref(null)
const apiTreeRef = ref(null)
const menuFilterText = ref('')
const apiFilterText = ref('')
const menuOptions = ref([])
const apiOptions = ref([])
const checkedMenuIds = ref([])
const checkedApiIds = ref([])

watch(menuFilterText, (val) => {
    menuTreeRef.value?.filter(val)
})

watch(apiFilterText, (val) => {
    apiTreeRef.value?.filter(val)
})

const filterMenuNode = (value, data) => {
    if (!value) return true
    return data.name.includes(value)
}

const filterApiNode = (value, data) => {
    if (!value) return true
    return data.summary?.includes(value) || data.path?.includes(value)
}

const buildApiTree = (data) => {
    const groupedData = {}
    data.forEach(item => {
        const tags = item.tags || 'Other'
        const path = item.path.split('/').slice(0, -1).join('/')
        const uniqueId = item.method.toLowerCase() + item.path

        if (!groupedData[path]) {
            groupedData[path] = {
                unique_id: path,
                path: path,
                summary: tags,
                children: []
            }
        }

        groupedData[path].children.push({
            id: item.id,
            path: item.path,
            method: item.method,
            summary: item.summary,
            unique_id: uniqueId
        })
    })
    return Object.values(groupedData)
}

const loadData = async () => {
    try {
        const [menuRes, apiRes, authorizedRes] = await Promise.all([
            menuApi.queryTree(),
            apiApi.queryByPage({ page: 1, pageSize: 9999 }),
            roleApi.getRoleAuthorized({ id: roleId.value })
        ])

        if (menuRes.data.code === 200) {
            menuOptions.value = menuRes.data.data
        }

        if (apiRes.data.code === 200) {
            apiOptions.value = buildApiTree(apiRes.data.data)
        }

        if (authorizedRes.data.code === 200) {
            roleName.value = authorizedRes.data.data.name
            checkedMenuIds.value = authorizedRes.data.data.menus?.map(m => m.id) || []
            checkedApiIds.value = authorizedRes.data.data.apis?.map(a => a.method.toLowerCase() + a.path) || []
        }
    } catch (error) {
        console.error('加载权限数据失败:', error)
        ElMessage.error('加载权限数据失败')
    }
}

const handleSave = async () => {
    try {
        const menuIds = menuTreeRef.value.getCheckedKeys()
        const apiCheckedData = apiTreeRef.value.getCheckedNodes()

        const apiInfos = apiCheckedData
            .filter(node => !node.children)
            .map(node => ({
                path: node.path,
                method: node.method
            }))

        const res = await roleApi.updateRoleAuthorized({
            id: roleId.value,
            menu_ids: menuIds,
            api_infos: apiInfos
        })

        if (res.data.code === 200) {
            ElMessage.success('权限设置成功')
            router.push('/roleList')
        }
    } catch (error) {
        console.error('保存权限失败:', error)
        ElMessage.error('保存权限失败')
    }
}

const handleCancel = () => {
    router.push('/roleList')
}

onMounted(() => {
    roleId.value = Number(route.query.id) || 0
    if (roleId.value > 0) {
        loadData()
    }
})
</script>

<style scoped>
.role-permission-container .el-card {
    margin: 20px;
}
</style>
