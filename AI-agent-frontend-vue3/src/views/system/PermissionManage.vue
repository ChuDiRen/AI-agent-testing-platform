<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="permission-manage-container">
    <el-card>
      <template #header>
        <div class="header">
          <h3>权限管理</h3>
          <el-select v-model="selectedRoleId" placeholder="选择角色" @change="handleRoleChange" style="width: 200px">
            <el-option v-for="role in roles" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </div>
      </template>

      <el-row :gutter="20" v-if="selectedRoleId">
        <!-- 菜单权限 -->
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>菜单权限</span>
                <el-button type="primary" size="small" @click="savePermissions">保存</el-button>
              </div>
            </template>
            <el-tree
              ref="menuTreeRef"
              :data="menuTree"
              show-checkbox
              node-key="id"
              :default-checked-keys="selectedMenuIds"
              :props="{ children: 'children', label: 'name' }"
            />
          </el-card>
        </el-col>

        <!-- API权限 -->
        <el-col :span="12">
          <el-card shadow="never">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center">
                <span>API权限</span>
                <el-input
                  v-model="apiSearchKeyword"
                  placeholder="搜索API"
                  clearable
                  style="width: 200px"
                  @input="handleApiSearch"
                />
              </div>
            </template>
            <div style="max-height: 600px; overflow-y: auto">
              <el-tree
                ref="apiTreeRef"
                :data="apiTree"
                show-checkbox
                node-key="id"
                :default-checked-keys="selectedApiIds"
                :props="{ children: 'children', label: 'label' }"
                :filter-node-method="filterApiNode"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-else description="请选择角色以配置权限" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElTree } from 'element-plus'
import type { Role } from '@/api/role'
import type { Menu, Permission } from '@/api/permission'
import { getRoleList } from '@/api/role'
import { getApiList, getMenuList, getRolePermissions, updateRolePermissions } from '@/api/permission'

// 角色列表
const roles = ref<Role[]>([])
const selectedRoleId = ref<number>()

// 菜单权限
const menuTree = ref<Menu[]>([])
const selectedMenuIds = ref<number[]>([])
const menuTreeRef = ref<InstanceType<typeof ElTree>>()

// API权限
const apiTree = ref<any[]>([])
const selectedApiIds = ref<number[]>([])
const apiTreeRef = ref<InstanceType<typeof ElTree>>()
const apiSearchKeyword = ref('')

// 加载角色列表
const loadRoles = async () => {
  try {
    const res = await getRoleList({ page: 1, page_size: 1000 })
    if (res.data.code === 200) {
      roles.value = res.data.data.items
    }
  } catch (error) {
    ElMessage.error('加载角色列表失败')
  }
}

// 加载菜单列表
const loadMenus = async () => {
  try {
    const res = await getMenuList()
    if (res.data.code === 200) {
      menuTree.value = buildMenuTree(res.data.data.items)
    }
  } catch (error) {
    ElMessage.error('加载菜单列表失败')
  }
}

// 加载API列表
const loadApis = async () => {
  try {
    const res = await getApiList({ page: 1, page_size: 10000 })
    if (res.data.code === 200) {
      apiTree.value = buildApiTree(res.data.data.items)
    }
  } catch (error) {
    ElMessage.error('加载API列表失败')
  }
}

// 构建菜单树
const buildMenuTree = (menus: Menu[]): Menu[] => {
  const map = new Map<number, Menu>()
  const roots: Menu[] = []

  menus.forEach((menu) => {
    map.set(menu.id, { ...menu, children: [] })
  })

  menus.forEach((menu) => {
    const node = map.get(menu.id)!
    if (menu.parent_id && map.has(menu.parent_id)) {
      const parent = map.get(menu.parent_id)!
      parent.children = parent.children || []
      parent.children.push(node)
    } else {
      roots.push(node)
    }
  })

  return roots
}

// 构建API树（按模块分组）
const buildApiTree = (apis: Permission[]): any[] => {
  const groups = new Map<string, Permission[]>()

  apis.forEach((api) => {
    const module = api.tags || '其他'
    if (!groups.has(module)) {
      groups.set(module, [])
    }
    groups.get(module)!.push(api)
  })

  const tree: any[] = []
  let nodeId = 100000 // 使用大数字作为分组节点ID，避免与真实API ID冲突

  groups.forEach((apiList, moduleName) => {
    const moduleNode = {
      id: nodeId++,
      label: moduleName,
      isGroup: true,
      children: apiList.map((api) => ({
        id: api.id,
        label: `${api.method} ${api.path}`,
        summary: api.summary,
        isGroup: false
      }))
    }
    tree.push(moduleNode)
  })

  return tree
}

// 加载角色权限
const loadRolePermissions = async (roleId: number) => {
  try {
    const res = await getRolePermissions(roleId)
    if (res.data.code === 200) {
      const { menus, apis } = res.data.data
      selectedMenuIds.value = menus.map((m) => m.id)
      selectedApiIds.value = apis.map((a) => a.id)

      // 等待DOM更新后设置树的选中状态
      await nextTick()
      menuTreeRef.value?.setCheckedKeys(selectedMenuIds.value)
      apiTreeRef.value?.setCheckedKeys(selectedApiIds.value)
    }
  } catch (error) {
    ElMessage.error('加载角色权限失败')
  }
}

// 角色切换
const handleRoleChange = (roleId: number) => {
  if (roleId) {
    loadRolePermissions(roleId)
  }
}

// API搜索
const handleApiSearch = (keyword: string) => {
  apiTreeRef.value?.filter(keyword)
}

const filterApiNode = (value: string, data: any) => {
  if (!value) return true
  if (data.isGroup) return true
  return data.label.toLowerCase().includes(value.toLowerCase())
}

// 保存权限
const savePermissions = async () => {
  if (!selectedRoleId.value) {
    ElMessage.warning('请选择角色')
    return
  }

  try {
    // 获取选中的菜单ID（包括半选中的父节点）
    const checkedMenuKeys = menuTreeRef.value?.getCheckedKeys() || []
    const halfCheckedMenuKeys = menuTreeRef.value?.getHalfCheckedKeys() || []
    const menuIds = [...checkedMenuKeys, ...halfCheckedMenuKeys] as number[]

    // 获取选中的API ID（过滤掉分组节点）
    const checkedApiKeys = apiTreeRef.value?.getCheckedKeys() || []
    const apiIds = (checkedApiKeys as number[]).filter((id) => id < 100000)

    const res = await updateRolePermissions({
      role_id: selectedRoleId.value,
      menu_ids: menuIds,
      api_ids: apiIds
    })

    if (res.data.code === 200) {
      ElMessage.success('权限保存成功')
    } else {
      ElMessage.error(res.data.msg || '权限保存失败')
    }
  } catch (error) {
    ElMessage.error('权限保存失败')
  }
}

onMounted(() => {
  loadRoles()
  loadMenus()
  loadApis()
})
</script>

<style scoped>
.permission-manage-container {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h3 {
  margin: 0;
}
</style>


