<template>
  <div>
    <!-- 列表视图 -->
    <div v-if="currentView === 'list'">
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
        <el-pagination :current-page="currentPage" :page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
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

    <!-- 表单视图 -->
    <div v-else>
      <!-- 面包屑导航 -->
      <Breadcrumb />
      <el-form ref="ruleFormRef" :inline="true" :model="apiInfo" :rules="rules" class="demo-form-inline">
        <!-- 模块 - 基础信息部分 - 按钮部分 -->
        <div class="form-wrapper">
          <div class="form-info">| 基础信息</div>
          <el-form-item class="form-buttons">
            <el-button type="primary" @click="onSubmit()">保存</el-button>
            <el-dropdown trigger="click">
              <el-button type="warning" style="margin-left: 10px;margin-right: 10px;">
                调试操作<el-icon><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="debugRequest">发送请求</el-dropdown-item>
                  <el-dropdown-item @click="downloadResponseData">发送并下载</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button @click="onCancel">关闭</el-button>
          </el-form-item>
        </div>

        <!-- 模块 - 基础信息部分 - 字段部分 -->
        <div>
          <el-form-item label="接口编号：">
            <el-input v-model="apiInfo.id" placeholder="接口编号" clearable disabled />
          </el-form-item>
          <el-form-item label="接口名称：">
            <el-input v-model="apiInfo.api_name" placeholder="输入接口名称" clearable prop="api_name" />
          </el-form-item>
          <el-form-item label="所属项目ID：" prop="project_id">
            <el-select v-model="apiInfo.project_id" placeholder="选择所属项目" filterable clearable>
              <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="接口描述：">
          <el-input v-model="apiInfo.case_desc" style="width: 600px" :rows="3" type="textarea" placeholder="请输入接口描述" />
        </el-form-item>

        <!-- 模块 - 接口信息部分 - 字段部分 -->
        <div class="form-wrapper">
          <div class="form-info">| 接口信息</div>
        </div>

        <el-select v-model="apiInfo.request_method" placeholder="请求方式" style="width: 100px; margin-left: 0px;">
          <el-option label="POST" value="POST" />
          <el-option label="GET" value="GET" />
          <el-option label="DELETE" value="DELETE" />
          <el-option label="PUT" value="PUT" />
          <el-option label="PATCH" value="PATCH" />
          <el-option label="COPY" value="COPY" />
          <el-option label="HEAD" value="HEAD" />
          <el-option label="OPTIONS" value="OPTIONS" />
        </el-select>
        <el-input v-model="apiInfo.request_url" placeholder="请求URL" style="width: 800px; margin-left: 0px;"/>

        <!-- 模块 - 接口信息部分 - 请求参数部分 -->
        <el-form-item style="margin-top: 10px;">
          <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 1150px;">
            <el-tab-pane label="URL参数" name="URL参数">
              <!-- 维护对应URL参数 -->
              <el-table :data="apiInfo.request_params" style="width: 100%" max-height="250">
                <el-table-column prop="key" label="参数名" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="参数名" />
                    <span v-else>{{ scope.row.key }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="参数" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="参数" />
                    <span v-else>{{ scope.row.value }}</span>
                  </template>
                </el-table-column>
                <el-table-column fixed="right" label="操作" style="width: 20%">
                  <template #default="scope">
                    <el-button link type="primary" size="small" @click.prevent="toggleEdit(scope.row)">
                      {{ scope.row.editing ? '确认' : '修改' }}
                    </el-button>
                    <el-button link type="primary" size="small" @click.prevent="deleteParams(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 添加 - 添加对应URL参数 -->
              <div id="addData">
                <el-input v-model="requestParams.key" placeholder="输入参数名" style="width: 30%" />
                <el-input v-model="requestParams.value" placeholder="输入参数" style="width: 30%" />
                <el-button style="width: 20%" @click="onAddParams">添加</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="请求头Header" name="请求头Header">
              <el-table :data="apiInfo.request_headers" style="width: 100%" max-height="250">
                <el-table-column prop="key" label="请求头名" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="参数名" />
                    <span v-else>{{ scope.row.key }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="请求头参数" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="参数" />
                    <span v-else>{{ scope.row.value }}</span>
                  </template>
                </el-table-column>
                <el-table-column fixed="right" label="操作" style="width: 20%">
                  <template #default="scope">
                    <el-button link type="primary" size="small" @click.prevent="toggleEdit(scope.row)">
                      {{ scope.row.editing ? '确认' : '修改' }}
                    </el-button>
                    <el-button link type="primary" size="small" @click.prevent="deleteHeaders(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <!-- 添加 - 添加对应Header参数 -->
              <div id="addData">
                <el-input v-model="requestHeaders.key" placeholder="输入请求头名" style="width: 30%" />
                <el-input v-model="requestHeaders.value" placeholder="输入请求头参数" style="width: 30%" />
                <el-button style="width: 20%" @click="onAddHeaders">添加</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="请求Body" name="请求Body">
              <el-tabs class="demo-tabs" model-value="form-data">
                <!-- Body-form-data -->
                <el-tab-pane label="form-data" name="form-data">
                  <el-table :data="apiInfo.request_form_datas" style="width: 100%" max-height="250">
                    <el-table-column prop="key" label="表单参数名" style="width: 30%">
                      <template #default="scope">
                        <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="表单参数名" />
                        <span v-else>{{ scope.row.key }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="表单参数" style="width: 30%">
                      <template #default="scope">
                        <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="表单参数" />
                        <span v-else>{{ scope.row.value }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column fixed="right" label="操作" style="width: 20%">
                      <template #default="scope">
                        <el-button link type="primary" size="small" @click.prevent="toggleEdit(scope.row)">
                          {{ scope.row.editing ? '确认' : '修改' }}
                        </el-button>
                        <el-button link type="primary" size="small" @click.prevent="deleteBodyFormDatas(scope.$index)">
                          删除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div id="addData">
                    <el-input v-model="requestBodyFormDatas.key" placeholder="输入表单参数名" style="width: 30%"/>
                    <el-input v-model="requestBodyFormDatas.value" placeholder="输入表单参数" style="width: 30%" />
                    <el-button style="width: 20%" @click="onAddBodyFormDatas">添加</el-button>
                  </div>
                </el-tab-pane>

                <!-- Body-x-www-form-data -->
                <el-tab-pane label="x-www-form-data" name="x-www-form-data">
                  <el-table :data="apiInfo.request_www_form_datas" style="width: 100%" max-height="250">
                    <el-table-column prop="key" label="表单参数名" style="width: 30%">
                      <template #default="scope">
                        <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="表单参数名" />
                        <span v-else>{{ scope.row.key }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="表单参数" style="width: 30%">
                      <template #default="scope">
                        <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="表单参数" />
                        <span v-else>{{ scope.row.value }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column fixed="right" label="操作" style="width: 20%">
                      <template #default="scope">
                        <el-button link type="primary" size="small" @click.prevent="toggleEdit(scope.row)">
                          {{ scope.row.editing ? '确认' : '修改' }}
                        </el-button>
                        <el-button link type="primary" size="small" @click.prevent="deleteBodyWwwFormDatas(scope.$index)">
                          删除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div id="addData">
                    <el-input v-model="requestBodyWwwFormDatas.key" placeholder="输入表单参数名" style="width: 30%"/>
                    <el-input v-model="requestBodyWwwFormDatas.value" placeholder="输入表单参数" style="width: 30%" />
                    <el-button style="width: 20%" @click="onAddBodyWwwFormDatas">添加</el-button>
                  </div>
                </el-tab-pane>

                <!-- Body-json -->
                <el-tab-pane label="json" name="json">
                  <el-input v-model="apiInfo.request_body_json" type="textarea" :rows="10" placeholder="请输入JSON格式的请求体" />
                </el-tab-pane>

                <!-- Body-files -->
                <el-tab-pane label="files" name="files">
                  <el-table :data="apiInfo.request_files" style="width: 100%" max-height="250">
                    <el-table-column prop="key" label="文件参数名" style="width: 30%">
                      <template #default="scope">
                        <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="文件参数名" />
                        <span v-else>{{ scope.row.key }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="文件路径" style="width: 30%">
                      <template #default="scope">
                        <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="文件路径" />
                        <span v-else>{{ scope.row.value }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column fixed="right" label="操作" style="width: 20%">
                      <template #default="scope">
                        <el-button link type="primary" size="small" @click.prevent="toggleEdit(scope.row)">
                          {{ scope.row.editing ? '确认' : '修改' }}
                        </el-button>
                        <el-button link type="primary" size="small" @click.prevent="deleteFiles(scope.$index)">
                          删除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                  <div id="addData">
                    <el-input v-model="requestFiles.key" placeholder="输入文件参数名" style="width: 30%"/>
                    <el-input v-model="requestFiles.value" placeholder="输入文件路径" style="width: 30%" />
                    <el-button style="width: 20%" @click="onAddFiles">添加</el-button>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </el-tab-pane>

            <el-tab-pane label="变量定义" name="变量定义">
              <el-table :data="apiInfo.variables" style="width: 100%" max-height="250">
                <el-table-column prop="key" label="变量名" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="变量名" />
                    <span v-else>{{ scope.row.key }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="value" label="变量值" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="变量值" />
                    <span v-else>{{ scope.row.value }}</span>
                  </template>
                </el-table-column>
                <el-table-column fixed="right" label="操作" style="width: 20%">
                  <template #default="scope">
                    <el-button link type="primary" size="small" @click.prevent="toggleEdit(scope.row)">
                      {{ scope.row.editing ? '确认' : '修改' }}
                    </el-button>
                    <el-button link type="primary" size="small" @click.prevent="deleteVariables(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div id="addData">
                <el-input v-model="variables.key" placeholder="输入变量名" style="width: 30%" />
                <el-input v-model="variables.value" placeholder="输入变量值" style="width: 30%" />
                <el-button style="width: 20%" @click="onAddVariables">添加</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="调试输出内容" name="调试输出内容">
              <div v-if="debugResult" style="padding: 20px;">
                <h3>调试结果</h3>
                <pre>{{ debugResult }}</pre>
              </div>
              <div v-else style="padding: 20px; text-align: center; color: #999;">
                暂无调试结果，请点击"调试操作"按钮
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
import { queryByPage, deleteData, queryById, insertData, updateData, doImportSwagger, doDebugRequest, downloadResponse } from '@/api/ApiInfo'
import { queryAllProject } from "@/api/ApiProject"
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
const searchForm = reactive({ "api_name": "", "project_id": "", "module_id": "" })

const columnList = ref([
  { prop: "id", label: '接口用例编号' },
  { prop: "api_name", label: '接口名称' },
  { prop: "request_method", label: '请求方法' },
  { prop: "request_url", label: '请求地址' },
  { prop: "created_at", label: '创建时间' },
  { prop: "updated_at", label: '更新时间' }
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
  const apiId = tableData.value[index]["id"]
  const apiName = tableData.value[index]["api_name"]

  await confirmDelete(
    () => deleteData(apiId),
    `确定要删除API "${apiName}" 吗？此操作不可恢复！`,
    'API删除成功',
    loadData
  )
}

function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data
  })
}

const projectChange = () => {
  // 项目选择变化处理
}

// Swagger 导入相关
const swaggerDialogVisible = ref(false)
const swaggerForm = reactive({
  version: "",
  host: "",
  project_id: ""
})

const loadSwagger = () => {
  swaggerDialogVisible.value = true
}

const confirmSwaggerImport = () => {
  doImportSwagger(swaggerForm).then((res) => {
    loadData()
  })
  swaggerDialogVisible.value = false
}

// ========== 表单相关数据 ==========
const ruleFormRef = ref()
const tabActiveName = ref("URL参数")

const apiInfo = reactive({
  id: 0,
  api_name: "",
  project_id: "",
  case_desc: "",
  request_method: "",
  request_url: "",
  request_params: [],
  request_headers: [],
  request_form_datas: [],
  request_www_form_datas: [],
  request_body_json: "",
  request_files: [],
  variables: []
})

const rules = reactive({
  api_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  project_id: [
    { required: true, message: '必填项', trigger: 'change' }
  ]
})

// 参数管理相关
const requestParams = reactive({ key: "", value: "" })
const requestHeaders = reactive({ key: "", value: "" })
const requestBodyFormDatas = reactive({ key: "", value: "" })
const requestBodyWwwFormDatas = reactive({ key: "", value: "" })
const requestFiles = reactive({ key: "", value: "" })
const variables = reactive({ key: "", value: "" })

const debugResult = ref("")

const loadFormData = async (id) => {
  const res = await queryById(id)
  apiInfo.id = res.data.data.id
  apiInfo.api_name = res.data.data.api_name
  apiInfo.project_id = res.data.data.project_id
  apiInfo.case_desc = res.data.data.case_desc
  apiInfo.request_method = res.data.data.request_method
  apiInfo.request_url = res.data.data.request_url
  apiInfo.request_params = res.data.data.request_params || []
  apiInfo.request_headers = res.data.data.request_headers || []
  apiInfo.request_form_datas = res.data.data.request_form_datas || []
  apiInfo.request_www_form_datas = res.data.data.request_www_form_datas || []
  apiInfo.request_body_json = res.data.data.request_body_json || ""
  apiInfo.request_files = res.data.data.request_files || []
  apiInfo.variables = res.data.data.variables || []
}

const resetForm = () => {
  apiInfo.id = 0
  apiInfo.api_name = ""
  apiInfo.project_id = ""
  apiInfo.case_desc = ""
  apiInfo.request_method = ""
  apiInfo.request_url = ""
  apiInfo.request_params = []
  apiInfo.request_headers = []
  apiInfo.request_form_datas = []
  apiInfo.request_www_form_datas = []
  apiInfo.request_body_json = ""
  apiInfo.request_files = []
  apiInfo.variables = []
  debugResult.value = ""
}

const onSubmit = () => {
  if (!ruleFormRef.value) return
  ruleFormRef.value.validate((valid) => {
    if (!valid) return
    
    if (apiInfo.id > 0) {
      updateData(apiInfo).then((res) => {
        if (res.data.code == 200) {
          Message.success('更新成功')
          currentView.value = 'list'
          loadData()
        }
      })
    } else {
      insertData(apiInfo).then((res) => {
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

// 参数管理方法
const toggleEdit = (row) => {
  row.editing = !row.editing
}

const onAddParams = () => {
  if (requestParams.key && requestParams.value) {
    apiInfo.request_params.push({
      key: requestParams.key,
      value: requestParams.value,
      editing: false
    })
    requestParams.key = ""
    requestParams.value = ""
  }
}

const deleteParams = (index) => {
  apiInfo.request_params.splice(index, 1)
}

const onAddHeaders = () => {
  if (requestHeaders.key && requestHeaders.value) {
    apiInfo.request_headers.push({
      key: requestHeaders.key,
      value: requestHeaders.value,
      editing: false
    })
    requestHeaders.key = ""
    requestHeaders.value = ""
  }
}

const deleteHeaders = (index) => {
  apiInfo.request_headers.splice(index, 1)
}

const onAddBodyFormDatas = () => {
  if (requestBodyFormDatas.key && requestBodyFormDatas.value) {
    apiInfo.request_form_datas.push({
      key: requestBodyFormDatas.key,
      value: requestBodyFormDatas.value,
      editing: false
    })
    requestBodyFormDatas.key = ""
    requestBodyFormDatas.value = ""
  }
}

const deleteBodyFormDatas = (index) => {
  apiInfo.request_form_datas.splice(index, 1)
}

const onAddBodyWwwFormDatas = () => {
  if (requestBodyWwwFormDatas.key && requestBodyWwwFormDatas.value) {
    apiInfo.request_www_form_datas.push({
      key: requestBodyWwwFormDatas.key,
      value: requestBodyWwwFormDatas.value,
      editing: false
    })
    requestBodyWwwFormDatas.key = ""
    requestBodyWwwFormDatas.value = ""
  }
}

const deleteBodyWwwFormDatas = (index) => {
  apiInfo.request_www_form_datas.splice(index, 1)
}

const onAddFiles = () => {
  if (requestFiles.key && requestFiles.value) {
    apiInfo.request_files.push({
      key: requestFiles.key,
      value: requestFiles.value,
      editing: false
    })
    requestFiles.key = ""
    requestFiles.value = ""
  }
}

const deleteFiles = (index) => {
  apiInfo.request_files.splice(index, 1)
}

const onAddVariables = () => {
  if (variables.key && variables.value) {
    apiInfo.variables.push({
      key: variables.key,
      value: variables.value,
      editing: false
    })
    variables.key = ""
    variables.value = ""
  }
}

const deleteVariables = (index) => {
  apiInfo.variables.splice(index, 1)
}

// 调试相关方法
const debugRequest = () => {
  debugApi(apiInfo).then((res) => {
    debugResult.value = JSON.stringify(res.data, null, 2)
    Message.success('调试请求完成')
  }).catch((error) => {
    debugResult.value = JSON.stringify(error.response?.data || error.message, null, 2)
    Message.error('调试请求失败')
  })
}

const downloadResponseData = () => {
  downloadApi(apiInfo).then((res) => {
    const blob = new Blob([res.data], { type: 'application/json' })
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = 'response.json'
    link.click()
    window.URL.revokeObjectURL(link.href)
    Message.success('下载完成')
  }).catch((error) => {
    Message.error('下载失败')
  })
}

// ========== 初始化 ==========
onMounted(() => {
  loadData()
  getProjectList()
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

#addData {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
</style>
