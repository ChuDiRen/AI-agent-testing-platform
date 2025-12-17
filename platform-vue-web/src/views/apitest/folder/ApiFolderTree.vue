<template>
  <div class="folder-tree-container">
    <!-- 工具栏 -->
    <div class="tree-toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索接口..."
        prefix-icon="Search"
        clearable
        size="small"
      />
      <div class="toolbar-actions">
        <el-tooltip content="新建目录">
          <el-button size="small" @click="handleAddFolder(0)">
            <el-icon><FolderAdd /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="刷新">
          <el-button size="small" @click="loadTree">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="全部展开">
          <el-button size="small" @click="expandAll">
            <el-icon><Expand /></el-icon>
          </el-button>
        </el-tooltip>
        <el-tooltip content="全部折叠">
          <el-button size="small" @click="collapseAll">
            <el-icon><Fold /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 目录树 -->
    <el-tree
      ref="treeRef"
      :data="filteredTreeData"
      :props="treeProps"
      node-key="id"
      :default-expanded-keys="expandedKeys"
      :expand-on-click-node="false"
      :highlight-current="true"
      draggable
      :allow-drop="allowDrop"
      :allow-drag="allowDrag"
      @node-click="handleNodeClick"
      @node-contextmenu="handleContextMenu"
      @node-drop="handleNodeDrop"
      class="folder-tree"
    >
      <template #default="{ node, data }">
        <div class="tree-node" :class="{ 'is-api': data.node_type === 'api' }">
          <!-- 图标 -->
          <el-icon v-if="data.node_type === 'folder'" class="node-icon folder-icon">
            <Folder />
          </el-icon>
          <span v-else class="method-tag" :class="getMethodClass(data.request_method)">
            {{ getMethodShort(data.request_method) }}
          </span>
          
          <!-- 名称 -->
          <span class="node-label" :title="data.folder_name || data.api_name">
            {{ data.folder_name || data.api_name }}
          </span>
          
          <!-- 接口数量 -->
          <span v-if="data.node_type === 'folder' && data.api_count > 0" class="api-count">
            {{ data.api_count }}
          </span>
          
          <!-- 操作按钮 -->
          <div class="node-actions" v-if="data.node_type === 'folder'">
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, data)">
              <el-icon class="more-icon"><MoreFilled /></el-icon>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="addFolder">新建子目录</el-dropdown-item>
                  <el-dropdown-item command="addApi">新建接口</el-dropdown-item>
                  <el-dropdown-item command="rename" divided>重命名</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>
    </el-tree>

    <!-- 新建/编辑目录对话框 -->
    <el-dialog v-model="folderDialogVisible" :title="folderDialogTitle" width="400px">
      <el-form ref="folderFormRef" :model="folderForm" :rules="folderRules" label-width="80px">
        <el-form-item label="目录名称" prop="folder_name">
          <el-input v-model="folderForm.folder_name" placeholder="请输入目录名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="folderForm.folder_desc" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleFolderSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <div
      v-show="contextMenuVisible"
      class="context-menu"
      :style="{ left: contextMenuPosition.x + 'px', top: contextMenuPosition.y + 'px' }"
    >
      <div class="menu-item" @click="handleContextAction('addFolder')">新建目录</div>
      <div class="menu-item" @click="handleContextAction('addApi')">新建接口</div>
      <div class="menu-divider"></div>
      <div class="menu-item" @click="handleContextAction('rename')">重命名</div>
      <div class="menu-item danger" @click="handleContextAction('delete')">删除</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, FolderAdd, Refresh, Expand, Fold, MoreFilled, Search } from '@element-plus/icons-vue'
import { queryTree, insertData, updateData, deleteData, moveFolder, batchSort } from './apiFolder'

