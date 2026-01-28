<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
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
        <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </div>

    <!-- 表单视图 -->
    <div v-else>
      <!-- 面包屑导航 -->
      <Breadcrumb />
      
      <el-form ref="ruleFormRef" :inline="true" :model="apiInfo" :rules="rules" class="demo-form-inline">
        <div class="form-wrapper">
          <div class="form-info">| 基础信息</div>
          <el-form-item class="form-buttons">
            <el-button type="primary" @click="onSubmit()">保存</el-button>
            <el-button type="warning" @click="okExecuteTest">调试执行测试</el-button>
            <el-button type="info" @click="onCancel">关闭</el-button>
          </el-form-item>
        </div>
        
        <el-form-item label="用例编号：">
          <el-input v-model="apiInfo.id" placeholder="用例编号" clearable disabled />
        </el-form-item>
        
        <el-form-item label="用例名称：">
          <el-input v-model="apiInfo.case_name" placeholder="输入用例名称" clearable />
        </el-form-item>
        
        <el-form-item label="所属项目ID：" prop="project_id" @change="projectChange">
          <el-select v-model="apiInfo.project_id" placeholder="选择所属项目" filterable clearable>
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="用例描述：">
          <el-input v-model="apiInfo.case_desc" style="width: 600px" :rows="3" type="textarea" placeholder="请输入用例描述" />
        </el-form-item>

        <div class="form-wrapper">
          <div class="form-info">| 用例信息</div>
        </div>
        
        <el-form-item>
          <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 100%">
            <el-tab-pane label="当前用例步骤" name="当前用例步骤">
              <el-table :data="tableDataCaseStep" row-key="id" class="table_data" max-height="500">
                <el-table-column fixed="left" label="操作" width="80">
                  <template #default="scope">
                    <el-button link type="primary" size="small" @click="updateAppCaseStep(scope.row)">
                      确认修改
                    </el-button>
                    <br />
                    <el-button link type="primary" size="small" @click="onDeleteStep(scope.row.id)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>

                <el-table-column prop="step_order" label="执行顺序" width="120">
                  <template #default="scope">
                    <el-input-number v-model="scope.row.step_order" :min="1" style="width: 107px" controls-position="right" placeholder="顺序"/>
                  </template>
                </el-table-column>
                
                <el-table-column prop="step_desc" label="步骤描述" width="480">
                  <template #default="scope">
                    <el-input style="max-width: 600px; width: 360px" v-model="scope.row.step_desc" placeholder="输入步骤描述"></el-input>
                  </template>
                </el-table-column>
                
                <el-table-column prop="value" label="关键字操作" width="320">
                  <template #default="scope">
                    <el-cascader v-model="scope.row.value" :options="keyWordAllList" @change="onStepKeyModifyChange(scope.$index)" />
                  </template>
                </el-table-column>
                
                <el-table-column prop="ref_variable" label="关键字参数" type="expand" width="120">
                  <template #default="scope">
                    <span style="margin-left: 10px;" v-for="(variable, index) in findKeyWordByName(scope.row.value[1]).keyword_desc" :key="index">
                      <span style="margin-right: 10px;">{{ variable.name }}</span>
                      <!-- 如果是接口信息对象 -->
                      <el-select v-if="variable.name.endsWith('_接口信息')"
                                v-model="scope.row.ref_variable[variable.name]"
                                filterable placeholder="选择接口信息" 
                                style="width: 180px"  
                                clearable>
                        <el-option
                                v-for="dataRequest in dataRequestList"
                                :key="dataRequest.id"
                                :label="dataRequest.api_name"
                                :value="dataRequest.id" >
                        </el-option>
                      </el-select>
                      <!-- 如果是数据库信息对象 -->
                      <el-select v-else-if="variable.name.endsWith('_数据库')"
                                v-model="scope.row.ref_variable[variable.name]"
                                filterable placeholder="_数据库" 
                                style="width: 180px"  
                                clearable>
                        <el-option
                                v-for="dataDb in dataDbList"
                                :key="dataDb.id"
                                :label="dataDb.name"
                                :value="dataDb.id" >
                        </el-option>
                      </el-select>
                      <!-- 其他类型 -->
                      <el-input v-else
                                v-model="scope.row.ref_variable[variable.name]"
                                placeholder="输入参数值"
                                style="width: 180px" />
                    </span>
                  </template>
                </el-table-column>
              </el-table>
              
              <div style="margin-top: 20px;">
                <el-button type="primary" @click="onAddStep">添加步骤</el-button>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="调试结果" name="调试结果">
              <div v-if="debugResult" style="padding: 20px;">
                <h3>测试执行结果</h3>
                <pre>{{ debugResult }}</pre>
              </div>
              <div v-else style="padding: 20px; text-align: center; color: #999;">
                暂无调试结果，请点击"调试执行测试"按钮
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue"
import { queryByPage, deleteData, downloadTemplate, queryById, insertData, updateData, excuteTest } from '@/api/ApiInfoCase'
import { queryAllProject } from "@/api/ApiProject"
import { queryByPage as apiQueryByPage } from "@/api/ApiInfo"
import { queryAll as keywordQueryAll } from "@/api/ApiKeyWord"
import { queryAll as dbQueryAll } from "@/api/DbBaseManage"
import { useRouter } from "vue-router"
import { Message } from '@/utils/message'
import { useDeleteConfirm } from '@/composables/useDeleteConfirm'
import Breadcrumb from "../../Breadcrumb.vue"

