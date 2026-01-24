<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="用例名称：">
        <el-input v-model="searchForm.case_name" placeholder="根据用例名称筛选" />
      </el-form-item>
      <el-form-item label="所属接口：">
        <el-select v-model="searchForm.api_info_id" placeholder="选择所属接口" clearable>
          <el-option v-for="api in apiList" :key="api.id" :label="api.api_name" :value="api.id" />
        </el-select>
      </el-form-item>

      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增用例</el-button>
        <el-dropdown @command="handleImportCommand">
          <el-button type="primary">
            导入用例<el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="onDownloadFile()">下载模板</el-dropdown-item>
              <el-dropdown-item @click="onImportFile()">导入用例</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-row>
    </el-form>

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
      <!-- 数据列 -->
      <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
        :show-overflow-tooltip="true" />
      <!-- 操作 -->
      <el-table-column fixed="right" label="操作">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
            编辑
          </el-button>
          <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="demo-pagination-block">
      <div class="demonstration"></div>
      <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { queryByPage, deleteData, downloadTemplate } from '@/api/ApiInfoCase'
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({ "case_name": "", "api_info_id": "" })

const columnList = ref([
  { prop: "id", label: '用例编号' },
  { prop: "case_name", label: '用例名称' },
  { prop: "api_info_id", label: '所属接口' },
  { prop: "create_time", label: '创建时间' }
])

const tableData = ref([])
const apiList = ref([])

const loadData = () => {
  let searchData = searchForm
  searchData["page"] = currentPage.value
  searchData["pageSize"] = pageSize.value

  queryByPage(searchData).then((res) => {
    tableData.value = res.data.data
    total.value = res.data.total
  })
}
loadData()

const handleSizeChange = (val) => {
  console.log("页大小变化:" + val)
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val) => {
  console.log("页码变化:" + val)
  currentPage.value = val
  loadData()
}

const onDataForm = (index) => {
  let params_data = {}
  if (index >= 0) {
    params_data = {
      id: tableData.value[index]["id"]
    }
  }
  router.push({
    path: 'ApiInfoCaseForm',
    query: params_data
  })
}

const onDelete = async (index) => {
  const caseId = tableData.value[index]["id"]
  const caseName = tableData.value[index]["case_name"]

  await confirmDelete(
    () => deleteData(caseId),
    `确定要删除用例 "${caseName}" 吗？此操作不可恢复！`,
    '用例删除成功',
    loadData
  )
}

const handleImportCommand = (command) => {
  console.log("导入命令:", command)
}

const onDownloadFile = () => {
  downloadTemplate().then((res) => {
    // 创建blob对象
    const blob = new Blob([res.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    // 创建下载链接
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = '测试用例导入模板.xlsx'
    link.click()
    // 释放URL对象
    window.URL.revokeObjectURL(link.href)
    Message.success("模板下载成功")
  }).catch((error) => {
    console.error("下载模板失败:", error)
    Message.error("下载模板失败：" + (error.response?.data?.msg || error.message))
  })
}

const onImportFile = () => {
  Message.info("导入用例功能开发中...")
}
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}
</style>