const props = defineProps({
  projectId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['select', 'add-api', 'edit-api'])

// 树数据
const treeData = ref([])
const treeRef = ref(null)
const expandedKeys = ref([])
const searchText = ref('')

// 树配置
const treeProps = {
  children: 'children',
  label: (data) => data.folder_name || data.api_name
}

// 过滤后的树数据
const filteredTreeData = computed(() => {
  if (!searchText.value) return treeData.value
  return filterTree(treeData.value, searchText.value.toLowerCase())
})

// 过滤树
const filterTree = (nodes, keyword) => {
  const result = []
  for (const node of nodes) {
    const name = (node.folder_name || node.api_name || '').toLowerCase()
    const url = (node.request_url || '').toLowerCase()
    
    if (name.includes(keyword) || url.includes(keyword)) {
      result.push({ ...node })
    } else if (node.children?.length) {
      const filteredChildren = filterTree(node.children, keyword)
      if (filteredChildren.length) {
        result.push({ ...node, children: filteredChildren })
      }
    }
  }
  return result
}

// 目录对话框
const folderDialogVisible = ref(false)
const folderDialogTitle = ref('新建目录')
const folderFormRef = ref(null)
const folderForm = ref({
  id: null,
  parent_id: 0,
  folder_name: '',
  folder_desc: ''
})
const folderRules = {
  folder_name: [{ required: true, message: '请输入目录名称', trigger: 'blur' }]
}

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const contextMenuNode = ref(null)

// 加载目录树
const loadTree = async () => {
  if (!props.projectId) return
  
  try {
    const res = await queryTree({ project_id: props.projectId })
    if (res.data.code === 200) {
      treeData.value = res.data.data || []
      // 默认展开第一级
      expandedKeys.value = treeData.value
        .filter(n => n.node_type === 'folder')
        .map(n => n.id)
    }
  } catch (error) {
    console.error('加载目录树失败:', error)
  }
}

// 获取方法类名
const getMethodClass = (method) => {
  const classMap = {
    GET: 'method-get',
    POST: 'method-post',
    PUT: 'method-put',
    DELETE: 'method-delete',
    PATCH: 'method-patch'
  }
  return classMap[method?.toUpperCase()] || 'method-get'
}

// 获取方法简写
const getMethodShort = (method) => {
  const shortMap = {
    GET: 'G',
    POST: 'P',
    PUT: 'U',
    DELETE: 'D',
    PATCH: 'PA'
  }
  return shortMap[method?.toUpperCase()] || 'G'
}

// 节点点击
const handleNodeClick = (data) => {
  if (data.node_type === 'api') {
    emit('select', { type: 'api', data })
  } else {
    emit('select', { type: 'folder', data })
  }
}

// 右键菜单
const handleContextMenu = (event, data, node) => {
  event.preventDefault()
  contextMenuNode.value = data
  contextMenuPosition.value = {
    x: event.clientX,
    y: event.clientY
  }
  contextMenuVisible.value = true
}

// 关闭右键菜单
const closeContextMenu = () => {
  contextMenuVisible.value = false
}

// 右键菜单操作
const handleContextAction = (action) => {
  closeContextMenu()
  handleCommand(action, contextMenuNode.value)
}

// 命令处理
const handleCommand = (command, data) => {
  switch (command) {
    case 'addFolder':
      handleAddFolder(data?.id || 0)
      break
    case 'addApi':
      emit('add-api', { folder_id: data?.id || 0 })
      break
    case 'rename':
      handleRenameFolder(data)
      break
    case 'delete':
      handleDeleteFolder(data)
      break
  }
}

// 新建目录
const handleAddFolder = (parentId) => {
  folderDialogTitle.value = '新建目录'
  folderForm.value = {
    id: null,
    parent_id: parentId,
    project_id: props.projectId,
    folder_name: '',
    folder_desc: ''
  }
  folderDialogVisible.value = true
}

// 重命名目录
const handleRenameFolder = (data) => {
  if (data.node_type !== 'folder') return
  
  folderDialogTitle.value = '重命名目录'
  folderForm.value = {
    id: data.id,
    folder_name: data.folder_name,
    folder_desc: data.folder_desc
  }
  folderDialogVisible.value = true
}

// 删除目录
const handleDeleteFolder = async (data) => {
  if (data.node_type !== 'folder') return
  
  try {
    await ElMessageBox.confirm(
      '删除目录后，子目录和接口将移动到父目录。确定删除吗？',
      '确认删除',
      { type: 'warning' }
    )
    
    const res = await deleteData(data.id, true)
    if (res.data.code === 200) {
      ElMessage.success('删除成功')
      loadTree()
    } else {
      ElMessage.error(res.data.msg || '删除失败')
    }
  } catch {
    // 取消删除
  }
}

// 提交目录表单
const handleFolderSubmit = async () => {
  try {
    await folderFormRef.value.validate()
    
    const res = folderForm.value.id
      ? await updateData(folderForm.value)
      : await insertData(folderForm.value)
    
    if (res.data.code === 200) {
      ElMessage.success(folderForm.value.id ? '更新成功' : '创建成功')
      folderDialogVisible.value = false
      loadTree()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
  }
}

// 拖拽相关
const allowDrop = (draggingNode, dropNode, type) => {
  // 接口只能放到目录中
  if (draggingNode.data.node_type === 'api') {
    return dropNode.data.node_type === 'folder' && type === 'inner'
  }
  // 目录可以放到其他目录中或同级
  return dropNode.data.node_type === 'folder' || type !== 'inner'
}

const allowDrag = (node) => {
  return true
}

const handleNodeDrop = async (draggingNode, dropNode, dropType) => {
  const dragData = draggingNode.data
  const dropData = dropNode.data
  
  try {
    if (dragData.node_type === 'folder') {
      // 移动目录
      let targetParentId = 0
      if (dropType === 'inner') {
        targetParentId = dropData.id
      } else if (dropData.parent_id !== undefined) {
        targetParentId = dropData.parent_id
      }
      
      await moveFolder({
        id: dragData.id,
        target_parent_id: targetParentId,
        target_sort_order: 0
      })
    }
    
    ElMessage.success('移动成功')
    loadTree()
  } catch (error) {
    console.error('移动失败:', error)
    loadTree()
  }
}

// 展开/折叠
const expandAll = () => {
  const keys = []
  const collectKeys = (nodes) => {
    nodes.forEach(node => {
      if (node.node_type === 'folder') {
        keys.push(node.id)
        if (node.children) collectKeys(node.children)
      }
    })
  }
  collectKeys(treeData.value)
  expandedKeys.value = keys
}

const collapseAll = () => {
  expandedKeys.value = []
}

// 监听项目变化
watch(() => props.projectId, () => {
  loadTree()
})

// 点击其他地方关闭右键菜单
onMounted(() => {
  loadTree()
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})

// 暴露方法
defineExpose({
  reload: loadTree
})
</script>

<style scoped>
.folder-tree-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tree-toolbar {
  padding: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  display: flex;
  gap: 8px;
  align-items: center;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
}

.folder-tree {
  flex: 1;
  overflow: auto;
  padding: 8px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  padding: 4px 0;
}

.tree-node.is-api {
  cursor: pointer;
}

.node-icon {
  font-size: 16px;
}

.folder-icon {
  color: #E6A23C;
}

.method-tag {
  font-size: 10px;
  font-weight: bold;
  padding: 2px 4px;
  border-radius: 2px;
  min-width: 20px;
  text-align: center;
}

.method-get { background: #67C23A; color: white; }
.method-post { background: #E6A23C; color: white; }
.method-put { background: #409EFF; color: white; }
.method-delete { background: #F56C6C; color: white; }
.method-patch { background: #909399; color: white; }

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.api-count {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 0 6px;
  border-radius: 10px;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.more-icon {
  cursor: pointer;
  padding: 4px;
}

.more-icon:hover {
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

/* 右键菜单 */
.context-menu {
  position: fixed;
  background: white;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  min-width: 120px;
}

.menu-item {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
}

.menu-item:hover {
  background: var(--el-fill-color-light);
}

.menu-item.danger {
  color: var(--el-color-danger);
}

.menu-divider {
  height: 1px;
  background: var(--el-border-color-lighter);
  margin: 4px 0;
}
</style>
