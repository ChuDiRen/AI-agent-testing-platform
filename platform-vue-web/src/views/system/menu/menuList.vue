<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>菜单管理</h3>
          <div class="header-actions">
            <el-button @click="loadData()">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="primary" @click="onDataForm(-1, 0)">
              <el-icon><Plus /></el-icon>
              新增菜单
            </el-button>
          </div>
        </div>
      </template>
    <!-- 数据表格 - 树形展示 -->
    <el-table
        :data="tableData"
        row-key="id"
        style="width: 100%"
        default-expand-all
        :tree-props="{ children: 'children' }"
    >
        <el-table-column prop="menu_name" label="菜单名称" width="180" show-overflow-tooltip />
        <el-table-column prop="icon" label="图标" width="100" align="center">
            <template #default="scope">
                <el-icon v-if="scope.row.icon" :size="18">
                    <component :is="scope.row.icon" />
                </el-icon>
                <span v-else style="color: var(--el-text-color-placeholder);">-</span>
            </template>
        </el-table-column>
        <el-table-column prop="order_num" label="排序" width="70" align="center" />
        <el-table-column prop="perms" label="权限标识" width="160" show-overflow-tooltip />
        <el-table-column prop="component" label="组件路径" min-width="180" show-overflow-tooltip />
        <el-table-column prop="menu_type" label="类型" width="80" align="center">
            <template #default="scope">
                <el-tag v-if="scope.row.menu_type === 'M'" type="warning">目录</el-tag>
                <el-tag v-else-if="scope.row.menu_type === 'C'" type="primary">菜单</el-tag>
                <el-tag v-else type="success">按钮</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="visible" label="可见" width="70" align="center">
            <template #default="scope">
                <el-tag v-if="scope.row.visible === '0'" type="success" size="small">显示</el-tag>
                <el-tag v-else type="info" size="small">隐藏</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="70" align="center">
            <template #default="scope">
                <el-tag v-if="scope.row.status === '0'" type="success" size="small">正常</el-tag>
                <el-tag v-else type="danger" size="small">停用</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="160" show-overflow-tooltip />
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作" width="220">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(-1, scope.row.id)">
                    新增
                </el-button>
                <el-button link type="warning" size="small" @click.prevent="onDataForm(scope.row.id, null)">
                    编辑
                </el-button>
                <el-button link type="danger" size="small" @click.prevent="onDelete(scope.row.id)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getMenuTree, deleteData } from './menu'
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 表格数据
const tableData = ref([])

// 加载页面数据（树形结构）
const loadData = () => {
    getMenuTree().then((res: { data: { code: number; data: never[]; msg: string }; }) => {
        if (res.data.code === 200) {
            tableData.value = res.data.data || []
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch((error: any) => {
        console.error('查询失败:', error)
        ElMessage.error('查询失败，请稍后重试')
    })
}
loadData()

// 打开表单 （编辑/新增）
// menuId: 要编辑的菜单ID，-1表示新增
// parentId: 上级菜单ID，用于新增时设置父菜单
const onDataForm = (menuId: number, parentId: number | null) => {
    let params_data = {}
    if (menuId > 0) {
        // 编辑
        params_data = { id: menuId }
    } else if (parentId !== null) {
        // 新增子菜单
        params_data = { parent_id: parentId }
    }
    router.push({
        path: '/menuForm',
        query: params_data
    })
}

// 删除数据
const onDelete = (menuId: number) => {
    ElMessageBox.confirm(
        '确定要删除该菜单吗？',
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(menuId).then((res: { data: { code: number; msg: string } }) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.msg || '删除失败')
            }
        }).catch(() => { // 删除失败处理
            ElMessage.error('删除失败，请稍后重试')
        })
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}
</script>

<style scoped>
@import '~/styles/common-list.css'; /* 统一使用~别名 */
@import '~/styles/common-form.css'; /* 统一使用~别名 */

.header-actions {
  display: flex;
  gap: 12px;
}
</style>

