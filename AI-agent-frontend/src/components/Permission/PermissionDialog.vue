# Copyright (c) 2025 左岚. All rights reserved.
<template>
  <el-dialog
    v-model="visible"
    title="权限配置"
    width="70%"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    @close="handleClose"
  >
    <div class="permission-dialog" v-loading="loading">
      <!-- 角色信息 -->
      <div class="role-info">
        <el-tag type="primary" size="large">
          <el-icon><UserFilled /></el-icon>
          <span>{{ roleInfo?.role_name || '未知角色' }}</span>
        </el-tag>
        <span class="role-desc">{{ roleInfo?.remark || '暂无描述' }}</span>
      </div>

      <!-- 权限配置标签页 -->
      <el-tabs v-model="activeTab" class="permission-tabs">
        <el-tab-pane label="菜单权限" name="menu">
          <div class="menu-permission-container">
            <!-- 操作工具栏 -->
            <div class="toolbar">
              <div class="left-actions">
                <el-checkbox
                  v-model="menuCheckAll"
                  :indeterminate="menuIndeterminate"
                  @change="handleMenuCheckAll"
                  :disabled="loading || treeLoading"
                >
                  全选/反选
                </el-checkbox>
                <el-divider direction="vertical" />
                <el-button
                  type="primary"
                  size="small"
                  :icon="Expand"
                  @click="expandAllMenus"
                  :disabled="loading || treeLoading"
                >
                  展开全部
                </el-button>
                <el-button
                  size="small"
                  :icon="Fold"
                  @click="collapseAllMenus"
                  :disabled="loading || treeLoading"
                >
                  折叠全部
                </el-button>
              </div>
              <div class="right-info">
                <el-text type="info" size="small">
                  已选择 {{ checkedCount }} / {{ totalCount }} 项权限
                </el-text>
              </div>
            </div>

            <!-- 菜单权限树 -->
            <div class="menu-tree-wrapper">
              <el-tree
                ref="menuTreeRef"
                :data="menuTreeData"
                :props="treeProps"
                show-checkbox
                node-key="menu_id"
                :default-expand-all="false"
                :check-strictly="false"
                :expand-on-click-node="false"
                @check="handleMenuCheck"
                class="permission-tree"
                v-loading="treeLoading"
                element-loading-text="加载菜单数据中..."
                empty-text="暂无菜单数据"
              >
                <template #default="{ node, data }">
                  <div class="tree-node">
                    <el-icon v-if="data.icon" class="node-icon">
                      <component :is="data.icon" />
                    </el-icon>
                    <span class="node-label">{{ data.menu_name }}</span>
                    <el-tag
                      v-if="data.menu_type === '1'"
                      size="small"
                      type="warning"
                      class="node-tag"
                    >
                      按钮
                    </el-tag>
                    <el-tag
                      v-else-if="data.menu_type === '0'"
                      size="small"
                      type="success"
                      class="node-tag"
                    >
                      菜单
                    </el-tag>
                  </div>
                </template>
              </el-tree>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 对话框底部操作按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="saving">
          取 消
        </el-button>
        <el-button
          type="primary"
          @click="handleSave"
          :loading="saving"
          :disabled="loading || treeLoading"
        >
          保 存
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage, ElTree } from 'element-plus'
import { UserFilled, Expand, Fold } from '@element-plus/icons-vue'
import { MenuApi } from '@/api/modules/menu'
import { RoleApi } from '@/api/modules/role'
import type { RoleInfo } from '@/api/types'

// 组件属性定义
interface PermissionDialogProps {
  modelValue: boolean
  roleInfo?: RoleInfo | null
}

// 组件事件定义
interface PermissionDialogEmits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = withDefaults(defineProps<PermissionDialogProps>(), {
  modelValue: false,
  roleInfo: null
})

const emit = defineEmits<PermissionDialogEmits>()

// 响应式状态
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false) // 整体加载状态
const treeLoading = ref(false) // 树组件加载状态
const saving = ref(false) // 保存状态
const activeTab = ref('menu') // 当前激活的标签页

// 菜单树相关状态
const menuTreeRef = ref<InstanceType<typeof ElTree>>()
const menuTreeData = ref<any[]>([])
const menuCheckAll = ref(false)
const menuIndeterminate = ref(false)

// 树组件配置
const treeProps = {
  children: 'children',
  label: 'menu_name'
}

// 计算属性
const checkedCount = computed(() => {
  if (!menuTreeRef.value) return 0
  const checkedKeys = menuTreeRef.value.getCheckedKeys(false)
  const halfCheckedKeys = menuTreeRef.value.getHalfCheckedKeys()
  return checkedKeys.length + halfCheckedKeys.length
})

