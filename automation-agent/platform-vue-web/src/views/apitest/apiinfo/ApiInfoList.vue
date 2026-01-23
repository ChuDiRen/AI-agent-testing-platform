<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="接口名称：">
        <el-input v-model="searchForm.api_name" placeholder="根据接口名称筛选" />
      </el-form-item>
      <el-form-item label="所属项目：">
        <el-select v-model="searchForm.project_id" placeholder="选择所属项目" @change="projectChange" clearable>
          <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
        </el-select>
      </el-form-item>

      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增接口</el-button>
        <el-button type="primary" @click="loadSwagger()">swagger导入<el-icon><Upload /></el-icon></el-button>
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

    <!-- Swagger 导入弹窗 -->
    <el-dialog v-model="swaggerDialogVisible" title="Swagger 导入" width="30%">
      <el-form :model="swaggerForm" label-width="120px">
        <el-form-item label="所属项目">
          <el-select v-model="swaggerForm.project_id" placeholder="选择所属项目" clearable>
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Swagger 版本">
          <el-select v-model="swaggerForm.version" placeholder="请选择 Swagger 版本">
            <el-option label="Swagger 2.0" value="v2" />
            <el-option label="Swagger 3.0" value="v3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Swagger 地址">
          <el-input v-model="swaggerForm.host" placeholder="请输入 Swagger地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="swaggerDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmSwaggerImport">确认导入</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import { queryByPage, deleteData } from './ApiInfo.js'
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({ "api_name": "", "project_id": "", "module_id": "" })

const columnList = ref([
  { prop: "id", label: '接口用例编号' },
  { prop: "api_name", label: '接口名称' },
  { prop: "request_method", label: '请求方法' },
  { prop: "request_url", label: '请求地址' }
])

const tableData = ref([])

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
    path: 'ApiInfoForm',
    query: params_data
  })
}

const onDelete = async (index) => {
  const apiId = tableData.value[index]["id"]
  const apiName = tableData.value[index]["api_name"]

  await confirmDelete(
    () => deleteData(apiId),
    `确定要删除API "${apiName}" 吗？此操作不可恢复！`,
    'API删除成功',
    loadData
  )
}

import { queryAllProject } from "../project/ApiProject.js"
const projectList = ref([{
  id: 0,
  project_name: '',
  project_desc: ''
}])

function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data
  })
}
getProjectList()

const projectChange = () => {
  console.log("项目选择变化:", searchForm.project_id)
}

const swaggerDialogVisible = ref(false)
const swaggerForm = reactive({
  version: "",
  host: "",
  project_id: ""
})

const loadSwagger = () => {
  swaggerDialogVisible.value = true
}

import { doImportSwagger } from './ApiInfo.js'
const confirmSwaggerImport = () => {
  console.log("Swagger 导入信息:", swaggerForm)
  doImportSwagger(swaggerForm).then((res) => {
    console.log(res.data.msg)
    loadData()
  })
  
  swaggerDialogVisible.value = false
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