const router = useRouter()
const { confirmDelete } = useDeleteConfirm()

// 视图控制
const currentView = ref('list')

// ========== 列表相关数据 ==========
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchForm = reactive({ "case_name": "", "api_info_id": "" })

const columnList = ref([
  { prop: "id", label: '用例编号' },
  { prop: "case_name", label: '用例名称' },
  { prop: "api_info_id", label: '所属接口' },
  { prop: "created_at", label: '创建时间' },
  { prop: "updated_at", label: '更新时间' }
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
  }).catch((error) => {
    tableData.value = []
    total.value = 0
  })
}

const handleSizeChange = (val) => {
  pageSize.value = val
  loadData()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  loadData()
}

const onDataForm = (index) => {
  currentView.value = 'form'
  if (index >= 0) {
    loadFormData(tableData.value[index]["id"])
  } else {
    resetForm()
  }
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
  // 处理导入命令
}

const onDownloadFile = () => {
  downloadTemplate().then((res) => {
    const blob = new Blob([res.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = '测试用例导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(link.href)
    Message.success("模板下载成功")
  }).catch((error) => {
    Message.error("下载模板失败：" + (error.response?.data?.msg || error.message))
  })
}

const onImportFile = () => {
  Message.info("导入用例功能开发中...")
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const tabActiveName = ref("当前用例步骤")

const apiInfo = reactive({
  id: 0,
  case_name: "",
  project_id: "",
  case_desc: ""
})

const rules = reactive({
  case_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '必填项', trigger: 'change' }
  ]
})

const projectList = ref([])
const tableDataCaseStep = ref([])
const keyWordAllList = ref([])
const dataRequestList = ref([])
const dataDbList = ref([])
const debugResult = ref("")

const loadFormData = async (id) => {
  const res = await queryById(id)
  apiInfo.id = res.data.data.id
  apiInfo.case_name = res.data.data.case_name
  apiInfo.project_id = res.data.data.project_id
  apiInfo.case_desc = res.data.data.case_desc
  // 加载步骤数据
  if (res.data.data.case_steps) {
    tableDataCaseStep.value = JSON.parse(res.data.data.case_steps)
  }
}

const resetForm = () => {
  apiInfo.id = 0
  apiInfo.case_name = ""
  apiInfo.project_id = ""
  apiInfo.case_desc = ""
  tableDataCaseStep.value = []
  debugResult.value = ""
}

const onSubmit = () => {
  if (!ruleFormRef.value) return
  ruleFormRef.value.validate((valid) => {
    if (!valid) return
    
    const data = {
      ...apiInfo,
      case_steps: JSON.stringify(tableDataCaseStep.value)
    }

    if (apiInfo.id > 0) {
      updateData(data).then((res) => {
        if (res.data.code == 200) {
          Message.success('更新成功')
          currentView.value = 'list'
          loadData()
        }
      })
    } else {
      insertData(data).then((res) => {
        if (res.data.code == 200) {
          Message.success('添加成功')
          currentView.value = 'list'
          loadData()
        }
      })
    }
  })
}

const onCancel = () => {
  currentView.value = 'list'
  loadData()
}

const projectChange = () => {
  // 项目选择变化处理
}

const onAddStep = () => {
  const newStep = {
    id: Date.now(),
    step_order: tableDataCaseStep.value.length + 1,
    step_desc: "",
    value: [],
    ref_variable: {}
  }
  tableDataCaseStep.value.push(newStep)
}

const updateAppCaseStep = (row) => {
  Message.success("步骤更新成功")
}

const onDeleteStep = (stepId) => {
  const index = tableDataCaseStep.value.findIndex(step => step.id === stepId)
  if (index > -1) {
    tableDataCaseStep.value.splice(index, 1)
    Message.success("步骤删除成功")
  }
}

const onStepKeyModifyChange = (index) => {
  // 步骤关键字变化处理
}

const findKeyWordByName = (keyWordName) => {
  // 根据关键字名称查找关键字详情
  return keyWordAllList.value.find(item => item.value === keyWordName) || { keyword_desc: [] }
}

const okExecuteTest = () => {
  const testData = {
    ...apiInfo,
    case_steps: JSON.stringify(tableDataCaseStep.value)
  }
  
  excuteTest(testData).then((res) => {
    debugResult.value = JSON.stringify(res.data, null, 2)
    Message.success('测试执行完成')
  }).catch((error) => {
    debugResult.value = JSON.stringify(error.response?.data || error.message, null, 2)
    Message.error('测试执行失败')
  })
}

// ========== 初始化 ==========
onMounted(() => {
  loadData()
  
  // 加载项目列表
  queryAllProject().then((res) => {
    projectList.value = res.data.data
  }).catch((error) => {
    projectList.value = []
  })
  
  // 加载API列表 - 使用分页接口获取所有数据
  const apiSearchData = { page: 1, pageSize: 1000 }
  apiQueryByPage(apiSearchData).then((res) => {
    apiList.value = res.data.data
  }).catch((error) => {
    apiList.value = []
  })
  
  // 加载关键字列表
  keywordQueryAll().then((res) => {
    keyWordAllList.value = res.data.data.map(item => ({
      value: item.name,
      label: item.name,
      children: item.keyword_desc ? item.keyword_desc.map(desc => ({
        value: desc.name,
        label: desc.name
      })) : []
    }))
  }).catch((error) => {
    keyWordAllList.value = []
  })
  
  // 加载数据库列表
  dbQueryAll().then((res) => {
    dataDbList.value = res.data.data
  }).catch((error) => {
    dataDbList.value = []
  })
  
  // 加载接口列表 - 使用分页接口获取所有数据
  apiQueryByPage(apiSearchData).then((res) => {
    dataRequestList.value = res.data.data
  }).catch((error) => {
    dataRequestList.value = []
  })
})
</script>

<style scoped>
.demo-pagination-block+.demo-pagination-block {
  margin-top: 10px;
}

.demo-pagination-block .demonstration {
  margin-bottom: 16px;
}

.form-wrapper {
  margin-bottom: 20px;
  border-bottom: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-info {
  font-weight: bold;
  color: #409eff;
}

.form-buttons {
  margin-left: auto;
}

.table_data {
  margin-top: 20px;
}
</style>
