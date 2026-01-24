<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="素材名称：">
        <el-input v-model="searchForm.mate_name" placeholder="根据素材名称筛选" />
      </el-form-item>
      <el-form-item label="所属项目：">
        <el-select v-model="searchForm.project_id" placeholder="选择所属项目" clearable>
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />     
        </el-select>
      </el-form-item>

      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增素材</el-button>
      </el-row>
    </el-form>
    <!-- END 搜索表单 -->
    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%" max-height="500">
      <!-- 数据列 -->
      <el-table-column
        v-for="col in columnList"
        :prop="col.prop"
        :label="col.label"
        :key="col.prop"
        :show-overflow-tooltip="true"
      />

      <!-- 操作 -->
      <el-table-column fixed="right" label="操作">
        <template #default="scope">
          <el-button link type="primary" size="small" @click.prevent="onDownloadFile(scope.$index)">
          下载
          </el-button>
          <el-button link type="primary" size="small" @click.prevent="copyMaterialUrl(scope.$index)" >
          复制链接
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
    <!-- END 分页 -->
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { queryByPage, deleteData } from '@/api/ApiMateManage'
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({ "mate_name": "", "project_id": "" })

const columnList = ref([
  { prop: "id", label: '素材编号' },
  { prop: "mate_name", label: '素材名称' },
  { prop: "mate_url", label: '素材地址' },
  { prop: "create_time", label: '创建时间' }
])

const tableData = ref([])
const projectList = ref([{
  id: 0,
  project_name: '',
  project_desc: ''
}])

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
    path: '/ApiMateManageForm',
    query: params_data
  })
}

const onDelete = async (index) => {
  const mateId = tableData.value[index]["id"]
  const mateName = tableData.value[index]["mate_name"]

  await confirmDelete(
    () => deleteData(mateId),
    `确定要删除素材 "${mateName}" 吗？此操作不可恢复！`,
    '素材删除成功',
    loadData
  )
}

const onDownloadFile = (index) => {
  const mateUrl = tableData.value[index]["mate_url"]
  Message.info(`下载功能开发中... 素材地址: ${mateUrl}`)
}

const copyMaterialUrl = (index) => {
  const mateUrl = tableData.value[index]["mate_url"]
  navigator.clipboard.writeText(mateUrl).then(() => {
    Message.success("素材链接已复制到剪贴板")
  }).catch(() => {
    Message.error("复制失败，请手动复制")
  })
}

import { queryAllProject } from "@/api/ApiProject"
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data
  })
}
getProjectList()
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}
</style>
