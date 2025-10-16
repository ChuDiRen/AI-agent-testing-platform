<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>用户管理</h3>
          <el-button type="primary" @click="onDataForm(-1)">
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="根据用户名筛选" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData()">查询</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    <!-- END 搜索表单 -->
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <!-- 数据列 -->
        <el-table-column prop="id" label="用户ID" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" show-overflow-tooltip />
        <el-table-column prop="email" label="邮箱" show-overflow-tooltip />
        <el-table-column prop="mobile" label="联系电话" show-overflow-tooltip />
        <el-table-column prop="dept_id" label="部门" show-overflow-tooltip>
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
        <el-table-column prop="create_time" label="创建时间" show-overflow-tooltip>
            <template #default="scope">
                {{ formatDateTime(scope.row.create_time) }}
            </template>
        </el-table-column>
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作" width="150">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
                    编辑
                </el-button>
                <el-button link type="danger" size="small" @click.prevent="onDelete(scope.$index)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
    
    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    </el-card>
  </div>
</template>
  
<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData } from './user' // 不同页面不同的接口
import { useRouter } from "vue-router";
import { formatDateTime } from '~/utils/timeFormatter'
import axios from '~/axios'
import { ElMessage, ElMessageBox } from 'element-plus'
const router = useRouter()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

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
        const res = await axios.get('/dept/tree')
        if (res.data.code === 200) {
            const depts = res.data.data
            // 将部门树扁平化为映射表
            const flattenDepts = (deptList, map = {}) => {
                deptList.forEach(dept => {
                    map[dept.dept_id] = dept.dept_name
                    if (dept.children && dept.children.length > 0) {
                        flattenDepts(dept.children, map)
                    }
                })
                return map
            }
            deptMap.value = flattenDepts(depts)
        } else {
            console.error('加载部门数据失败:', res.data.msg)
        }
    } catch (error) {
        console.error('加载部门数据失败:', error)
        ElMessage.error('加载部门数据失败，请稍后重试')
    }
}

// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    queryByPage(searchData).then((res: { data: { code: number; data: never[]; total: number; msg: string }; }) => {
        if (res.data.code === 200) {
            tableData.value = res.data.data || []
            total.value = res.data.total || 0
        } else {
            ElMessage.error(res.data.msg || '查询失败')
        }
    }).catch((error: any) => {
        console.error('查询失败:', error)
        ElMessage.error('查询失败，请稍后重试')
    })
}

// 重置搜索
const resetSearch = () => {
    searchForm.username = null
    currentPage.value = 1
    loadData()
}

// 页面初始化
onMounted(() => {
    loadDeptData() // 先加载部门数据
    loadData() // 再加载用户数据
})

// 变更 页大小
const handleSizeChange = (val: number) => {
    pageSize.value = val
    loadData()
}
// 变更 页码
const handleCurrentChange = (val: number) => {
    currentPage.value = val
    loadData()
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
        path: 'userForm', // 不同页面不同的表单路径
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
        }).catch(() => { // 删除失败处理
            ElMessage.error('删除失败，请稍后重试')
        })
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
}

// 其他功能拓展

</script>
<style scoped>
@import '~/styles/common-list.css'; /* 统一使用~别名 */
@import '~/styles/common-form.css'; /* 统一使用~别名 */
</style>