const totalCount = computed(() => {
  const countNodes = (nodes: any[]): number => {
    let count = 0
    for (const node of nodes) {
      count++
      if (node.children && node.children.length > 0) {
        count += countNodes(node.children)
      }
    }
    return count
  }
  return countNodes(menuTreeData.value)
})

// 监听对话框显示状态
watch(visible, async (newVal) => {
  if (newVal && props.roleInfo) {
    // 重置状态
    resetDialogState()
    // 初始化权限数据
    await initPermissionData()
  }
})

// 重置对话框状态
const resetDialogState = () => {
  // 不要清空菜单数据，只重置状态
  menuCheckAll.value = false
  menuIndeterminate.value = false
  saving.value = false
  // 保持 loading 和 treeLoading 状态，让初始化过程控制
}

// 初始化权限数据
const initPermissionData = async () => {
  if (!props.roleInfo) return
  
  try {
    loading.value = true
    
    // 并行加载菜单树和角色权限
    const [menuTreeResult, rolePermissionsResult] = await Promise.allSettled([
      loadMenuTree(),
      loadRolePermissions(props.roleInfo.role_id)
    ])
    
    // 检查加载结果
    if (menuTreeResult.status === 'rejected') {
      console.error('加载菜单树失败:', menuTreeResult.reason)
      ElMessage.error('加载菜单树失败')
      return
    }
    
    if (rolePermissionsResult.status === 'rejected') {
      console.error('加载角色权限失败:', rolePermissionsResult.reason)
      ElMessage.error('加载角色权限失败')
      return
    }
    
    // 设置权限勾选状态
    await setPermissionCheckedState(rolePermissionsResult.value)
    
  } catch (error) {
    console.error('初始化权限数据失败:', error)
    ElMessage.error('初始化权限数据失败')
  } finally {
    loading.value = false
  }
}

// 加载菜单树
const loadMenuTree = async () => {
  try {
    treeLoading.value = true
    const response = await MenuApi.getMenuTree()
    
    if (response.success && response.data) {
      menuTreeData.value = Array.isArray(response.data) ? response.data : []
      console.log('菜单树加载成功，共', menuTreeData.value.length, '个顶级菜单')
    } else {
      menuTreeData.value = []
      throw new Error(response.message || '获取菜单树失败')
    }
  } finally {
    treeLoading.value = false
  }
}

// 加载角色权限
const loadRolePermissions = async (roleId: number): Promise<number[]> => {
  const response = await RoleApi.getRoleMenus(roleId)
  
  if (response.success && response.data) {
    const menuIds = Array.isArray(response.data) ? response.data : []
    console.log('角色权限加载成功，共', menuIds.length, '个权限')
    return menuIds
  } else {
    throw new Error(response.message || '获取角色权限失败')
  }
}

// 设置权限勾选状态
const setPermissionCheckedState = async (menuIds: number[]) => {
  // 等待树组件完全渲染
  await nextTick()

  if (!menuTreeRef.value) {
    console.warn('菜单树组件未准备就绪')
    return
  }

  if (menuIds.length === 0) {
    console.log('角色无权限，清空勾选状态')
    menuTreeRef.value.setCheckedKeys([])
    updateMenuCheckStatus()
    return
  }

  try {
    // 设置勾选状态，使用重试机制
    let retryCount = 0
    const maxRetries = 3

    const setCheckedWithRetry = async () => {
      try {
        menuTreeRef.value?.setCheckedKeys(menuIds)
        console.log('权限勾选状态设置完成，勾选了', menuIds.length, '个权限')

        // 验证设置是否成功
        const checkedKeys = menuTreeRef.value?.getCheckedKeys(false) || []
        if (checkedKeys.length === 0 && menuIds.length > 0 && retryCount < maxRetries) {
          retryCount++
          console.log(`权限设置验证失败，重试第 ${retryCount} 次`)
          await new Promise(resolve => setTimeout(resolve, 100))
          await setCheckedWithRetry()
        }
      } catch (error) {
        if (retryCount < maxRetries) {
          retryCount++
          console.log(`权限设置失败，重试第 ${retryCount} 次:`, error)
          await new Promise(resolve => setTimeout(resolve, 100))
          await setCheckedWithRetry()
        } else {
          throw error
        }
      }
    }

    await setCheckedWithRetry()
  } catch (error) {
    console.error('设置权限勾选状态失败:', error)
    ElMessage.warning('权限状态设置可能不完整，请检查后重新保存')
  }

  // 更新全选状态
  updateMenuCheckStatus()
}

// 获取所有菜单ID
const getAllMenuKeys = (menus: any[]): number[] => {
  const keys: number[] = []
  
  const traverse = (nodes: any[]) => {
    for (const node of nodes) {
      keys.push(node.menu_id)
      if (node.children && node.children.length > 0) {
        traverse(node.children)
      }
    }
  }
  
  traverse(menus)
  return keys
}

