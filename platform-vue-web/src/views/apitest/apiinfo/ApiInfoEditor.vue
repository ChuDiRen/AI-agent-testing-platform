<template>
  <div class="api-editor-container">
    <!-- 顶部操作栏 -->
    <el-card class="header-card" shadow="never">
      <div class="header-actions">
        <el-button type="primary" @click="handleSave">保存</el-button>
        <div class="executor-select-wrapper">
          <el-select 
            v-model="selectedExecutor" 
            placeholder="选择执行器" 
            size="default"
            style="width: 180px"
          >
            <el-option 
              v-for="executor in executorList" 
              :key="executor.id" 
              :label="executor.plugin_name" 
              :value="executor.plugin_code" 
            />
          </el-select>
        </div>
        <el-button type="success" :loading="testing" @click="handleExecuteTest">执行测试</el-button>
        <el-button @click="goBack">关闭</el-button>
      </div>
    </el-card>

    <!-- 基础信息区 -->
    <el-card class="info-card" shadow="never">
      <div class="base-info">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="info-item">
              <label>接口编号：</label>
              <el-input v-model="formData.id" disabled size="small" style="width: 200px" />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <label>接口名称：</label>
              <el-input v-model="formData.api_name" placeholder="示例：登录接口" size="small" style="width: 200px" />
            </div>
          </el-col>
          <el-col :span="8">
            <div class="info-item">
              <label>所属项目ID：</label>
              <el-select v-model="formData.project_id" placeholder="选择项目" size="small" style="width: 200px">
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
              </el-select>
            </div>
          </el-col>
        </el-row>
        
        <div class="info-item" style="margin-top: 15px">
          <label>接口描述：</label>
          <el-input 
            v-model="formData.description" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入接口描述"
            style="width: 100%"
          />
        </div>
      </div>
    </el-card>

    <!-- 接口信息区 -->
    <el-card class="request-card" shadow="never">
      <template #header>
        <span class="card-title">接口信息</span>
      </template>

      <!-- 请求方法和URL -->
      <div class="request-line">
        <el-select v-model="formData.request_method" size="large" style="width: 120px">
          <el-option label="GET" value="GET" />
          <el-option label="POST" value="POST" />
          <el-option label="PUT" value="PUT" />
          <el-option label="DELETE" value="DELETE" />
          <el-option label="PATCH" value="PATCH" />
        </el-select>
        <el-input 
          v-model="formData.request_url" 
          placeholder="http://shop-xo.hctestedu.com/?application=app&s=api/user/login"
          size="large"
          style="flex: 1; margin-left: 10px"
        />
      </div>

      <!-- URL参数标签页 -->
      <el-tabs v-model="activeTab" class="url-params-tabs">
        <!-- 请求头 Header -->
        <el-tab-pane label="请求头Header" name="header">
          <div class="params-editor">
            <el-table :data="headerParams" border size="small">
              <el-table-column prop="key" label="参数名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="参数名" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="value" label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="参数值" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button type="danger" link size="small" @click="removeHeaderParam(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" link size="small" @click="addHeaderParam" style="margin-top: 10px">+ 添加参数</el-button>
          </div>
        </el-tab-pane>

        <!-- 请求Body -->
        <el-tab-pane label="请求Body" name="body">
          <el-radio-group v-model="bodyType" size="small" style="margin-bottom: 15px">
            <el-radio-button value="none">无</el-radio-button>
            <el-radio-button value="form-data">form-data</el-radio-button>
            <el-radio-button value="x-www-form-urlencoded">x-www-form-urlencoded</el-radio-button>
            <el-radio-button value="raw">raw (JSON)</el-radio-button>
          </el-radio-group>

          <!-- form-data -->
          <div v-if="bodyType === 'form-data'" class="params-editor">
            <el-table :data="formDataParams" border size="small">
              <el-table-column prop="key" label="参数名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="参数名" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="value" label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="参数值" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button type="danger" link size="small" @click="removeFormDataParam(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" link size="small" @click="addFormDataParam" style="margin-top: 10px">+ 添加参数</el-button>
          </div>

          <!-- x-www-form-urlencoded -->
          <div v-else-if="bodyType === 'x-www-form-urlencoded'" class="params-editor">
            <el-table :data="wwwFormParams" border size="small">
              <el-table-column prop="key" label="参数名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="参数名" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="value" label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="参数值" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button type="danger" link size="small" @click="removeWwwFormParam(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" link size="small" @click="addWwwFormParam" style="margin-top: 10px">+ 添加参数</el-button>
          </div>

          <!-- raw (JSON) -->
          <div v-else-if="bodyType === 'raw'">
            <el-input 
              v-model="jsonBody" 
              type="textarea" 
              :rows="10" 
              placeholder='{\n  "username": "admin",\n  "password": "123456"\n}'
              style="font-family: monospace"
            />
          </div>
        </el-tab-pane>

        <!-- 变量定义 -->
        <el-tab-pane label="变量定义" name="variables">
          <div class="params-editor">
            <el-table :data="variableParams" border size="small">
              <el-table-column prop="key" label="变量名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="变量名" size="small" />
                </template>
              </el-table-column>
              <el-table-column prop="value" label="变量值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="变量值" size="small" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button type="danger" link size="small" @click="removeVariableParam(scope.$index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" link size="small" @click="addVariableParam" style="margin-top: 10px">+ 添加变量</el-button>
          </div>
        </el-tab-pane>

        <!-- 测试编辑器 -->
        <el-tab-pane label="测试编辑器" name="test">
          <el-alert title="提示" type="info" :closable="false" style="margin-bottom: 15px">
            这里可以编写测试断言和脚本
          </el-alert>
          <el-input 
            v-model="testScript" 
            type="textarea" 
            :rows="10" 
            placeholder="// 编写测试脚本示例：&#10;// assert(response.code === 200, '状态码应为200');"
            style="font-family: monospace"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 测试结果区 -->
    <el-card v-if="showTestResult" class="result-card" shadow="never">
      <template #header>
        <div class="result-header">
          <span class="card-title">测试结果</span>
          <el-tag v-if="testResult.status" :type="testResult.status === 'success' ? 'success' : 'danger'">
            {{ testResult.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </div>
      </template>

      <el-tabs v-model="resultTab">
        <el-tab-pane label="响应Body" name="response">
          <pre class="response-content">{{ formatJson(testResult.response) }}</pre>
        </el-tab-pane>
        <el-tab-pane label="响应头" name="headers">
          <pre class="response-content">{{ formatJson(testResult.headers) }}</pre>
        </el-tab-pane>
        <el-tab-pane label="请求详情" name="request">
          <pre class="response-content">{{ formatJson(testResult.request) }}</pre>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryById, insertData, updateData } from './apiinfo.js'
import { queryByPage as getProjectList } from '../project/apiProject.js'
import { executeTest as executeApiTest } from '../apitest/apiTest.js'
import { listEnabledPlugins } from '../../plugin/plugin.js'

const router = useRouter()
const route = useRoute()

// 项目列表
const projectList = ref([])

// 执行器列表
const executorList = ref([])
const selectedExecutor = ref('')
const testing = ref(false)

// 表单数据
const formData = reactive({
  id: null,
  api_name: '',
  project_id: null,
  description: '',
  request_method: 'POST',
  request_url: '',
  request_headers: '',
  request_params: '',
  request_form_datas: '',
  request_www_form_datas: '',
  requests_json_data: '',
  request_files: '',
  debug_vars: ''
})

// 当前激活的标签
const activeTab = ref('header')
const resultTab = ref('response')

// Body类型
const bodyType = ref('none')

// 参数列表
const headerParams = ref([])
const formDataParams = ref([])
const wwwFormParams = ref([])
const variableParams = ref([])

// JSON Body
const jsonBody = ref('')

// 测试脚本
const testScript = ref('')

// 测试结果
const showTestResult = ref(false)
const testResult = reactive({
  status: null,
  response: null,
  headers: null,
  request: null
})

// 加载项目列表
const loadProjectList = async () => {
  try {
    const res = await getProjectList({ page: 1, pageSize: 1000 })
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 加载接口数据
const loadApiInfo = async (id) => {
  try {
    const res = await queryById(id)
    if (res.data.code === 200 && res.data.data) {
      const data = res.data.data
      Object.keys(formData).forEach(key => {
        if (data[key] !== undefined) {
          formData[key] = data[key]
        }
      })
      
      // 解析参数
      parseParams()
    }
  } catch (error) {
    console.error('加载接口数据失败:', error)
    ElMessage.error('加载接口数据失败')
  }
}

// 解析参数
const parseParams = () => {
  try {
    // 解析Header
    if (formData.request_headers) {
      const headers = JSON.parse(formData.request_headers)
      headerParams.value = Object.entries(headers).map(([key, value]) => ({ key, value }))
    }
    
    // 解析form-data
    if (formData.request_form_datas) {
      const formDatas = JSON.parse(formData.request_form_datas)
      formDataParams.value = Object.entries(formDatas).map(([key, value]) => ({ key, value }))
      if (formDataParams.value.length > 0) bodyType.value = 'form-data'
    }
    
    // 解析www-form
    if (formData.request_www_form_datas) {
      const wwwForms = JSON.parse(formData.request_www_form_datas)
      wwwFormParams.value = Object.entries(wwwForms).map(([key, value]) => ({ key, value }))
      if (wwwFormParams.value.length > 0) bodyType.value = 'x-www-form-urlencoded'
    }
    
    // 解析JSON Body
    if (formData.requests_json_data) {
      jsonBody.value = typeof formData.requests_json_data === 'string' 
        ? formData.requests_json_data 
        : JSON.stringify(JSON.parse(formData.requests_json_data), null, 2)
      if (jsonBody.value) bodyType.value = 'raw'
    }
    
    // 解析变量
    if (formData.debug_vars) {
      const vars = JSON.parse(formData.debug_vars)
      variableParams.value = Object.entries(vars).map(([key, value]) => ({ key, value }))
    }
  } catch (error) {
    console.error('解析参数失败:', error)
  }
}

// 序列化参数
const serializeParams = () => {
  try {
    // 序列化Header
    if (headerParams.value.length > 0) {
      const headers = {}
      headerParams.value.forEach(item => {
        if (item.key) headers[item.key] = item.value || ''
      })
      formData.request_headers = JSON.stringify(headers)
    }
    
    // 序列化form-data
    if (bodyType.value === 'form-data' && formDataParams.value.length > 0) {
      const formDatas = {}
      formDataParams.value.forEach(item => {
        if (item.key) formDatas[item.key] = item.value || ''
      })
      formData.request_form_datas = JSON.stringify(formDatas)
    } else {
      formData.request_form_datas = ''
    }
    
    // 序列化www-form
    if (bodyType.value === 'x-www-form-urlencoded' && wwwFormParams.value.length > 0) {
      const wwwForms = {}
      wwwFormParams.value.forEach(item => {
        if (item.key) wwwForms[item.key] = item.value || ''
      })
      formData.request_www_form_datas = JSON.stringify(wwwForms)
    } else {
      formData.request_www_form_datas = ''
    }
    
    // 序列化JSON Body
    if (bodyType.value === 'raw' && jsonBody.value) {
      formData.requests_json_data = jsonBody.value
    } else {
      formData.requests_json_data = ''
    }
    
    // 序列化变量
    if (variableParams.value.length > 0) {
      const vars = {}
      variableParams.value.forEach(item => {
        if (item.key) vars[item.key] = item.value || ''
      })
      formData.debug_vars = JSON.stringify(vars)
    }
  } catch (error) {
    console.error('序列化参数失败:', error)
  }
}

// 添加Header参数
const addHeaderParam = () => {
  headerParams.value.push({ key: '', value: '' })
}

// 删除Header参数
const removeHeaderParam = (index) => {
  headerParams.value.splice(index, 1)
}

// 添加form-data参数
const addFormDataParam = () => {
  formDataParams.value.push({ key: '', value: '' })
}

// 删除form-data参数
const removeFormDataParam = (index) => {
  formDataParams.value.splice(index, 1)
}

// 添加www-form参数
const addWwwFormParam = () => {
  wwwFormParams.value.push({ key: '', value: '' })
}

// 删除www-form参数
const removeWwwFormParam = (index) => {
  wwwFormParams.value.splice(index, 1)
}

// 添加变量
const addVariableParam = () => {
  variableParams.value.push({ key: '', value: '' })
}

// 删除变量
const removeVariableParam = (index) => {
  variableParams.value.splice(index, 1)
}

// 保存
const handleSave = async () => {
  if (!formData.api_name) {
    ElMessage.warning('请输入接口名称')
    return
  }
  if (!formData.request_url) {
    ElMessage.warning('请输入请求URL')
    return
  }
  
  serializeParams()
  
  try {
    let res
    if (formData.id) {
      res = await updateData(formData)
    } else {
      res = await insertData(formData)
    }
    
    if (res.data.code === 200) {
      ElMessage.success('保存成功')
      if (!formData.id && res.data.data && res.data.data.id) {
        formData.id = res.data.data.id
      }
    } else {
      ElMessage.error(res.data.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败，请稍后重试')
  }
}

// 加载执行器列表
const loadExecutorList = async () => {
  try {
    const res = await listEnabledPlugins('executor')
    if (res.data.code === 200) {
      executorList.value = res.data.data || []
      // 默认选择第一个执行器
      if (executorList.value.length > 0 && !selectedExecutor.value) {
        selectedExecutor.value = executorList.value[0].plugin_code
      }
    }
  } catch (error) {
    console.error('加载执行器列表失败:', error)
  }
}

// 执行测试（按钮点击）
const handleExecuteTest = async () => {
  if (!selectedExecutor.value) {
    ElMessage.warning('请选择执行器')
    return
  }
  await handleSave()
  executeTest()
}

// 执行测试
const executeTest = async () => {
  if (!formData.request_url) {
    ElMessage.warning('请输入请求URL')
    return
  }
  
  if (!selectedExecutor.value) {
    ElMessage.warning('请选择执行器')
    return
  }
  
  serializeParams()
  testing.value = true
  
  try {
    const testData = {
      api_info_id: formData.id,
      request_method: formData.request_method,
      request_url: formData.request_url,
      request_headers: formData.request_headers,
      request_params: formData.request_params,
      request_body: formData.requests_json_data || formData.request_form_datas || formData.request_www_form_datas,
      executor_code: selectedExecutor.value  // 添加执行器代码
    }
    
    const res = await executeApiTest(testData)
    
    if (res.data.code === 200) {
      showTestResult.value = true
      testResult.status = 'success'
      testResult.response = res.data.data || res.data
      testResult.headers = res.headers || {}
      testResult.request = testData
      ElMessage.success('测试执行成功')
    } else {
      showTestResult.value = true
      testResult.status = 'error'
      testResult.response = res.data
      ElMessage.error(res.data.msg || '测试执行失败')
    }
  } catch (error) {
    console.error('测试执行失败:', error)
    showTestResult.value = true
    testResult.status = 'error'
    testResult.response = error.message || '测试执行失败'
    ElMessage.error('测试执行失败，请稍后重试')
  } finally {
    testing.value = false
  }
}

// 格式化JSON
const formatJson = (data) => {
  if (!data) return ''
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

// 返回
const goBack = () => {
  router.push('/ApiInfoList')
}

// 页面加载
onMounted(() => {
  loadProjectList()
  loadExecutorList()
  
  const id = route.query.id
  if (id) {
    loadApiInfo(parseInt(id))
  } else {
    // 新增模式，添加默认参数
    addHeaderParam()
  }
})
</script>

<style scoped lang="scss">
.api-editor-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}

.header-card,
.info-card,
.request-card,
.result-card {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.executor-select-wrapper {
  margin-left: 20px;
}

.base-info {
  .info-item {
    display: flex;
    align-items: center;
    
    label {
      white-space: nowrap;
      margin-right: 10px;
      font-weight: 500;
      color: #606266;
    }
  }
}

.card-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.request-line {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.url-params-tabs {
  margin-top: 20px;
  
  :deep(.el-tabs__content) {
    padding: 20px 0;
  }
}

.params-editor {
  :deep(.el-input__inner) {
    border-radius: 4px;
  }
}

.response-content {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
  max-height: 400px;
  overflow: auto;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
