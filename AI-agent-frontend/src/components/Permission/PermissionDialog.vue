<!-- 权限配置对话框组件 -->
<template>
  <el-dialog
    v-model="dialogVisible"
    title="权限配置"
    width="800px"
    :close-on-click-modal="false"
    destroy-on-close
    @open="handleOpen"
    @close="handleClose"
  >
    <div class="permission-dialog-content" v-loading="loading">
      <!-- 角色信息 -->
      <div class="role-info">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="角色名称">
            {{ roleInfo?.role_name }}
          </el-descriptions-item>
          <el-descriptions-item label="角色描述">
            {{ roleInfo?.remark || '暂无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      
      <!-- 权限配置 -->
      <div class="permission-config">
        <div class="section-title">
          <h3>菜单权限配置</h3>
          <div class="actions">
            <el-button size="small" @click="expandAll">
              <el-icon><CaretBottom /></el-icon>
              展开全部
            </el-button>
            <el-button size="small" @click="collapseAll">
              <el-icon><CaretRight /></el-icon>
              收起全部
            </el-button>
            <el-button size="small" type="primary" @click="checkAll">
              <el-icon><Select /></el-icon>
              全选
            </el-button>
            <el-button size="small" @click="uncheckAll">
              <el-icon><CloseBold /></el-icon>
              取消全选
            </el-button>
          </div>
        </div>
        
        <!-- 菜单树 -->
        <el-tree
          ref="treeRef"
          :data="menuTreeData"
          :props="treeProps"
          :default-expand-all="false"
          :expand-on-click-node="false"
          :check-on-click-node="false"
          :auto-expand-parent="true"
          :default-checked-keys="checkedKeys"
          :default-expanded-keys="expandedKeys"
          show-checkbox
          node-key="id"
          check-strictly
          highlight-current
          @check="handleCheck"
          @check-change="handleCheckChange"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <div class="node-content">
                <!-- 菜单图标 -->
                <el-icon v-if="data.icon" class="node-icon">
                  <component :is="data.icon" />
                </el-icon>
                
                <!-- 菜单信息 -->
                <div class="node-info">
                  <span class="node-label">{{ data.label }}</span>
                  <span class="node-type" :class="getNodeTypeClass(data.type)">
                    {{ getNodeTypeText(data.type) }}
                  </span>
                </div>
                
                <!-- 权限标识 -->
                <div v-if="data.permission" class="node-permission">
                  <el-tag size="small" type="info">{{ data.permission }}</el-tag>
                </div>
              </div>
              
              <!-- 节点描述 -->
              <div v-if="data.description" class="node-description">
                <el-text type="info" size="small">{{ data.description }}</el-text>
              </div>
            </div>
          </template>
        </el-tree>
      </div>
      
      <!-- 权限说明 -->
      <div class="permission-tips">
        <el-alert
          title="权限说明"
          type="info"
          :closable="false"
          show-icon
        >
          <ul>
            <li>• <strong>目录</strong>：导航菜单分组，通常不包含具体页面</li>
            <li>• <strong>菜单</strong>：具体的页面菜单项，用户可以点击访问</li>
            <li>• <strong>按钮</strong>：页面内的操作按钮，如增删改查等功能</li>
            <li>• 选中父级菜单时，建议同时选中相关的子级权限</li>
            <li>• 权限配置后需要重新登录才能生效</li>
          </ul>
        </el-alert>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :loading="saving">
          保存配置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  CaretBottom, 
  CaretRight, 
  Select, 
  CloseBold 
} from '@element-plus/icons-vue'
import { MenuApi } from '@/api/modules/menu'
import { RoleApi } from '@/api/modules/role'
import type { MenuTreeNode, RoleInfo } from '@/api/types'

// Props定义
interface Props {
  modelValue: boolean
  roleInfo?: RoleInfo | null
}

const props = withDefaults(defineProps<Props>(), {
  roleInfo: null
})

// Emits定义
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

// 引用
const treeRef = ref()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const menuTreeData = ref<MenuTreeNode[]>([])
const checkedKeys = ref<string[]>([])
const expandedKeys = ref<string[]>([])

// 计算属性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 树形组件配置
const treeProps = {
  children: 'children',
  label: 'label',
  disabled: 'disabled'
}

// 监听角色信息变化
watch(() => props.roleInfo, (newRole) => {
  if (newRole && dialogVisible.value) {
    loadMenuTree()
    loadRolePermissions()
  }
}, { immediate: true })

// 方法定义
const loadMenuTree = async () => {
  try {
    loading.value = true
    const response = await MenuApi.getMenuTree()
    
    if (response.success && response.data) {
      menuTreeData.value = formatMenuTree(response.data)
      // 默认展开第一级
      expandedKeys.value = menuTreeData.value.map(item => item.id)
    }
  } catch (error) {
    console.error('加载菜单树失败:', error)
    ElMessage.error('加载菜单树失败')
  } finally {
    loading.value = false
  }
}

const loadRolePermissions = async () => {
  if (!props.roleInfo?.role_id) return
  
  try {
    const response = await RoleApi.getRolePermissions(props.roleInfo.role_id)
    
    if (response.success && response.data) {
      checkedKeys.value = response.data.menu_ids || []
      
      // 设置树的选中状态
      nextTick(() => {
        treeRef.value?.setCheckedKeys(checkedKeys.value)
      })
    }
  } catch (error) {
    console.error('加载角色权限失败:', error)
    ElMessage.error('加载角色权限失败')
  }
}

const formatMenuTree = (menuList: any[]): MenuTreeNode[] => {
  return menuList.map(menu => ({
    id: menu.menu_id.toString(),
    label: menu.menu_name,
    type: menu.TYPE, // 0目录 1菜单 2按钮
    icon: menu.ICON,
    permission: menu.permission_code,
    description: menu.COMPONENT,
    disabled: menu.STATUS === '0', // 禁用状态的菜单不可选
    children: menu.children ? formatMenuTree(menu.children) : []
  }))
}

const getNodeTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    '0': '目录',
    '1': '菜单', 
    '2': '按钮'
  }
  return typeMap[type] || '未知'
}