// 菜单全选/反选
const handleMenuCheckAll = (checked: boolean) => {
  if (!menuTreeRef.value) return
  
  if (checked) {
    const allKeys = getAllMenuKeys(menuTreeData.value)
    menuTreeRef.value.setCheckedKeys(allKeys)
  } else {
    menuTreeRef.value.setCheckedKeys([])
  }
  
  updateMenuCheckStatus()
}

// 菜单选中变化
const handleMenuCheck = () => {
  updateMenuCheckStatus()
}

// 更新菜单选中状态
const updateMenuCheckStatus = () => {
  if (!menuTreeRef.value) return
  
  const checkedKeys = menuTreeRef.value.getCheckedKeys(false) || []
  const allKeys = getAllMenuKeys(menuTreeData.value)
  
  menuCheckAll.value = checkedKeys.length > 0 && checkedKeys.length === allKeys.length
  menuIndeterminate.value = checkedKeys.length > 0 && checkedKeys.length < allKeys.length
}

// 展开所有菜单
const expandAllMenus = () => {
  if (!menuTreeRef.value || !menuTreeData.value.length) {
    console.warn('菜单树未准备就绪或无数据')
    return
  }

  try {
    // 使用 nextTick 确保 DOM 更新完成
    nextTick(() => {
      const allKeys = getAllMenuKeys(menuTreeData.value)
      console.log('展开所有菜单，节点数量:', allKeys.length)

      // 使用 Element Plus Tree 的内置方法
      allKeys.forEach(key => {
        try {
          const node = menuTreeRef.value?.getNode(key)
          if (node && node.childNodes && node.childNodes.length > 0) {
            node.expanded = true
          }
        } catch (err) {
          console.warn('展开节点失败:', key, err)
        }
      })
    })
  } catch (error) {
    console.error('展开菜单失败:', error)
  }
}

// 折叠所有菜单
const collapseAllMenus = () => {
  if (!menuTreeRef.value || !menuTreeData.value.length) {
    console.warn('菜单树未准备就绪或无数据')
    return
  }

  try {
    // 使用 nextTick 确保 DOM 更新完成
    nextTick(() => {
      const allKeys = getAllMenuKeys(menuTreeData.value)
      console.log('折叠所有菜单，节点数量:', allKeys.length)

      // 使用 Element Plus Tree 的内置方法
      allKeys.forEach(key => {
        try {
          const node = menuTreeRef.value?.getNode(key)
          if (node) {
            node.expanded = false
          }
        } catch (err) {
          console.warn('折叠节点失败:', key, err)
        }
      })
    })
  } catch (error) {
    console.error('折叠菜单失败:', error)
  }
}

// 保存权限配置
const handleSave = async () => {
  if (!props.roleInfo || !menuTreeRef.value) return
  
  try {
    saving.value = true
    
    // 获取选中的菜单ID
    const checkedKeys = (menuTreeRef.value.getCheckedKeys(false) as number[]) || []
    const halfCheckedKeys = (menuTreeRef.value.getHalfCheckedKeys() as number[]) || []
    const menuIds = [...checkedKeys, ...halfCheckedKeys]
    
    console.log('保存权限配置，角色ID:', props.roleInfo.role_id, '权限数量:', menuIds.length)
    
    // 调用API保存
    const response = await RoleApi.assignRoleMenus(props.roleInfo.role_id, {
      menu_ids: menuIds
    })
    
    if (response.success) {
      ElMessage.success('权限配置保存成功')
      emit('success')
      handleClose()
    } else {
      throw new Error(response.message || '保存权限配置失败')
    }
  } catch (error) {
    console.error('保存权限配置失败:', error)
    ElMessage.error('保存权限配置失败')
  } finally {
    saving.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  visible.value = false

  // 重置状态（保留菜单数据以便下次快速打开）
  menuCheckAll.value = false
  menuIndeterminate.value = false
  activeTab.value = 'menu'
  loading.value = false
  treeLoading.value = false
  saving.value = false
}
</script>

<style scoped lang="scss">
.permission-dialog {
  .role-info {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 8px;
    
    .role-desc {
      color: #666;
      font-size: 14px;
    }
  }
  
  .permission-tabs {
    .menu-permission-container {
      .toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding: 12px 16px;
        background: #fafafa;
        border-radius: 6px;
        
        .left-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .right-info {
          font-size: 13px;
        }
      }
      
      .menu-tree-wrapper {
        border: 1px solid #e4e7ed;
        border-radius: 6px;
        max-height: 400px;
        overflow-y: auto;
        
        .permission-tree {
          padding: 8px;
          
          .tree-node {
            display: flex;
            align-items: center;
            gap: 8px;
            flex: 1;
            
            .node-icon {
              color: #409eff;
            }
            
            .node-label {
              flex: 1;
            }
            
            .node-tag {
              margin-left: auto;
            }
          }
        }
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
