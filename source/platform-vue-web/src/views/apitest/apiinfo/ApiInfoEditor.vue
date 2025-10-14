<template>
  <div class="api-editor-container">
    <el-card class="header-card">
      <div class="editor-header">
        <el-input
          v-model="apiInfo.api_name"
          placeholder="接口名称"
          class="name-input"
        />
        <el-button type="primary" @click="saveApiInfo">保存</el-button>
        <el-button type="success" @click="executeTest">发送测试</el-button>
        <el-button @click="goBack">返回</el-button>
      </div>
    </el-card>

    <div class="editor-content">
      <!-- 左侧请求配置 -->
      <div class="left-panel">
        <el-card>
          <template #header>
            <span>请求配置</span>
          </template>
          
          <!-- URL和请求方法 -->
          <div class="url-row">
            <el-select v-model="apiInfo.request_method" style="width: 120px">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
              <el-option label="PATCH" value="PATCH" />
            </el-select>
            <el-input
              v-model="apiInfo.request_url"
              placeholder="请输入请求URL"
              class="url-input"
            />
          </div>

          <!-- 请求参数标签页 -->
          <el-tabs v-model="activeTab" class="request-tabs">
            <!-- Params -->
            <el-tab-pane label="Params" name="params">
              <RequestParams v-model="apiInfo.request_params" />
            </el-tab-pane>

            <!-- Headers -->
            <el-tab-pane label="Headers" name="headers">
              <RequestHeaders v-model="apiInfo.request_headers" />
            </el-tab-pane>

            <!-- Body -->
            <el-tab-pane label="Body" name="body" v-if="showBodyTab">
              <RequestBody
                v-model:formData="apiInfo.request_form_datas"
                v-model:wwwFormData="apiInfo.request_www_form_datas"
                v-model:jsonData="apiInfo.requests_json_data"
                v-model:files="apiInfo.request_files"
              />
            </el-tab-pane>

            <!-- Pre-Script -->
            <el-tab-pane label="Pre-Script" name="pre-script">
              <ScriptPanel v-model="preScript" placeholder="前置脚本（在请求发送前执行）" />
            </el-tab-pane>

            <!-- Post-Script -->
            <el-tab-pane label="Post-Script" name="post-script">
              <ScriptPanel v-model="postScript" placeholder="后置脚本（在请求完成后执行）" />
            </el-tab-pane>

            <!-- Assertions -->
            <el-tab-pane label="Assertions" name="assertions">
              <AssertPanel v-model="assertions" />
            </el-tab-pane>

            <!-- Variables -->
            <el-tab-pane label="Variables" name="variables">
              <VariablePanel v-model="contextVars" />
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>

      <!-- 右侧响应结果 -->
      <div class="right-panel">
        <el-card>
          <template #header>
            <div class="response-header">
              <span>响应结果</span>
              <el-tag v-if="testResult.status" :type="testResult.status === 'success' ? 'success' : 'danger'">
                {{ testResult.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </div>
          </template>
          
          <ResponsePanel :result="testResult" :loading="testLoading" />
        </el-card>

        <!-- YAML预览 -->
        <el-card class="yaml-card">
          <template #header>
            <span>YAML用例预览</span>
          </template>
          <YamlPreview :apiInfo="apiInfo" :contextVars="contextVars" :assertions="assertions" />
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import RequestParams from './components/RequestParams.vue'
import RequestHeaders from './components/RequestHeaders.vue'
import RequestBody from './components/RequestBody.vue'
import ScriptPanel from './components/ScriptPanel.vue'
import AssertPanel from './components/AssertPanel.vue'
import VariablePanel from './components/VariablePanel.vue'
import ResponsePanel from './components/ResponsePanel.vue'
import YamlPreview from './components/YamlPreview.vue'
import { queryById as getApiInfo, insertData as createApiInfo, updateData as updateApiInfo } from './apiinfo.js'  // 修复：使用正确的导出名称
import { executeApiTest, getTestStatus } from './apiTest.js'

const route = useRoute()
const router = useRouter()

// 当前激活的标签页
const activeTab = ref('params')

// 接口信息
const apiInfo = ref({
  id: null,
  api_name: '',
  request_url: '',
  request_method: 'GET',
  request_params: '{}',
  request_headers: '{}',
  request_form_datas: '{}',
  request_www_form_datas: '{}',
  requests_json_data: '{}',
  request_files: '{}',
  project_id: null,
  group_id: null
})

// 测试相关数据
const preScript = ref([])
const postScript = ref([])
const assertions = ref([])
const contextVars = ref({})
const testResult = ref({})
const testLoading = ref(false)

// 是否显示Body标签页
const showBodyTab = computed(() => {
  return ['POST', 'PUT', 'PATCH'].includes(apiInfo.value.request_method)
})

// 监听请求方法变化，自动切换标签页
watch(() => apiInfo.value.request_method, (newMethod) => {
  if (['POST', 'PUT', 'PATCH'].includes(newMethod) && activeTab.value === 'params') {
    activeTab.value = 'body'
  } else if (!['POST', 'PUT', 'PATCH'].includes(newMethod) && activeTab.value === 'body') {
    activeTab.value = 'params'
  }
})

// 加载接口信息
const loadApiInfo = async () => {
  const id = route.params.id
  if (id && id !== 'new') {
    try {
      const res = await getApiInfo(id)
      if (res.code === 200 && res.data) {
        apiInfo.value = res.data
      }
    } catch (error) {
      ElMessage.error('加载接口信息失败')
    }
  }
}

// 保存接口信息
const saveApiInfo = async () => {
  if (!apiInfo.value.api_name) {
    ElMessage.warning('请输入接口名称')
    return
  }
  if (!apiInfo.value.request_url) {
    ElMessage.warning('请输入请求URL')
    return
  }

  try {
    let res
    if (apiInfo.value.id) {
      res = await updateApiInfo(apiInfo.value.id, apiInfo.value)
    } else {
      res = await createApiInfo(apiInfo.value)
    }

    if (res.code === 200) {
      ElMessage.success('保存成功')
      if (!apiInfo.value.id && res.data) {
        apiInfo.value.id = res.data.id
        router.replace(`/apitest/apiinfo/edit/${res.data.id}`)
      }
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 执行测试
const executeTest = async () => {
  if (!apiInfo.value.id) {
    const confirm = await ElMessageBox.confirm(
      '接口信息尚未保存，是否先保存再执行测试？',
      '提示',
      {
        confirmButtonText: '保存并测试',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).catch(() => false)

    if (confirm) {
      await saveApiInfo()
      if (!apiInfo.value.id) {
        return
      }
    } else {
      return
    }
  }

  testLoading.value = true
  testResult.value = {}

  try {
    const res = await executeApiTest({
      api_info_id: apiInfo.value.id,
      test_name: `${apiInfo.value.api_name}_测试`,
      context_vars: contextVars.value,
      pre_script: preScript.value,
      post_script: postScript.value,
      assertions: assertions.value
    })

    if (res.code === 200 && res.data) {
      const testId = res.data.test_id
      // 轮询查询测试状态
      pollTestStatus(testId)
    } else {
      ElMessage.error(res.msg || '执行测试失败')
      testLoading.value = false
    }
  } catch (error) {
    ElMessage.error('执行测试失败')
    testLoading.value = false
  }
}

// 轮询查询测试状态
const pollTestStatus = async (testId, maxAttempts = 30) => {
  let attempts = 0
  
  const poll = async () => {
    if (attempts >= maxAttempts) {
      ElMessage.warning('测试执行超时')
      testLoading.value = false
      return
    }

    try {
      const res = await getTestStatus(testId)
      if (res.code === 200 && res.data) {
        const status = res.data.status

        if (status === 'success' || status === 'failed') {
          testResult.value = res.data
          testLoading.value = false
          ElMessage.success('测试执行完成')
        } else if (status === 'running') {
          attempts++
          setTimeout(poll, 2000) // 2秒后再次查询
        }
      }
    } catch (error) {
      attempts++
      setTimeout(poll, 2000)
    }
  }

  poll()
}

// 返回列表
const goBack = () => {
  router.back()
}

onMounted(() => {
  loadApiInfo()
})
</script>

<style scoped lang="scss">
.api-editor-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 10px;

  .name-input {
    flex: 1;
  }
}

.editor-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.left-panel,
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.url-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;

  .url-input {
    flex: 1;
  }
}

.request-tabs {
  :deep(.el-tabs__content) {
    min-height: 400px;
  }
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.yaml-card {
  margin-top: 20px;
  
  :deep(.el-card__body) {
    max-height: 400px;
    overflow: auto;
  }
}
</style>