const getNodeTypeClass = (type: string) => {
  const classMap: Record<string, string> = {
    '0': 'type-directory',
    '1': 'type-menu',
    '2': 'type-button'
  }
  return classMap[type] || ''
}

const expandAll = () => {
  const allKeys = getAllNodeKeys(menuTreeData.value)
  expandedKeys.value = allKeys
  
  nextTick(() => {
    allKeys.forEach(key => {
      treeRef.value?.store.nodesMap[key]?.expand()
    })
  })
}

const collapseAll = () => {
  expandedKeys.value = []
  
  nextTick(() => {
    const allKeys = getAllNodeKeys(menuTreeData.value)
    allKeys.forEach(key => {
      treeRef.value?.store.nodesMap[key]?.collapse()
    })
  })
}

const checkAll = () => {
  const allKeys = getAllNodeKeys(menuTreeData.value)
  checkedKeys.value = allKeys
  treeRef.value?.setCheckedKeys(allKeys)
}

const uncheckAll = () => {
  checkedKeys.value = []
  treeRef.value?.setCheckedKeys([])
}

const getAllNodeKeys = (nodes: MenuTreeNode[]): string[] => {
  let keys: string[] = []
  
  const traverse = (nodeList: MenuTreeNode[]) => {
    nodeList.forEach(node => {
      if (!node.disabled) {
        keys.push(node.id)
      }
      if (node.children && node.children.length > 0) {
        traverse(node.children)
      }
    })
  }
  
  traverse(nodes)
  return keys
}

const handleCheck = (data: any, checked: any) => {
  // 获取当前选中的所有节点
  checkedKeys.value = checked.checkedKeys
}

const handleCheckChange = (data: any, checked: boolean, indeterminate: boolean) => {
  // 可以在这里添加额外的检查逻辑
}

const handleOpen = () => {
  if (props.roleInfo) {
    loadMenuTree()
    loadRolePermissions()
  }
}

const handleClose = () => {
  // 清理数据
  menuTreeData.value = []
  checkedKeys.value = []
  expandedKeys.value = []
}

const handleCancel = () => {
  dialogVisible.value = false
}

const handleConfirm = async () => {
  if (!props.roleInfo?.role_id) {
    ElMessage.error('角色信息不完整')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要保存当前的权限配置吗？配置后需要重新登录才能生效。',
      '确认保存',
      {
        type: 'warning',
        confirmButtonText: '确定保存',
        cancelButtonText: '取消'
      }
    )
    
    saving.value = true
    
    // 获取当前选中的菜单ID
    const selectedMenuIds = treeRef.value?.getCheckedKeys() || []
    
    const response = await RoleApi.assignMenus(props.roleInfo.role_id, {
      menu_ids: selectedMenuIds
    })
    
    if (response.success) {
      ElMessage.success('权限配置保存成功')
      emit('success')
      dialogVisible.value = false
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('保存权限配置失败:', error)
      ElMessage.error('保存权限配置失败')
    }
  } finally {
    saving.value = false
  }
}

// 暴露方法
defineExpose({
  loadMenuTree,
  loadRolePermissions
})
</script>

<style scoped lang="scss">
.permission-dialog-content {
  .role-info {
    margin-bottom: 24px;
  }
  
  .permission-config {
    .section-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
      
      .actions {
        display: flex;
        gap: 8px;
      }
    }
    
    :deep(.el-tree) {
      border: 1px solid var(--el-border-color);
      border-radius: 4px;
      max-height: 400px;
      overflow-y: auto;
      
      .el-tree-node {
        .el-tree-node__content {
          height: auto;
          min-height: 32px;
          padding: 8px;
          
          &:hover {
            background-color: var(--el-tree-node-hover-bg-color);
          }
        }
        
        .tree-node {
          flex: 1;
          display: flex;
          flex-direction: column;
          
          .node-content {
            display: flex;
            align-items: center;
            gap: 8px;
            
            .node-icon {
              font-size: 16px;
              color: var(--el-color-primary);
            }
            
            .node-info {
              flex: 1;
              display: flex;
              align-items: center;
              gap: 8px;
              
              .node-label {
                font-size: 14px;
                color: #303133;
              }
              
              .node-type {
                padding: 2px 6px;
                border-radius: 2px;
                font-size: 12px;
                line-height: 1;
                
                &.type-directory {
                  background-color: #e1f3ff;
                  color: #0052d9;
                }
                
                &.type-menu {
                  background-color: #e6f7ff;
                  color: #1890ff;
                }
                
                &.type-button {
                  background-color: #f6ffed;
                  color: #52c41a;
                }
              }
            }
            
            .node-permission {
              .el-tag {
                font-size: 11px;
                height: 20px;
                line-height: 18px;
              }
            }
          }
          
          .node-description {
            margin-top: 4px;
            padding-left: 24px;
            
            .el-text {
              font-size: 12px;
            }
          }
        }
      }
    }
  }
  
  .permission-tips {
    margin-top: 24px;
    
    :deep(.el-alert__content) {
      ul {
        margin: 8px 0 0 0;
        padding-left: 16px;
        
        li {
          margin-bottom: 4px;
          font-size: 13px;
          line-height: 1.5;
          
          &:last-child {
            margin-bottom: 0;
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

:deep(.el-dialog__body) {
  padding: 20px 24px;
}

:deep(.el-dialog__footer) {
  padding: 12px 24px 24px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>