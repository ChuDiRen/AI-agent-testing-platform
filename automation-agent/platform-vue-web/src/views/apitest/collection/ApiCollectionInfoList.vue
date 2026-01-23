<template>
  <div>
    <Breadcrumb />
    
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
      <el-form-item label="集合名称：">
        <el-input v-model="searchForm.collection_name" placeholder="根据集合名称筛选" />
      </el-form-item>

      <el-row class="mb-4" type="flex" justify="end">
        <el-button type="primary" @click="loadData()">查询</el-button>
        <el-button type="warning" @click="onDataForm(-1)">新增集合</el-button>
      </el-row>
    </el-form>

    <el-table :data="tableData" style="width: 100%;" max-height="500">
      <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
        :show-overflow-tooltip="true" />
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
import { queryByPage, deleteData } from './ApiCollectionInfo.js'
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const searchForm = reactive({ "collection_name": "" })

const columnList = ref([
  { prop: "id", label: '集合编号' },
  { prop: "collection_name", label: '集合名称' },
  { prop: "create_time", label: '创建时间' }
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
    path: '/ApiCollectionInfoForm',
    query: params_data
  })
}

const onDelete = async (index) => {
  const collectionId = tableData.value[index]["id"]
  const collectionName = tableData.value[index]["collection_name"]

  await confirmDelete(
    () => deleteData(collectionId),
    `确定要删除集合 "${collectionName}" 吗？此操作不可恢复！`,
    '集合删除成功',
    loadData
  )
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
