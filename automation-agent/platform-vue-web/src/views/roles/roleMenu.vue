<template>
    <Breadcrumb />
    <el-card class="box-card">
        <template #header>
            <div class="card-header">
                <span>角色: {{ roleName }}</span>
                <el-button type="primary" @click="saveMenus()">保存</el-button>
            </div>
        </template>
        <el-tree
            ref="treeRef"
            :data="menuTree"
            show-checkbox
            node-key="id"
            :default-checked-keys="checkedKeys"
            :props="defaultProps"
        />
    </el-card>
</template>

<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import roleApi from './roleApi'

const router = useRouter()
const treeRef = ref()
const menuTree = ref([])
const checkedKeys = ref([])
const defaultProps = {
    children: 'children',
    label: 'name'
}

const roleId = router.currentRoute.value.query.id
const roleName = router.currentRoute.value.query.name || ''

const loadMenus = async () => {
    const res = await roleApi.queryMenus(roleId)
    if (res.data.data) {
        menuTree.value = buildTree(res.data.data)
        checkedKeys.value = res.data.data.filter((m) => m.checked).map((m) => m.id)
    }
}

const buildTree = (menus) => {
    const map = {}
    const roots = []
    menus.forEach((m) => {
        map[m.id] = { ...m, children: [] }
    })
    menus.forEach((m) => {
        if (m.parent_id === 0 || !map[m.parent_id]) {
            roots.push(map[m.id])
        } else {
            if (map[m.parent_id]) {
                map[m.parent_id].children.push(map[m.id])
            }
        }
    })
    return roots
}

const saveMenus = () => {
    const menu_ids = treeRef.value.getCheckedKeys()
    roleApi.updateMenus({ id: roleId, menu_ids }).then((res) => {
        if (res.data.code == 200) {
            router.push('/roleList')
        }
    })
}

onMounted(() => {
    loadMenus()
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
