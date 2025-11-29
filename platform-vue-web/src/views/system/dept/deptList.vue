<template>
  <div class="page-container">
    <BaseTable
      title="部门管理"
      :data="tableData"
      :loading="loading"
      :show-pagination="false"
      :show-expand-toggle="true"
      row-key="id"
      :tree-props="{ children: 'children' }"
      @refresh="loadData"
    >
      <template #header>
        <el-button @click="loadData()">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="onDataForm(-1, 0)">
          <el-icon><Plus /></el-icon>
          新增部门
        </el-button>
      </template>

      <el-table-column prop="dept_name" label="部门名称" min-width="300" />
      <el-table-column prop="order_num" label="排序" width="120" align="center" />
      <el-table-column prop="create_time" label="创建时间" width="180" align="center">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
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
    </BaseTable>
  </div>
</template>

<script lang="ts" setup>
import { ref } from "vue"
import { getDeptTree, deleteData } from './dept'
import { formatDateTime } from '~/utils/timeFormatter'
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 加载页面数据（树形结构）
const loadData = () => {
    loading.value = true
    getDeptTree().then((res: { data: { code: number; data: never[]; msg: string }; }) => {
        if (res.data.code === 200) {
            tableData.value = res.data.data || []
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch((error: any) => {
        console.error('查询失败:', error)
        ElMessage.error('查询失败，请稍后重试')
    }).finally(() => {
        loading.value = false
    })
}
loadData()

// 打开表单 （编辑/新增）
// deptId: 要编辑的部门ID，-1表示新增
// parentId: 上级部门ID，用于新增时设置父部门
const onDataForm = (deptId: number, parentId: number | null) => {
    let params_data = {}
    if (deptId > 0) {
        // 编辑
        params_data = { id: deptId }
    } else if (parentId !== null) {
        // 新增子部门
        params_data = { parent_id: parentId }
    }
    router.push({
        path: '/deptForm',
        query: params_data
    })
}

// 删除数据
const onDelete = (deptId: number) => {
    ElMessageBox.confirm(
        '确定要删除该部门吗？',
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(deptId).then((res: { data: { code: number; msg: string } }) => {
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
</style>

