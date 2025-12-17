<template>
  <div class="page-container">
    <BaseSearch 
      :model="searchForm" 
      @search="loadData" 
      @reset="resetSearch"
    >
      <el-form-item label="用户名">
        <el-input v-model="searchForm.username" placeholder="根据用户名筛选" />
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="用户管理"
      :data="tableData"
      :loading="loading"
      :total="total"
      v-model:pagination="pagination"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="onDataForm(-1)">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </template>

      <!-- 数据列 -->
      <el-table-column prop="id" label="用户ID" width="100" />
      <el-table-column prop="username" label="用户名" width="120" show-overflow-tooltip />
      <el-table-column prop="email" label="邮箱" width="200" show-overflow-tooltip />
      <el-table-column prop="mobile" label="联系电话" width="130" />
      <el-table-column prop="dept_id" label="部门" width="120">
        <template #default="scope">
          {{ deptMap[scope.row.dept_id] || scope.row.dept_id }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="scope">
          <el-tag :type="scope.row.status === '1' ? 'success' : 'warning'">
            {{ scope.row.status === '1' ? '有效' : '锁定' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ssex" label="性别" width="80">
        <template #default="scope">
          {{ genderMap[scope.row.ssex] || '未知' }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="创建时间" width="180">
        <template #default="scope">
          {{ formatDateTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作" width="220">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDataView(scope.$index)">
            查看
          </el-button>
          <el-button link type="success" size="small" @click.prevent="onDataForm(scope.$index)">
            编辑
          </el-button>
          <el-button link type="danger" size="small" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </BaseTable>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData } from './user'
import { getDeptTree } from '~/views/system/dept/dept'
import { useRouter } from "vue-router";
import { formatDateTime } from '~/utils/timeFormatter'
import { ElMessage, ElMessageBox } from 'element-plus'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

const router = useRouter()

// 分页参数
const pagination = reactive({
  page: 1,
  limit: 10
})
const total = ref(0)
const loading = ref(false)

// 搜索功能 - 筛选表单
const searchForm = reactive({"username": null})

// 数据字典映射
const genderMap = {
    '0': '男',
    '1': '女',
    '2': '保密'
}

// 部门映射（从后端加载）
const deptMap = ref({})

// 加载部门数据
const loadDeptData = async () => {
    try {
        const res = await getDeptTree()
        if (res.data.code === 200) {
            const depts = res.data.data
            // 将部门树扁平化为映射表
            const flattenDepts = (deptList, map = {}) => {
                if (!deptList || !Array.isArray(deptList)) {
                    return map
                }
                deptList.forEach(dept => {
                    if (dept.id !== undefined && dept.id !== null) {
                        map[dept.id] = dept.dept_name
                    }
                    if (dept.children && dept.children.length > 0) {
                        flattenDepts(dept.children, map)
                    }
                })
                return map
            }
            deptMap.value = flattenDepts(depts)
        }
    } catch (error) {
        ElMessage.error('加载部门数据失败，请稍后重试')
    }
}

// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    loading.value = true
    let searchData = { ...searchForm }
    searchData["page"] = pagination.page
    searchData["pageSize"] = pagination.limit

    queryByPage(searchData).then((res: { data: { code: number; data: never[]; total: number; msg: string }; }) => {
        if (res.data.code === 200) {
            tableData.value = res.data.data || []
            total.value = res.data.total || 0
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch(() => {
        ElMessage.error('查询失败，请稍后重试')
    }).finally(() => {
        loading.value = false
    })
}

// 重置搜索
const resetSearch = () => {
    searchForm.username = null
    pagination.page = 1
    loadData()
}

// 页面初始化
onMounted(() => {
    loadDeptData()
    loadData()
})

// 查看用户详情
const onDataView = (index: number) => {
    const item = tableData.value[index]
    router.push({
        path: 'userForm',
        query: {
            id: item.id,
            view: 'true'
        }
    })
}

// 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: 'userForm',
        query: params_data
    });
}
// 删除数据
const onDelete = (index: number) => {
    const item = tableData.value[index]
    ElMessageBox.confirm(
        `确定要删除用户"${item.username}"吗？`,
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        deleteData(item.id).then((res: { data: { code: number; msg: string } }) => {
            if (res.data.code === 200) {
                ElMessage.success('删除成功')
                loadData()
            } else {
                ElMessage.error(res.data.msg || '删除失败')
            }
        }).catch(() => {
            ElMessage.error('删除失败，请稍后重试')
        })
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}
</script>

<style scoped>
/* 移除原来的样式引用，因为组件内部已经包含了必要的样式 */
</style>