<template>
  <div class="page-container">
    <el-card class="page-card">
      <!-- 顶部标题和操作栏 -->
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Connection /></el-icon>
            <h3>{{ isEdit ? '编辑接口信息' : '新增接口信息' }}</h3>
            <span class="subtitle">{{ isEdit ? '修改现有API接口配置' : '创建新的API接口配置' }}</span>
          </div>
          <div class="header-right">
            <el-select v-model="currentExecutorCode" placeholder="选择执行器" style="width: 160px; margin-right: 12px">
              <el-option
                v-for="exe in executorList"
                :key="exe.plugin_code"
                :label="exe.plugin_name"
                :value="exe.plugin_code"
              />
            </el-select>
            <el-button type="primary" @click="submitForm" :loading="submitting">
              保存接口
            </el-button>
            <el-button type="success" :loading="testing" @click="handleTestCommand('sendRequest')">
              发送请求
            </el-button>
            <el-button type="warning" @click="addToTestCase" :loading="addingCase">
              加入测试用例
            </el-button>
            <el-button @click="goBack">
              关闭
            </el-button>
          </div>
        </div>
      </template>

      <!-- 基础信息 -->
      <div class="form-section">
        <div class="section-header">
          <h4 class="section-title">基础信息</h4>
        </div>
        <div class="form-content">
          <el-form :model="ruleForm" label-width="100px">
            <el-row :gutter="24">
              <el-col :span="6">
                <el-form-item label="接口编号">
                  <el-input v-model="ruleForm.id" disabled placeholder="系统自动生成" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="接口名称" required>
                  <el-input v-model="ruleForm.api_name" placeholder="示例：用户登录接口" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="所属项目">
                  <el-select v-model="ruleForm.project_id" placeholder="选择项目" style="width: 100%">
                    <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </div>

      <!-- 接口配置 -->
      <div class="form-section">
        <div class="section-header">
          <h4 class="section-title">接口配置</h4>
        </div>
        <div class="api-config-content">
          <div class="request-line">
            <el-select v-model="ruleForm.request_method" placeholder="POST" class="method-select">
              <el-option v-for="method in methodList" :key="method" :label="method" :value="method" />
            </el-select>
            <el-input 
              v-model="ruleForm.request_url" 
              placeholder="https://api.example.com/v1/users/login" 
              class="url-input"
            />
          </div>

        <!-- 标签页 -->
        <el-tabs v-model="activeTab" class="params-tabs">
          <!-- URL参数 -->
          <el-tab-pane label="URL参数" name="params">
            <el-table :data="urlParams" border :show-header="true">
              <el-table-column label="参数名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="参数名" />
                </template>
              </el-table-column>
              <el-table-column label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="参数值" />
                </template>
              </el-table-column>
              <el-table-column label="描述" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.description" placeholder="参数描述" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button link type="danger" @click="removeUrlParam(scope.$index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" @click="addUrlParam" style="margin-top: 12px">
              添加参数
            </el-button>
          </el-tab-pane>

          <!-- 请求头Header -->
          <el-tab-pane label="请求头Header" name="headers">
            <el-table :data="headerParams" border>
              <el-table-column label="参数名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="Content-Type" />
                </template>
              </el-table-column>
              <el-table-column label="参数值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="application/json" />
                </template>
              </el-table-column>
              <el-table-column label="描述" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.description" placeholder="请求内容类型" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button link type="danger" @click="removeHeaderParam(scope.$index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" @click="addHeaderParam" style="margin-top: 12px">
              添加请求头
            </el-button>
          </el-tab-pane>

          <!-- 请求Body -->
          <el-tab-pane label="请求Body" name="body">
            <el-radio-group v-model="bodyType" style="margin-bottom: 16px">
              <el-radio-button value="none">无</el-radio-button>
              <el-radio-button value="form-data">form-data</el-radio-button>
              <el-radio-button value="x-www-form-urlencoded">urlencoded</el-radio-button>
              <el-radio-button value="raw">JSON</el-radio-button>
            </el-radio-group>

            <!-- form-data -->
            <div v-if="bodyType === 'form-data'">
              <el-table :data="formDataParams" border>
                <el-table-column label="参数名" width="200">
                  <template #default="scope">
                    <el-input v-model="scope.row.key" placeholder="参数名" />
                  </template>
                </el-table-column>
                <el-table-column label="参数值">
                  <template #default="scope">
                    <el-input v-model="scope.row.value" placeholder="参数值" />
                  </template>
                </el-table-column>
                <el-table-column label="描述" width="200">
                  <template #default="scope">
                    <el-input v-model="scope.row.description" placeholder="参数描述" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" align="center">
                  <template #default="scope">
                    <el-button link type="danger" @click="removeFormDataParam(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" @click="addFormDataParam" style="margin-top: 12px">
                添加参数
              </el-button>
            </div>

            <!-- x-www-form-urlencoded -->
            <div v-else-if="bodyType === 'x-www-form-urlencoded'">
              <el-table :data="wwwFormParams" border>
                <el-table-column label="参数名" width="200">
                  <template #default="scope">
                    <el-input v-model="scope.row.key" placeholder="参数名" />
                  </template>
                </el-table-column>
                <el-table-column label="参数值">
                  <template #default="scope">
                    <el-input v-model="scope.row.value" placeholder="参数值" />
                  </template>
                </el-table-column>
                <el-table-column label="描述" width="200">
                  <template #default="scope">
                    <el-input v-model="scope.row.description" placeholder="参数描述" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" align="center">
                  <template #default="scope">
                    <el-button link type="danger" @click="removeWwwFormParam(scope.$index)">
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <el-button type="primary" @click="addWwwFormParam" style="margin-top: 12px">
                添加参数
              </el-button>
            </div>

            <!-- raw (JSON) -->
            <div v-else-if="bodyType === 'raw'" class="json-editor-container">
              <!-- JSON工具栏 -->
              <div class="json-toolbar">
                <div class="json-toolbar-left">
                  <span class="json-label">JSON Body</span>
                  <el-tag v-if="jsonValidStatus === 'valid'" type="success" size="small">格式正确</el-tag>
                  <el-tag v-else-if="jsonValidStatus === 'invalid'" type="danger" size="small">格式错误</el-tag>
                </div>
                <div class="json-toolbar-right">
                  <el-button size="small" @click="formatJson">格式化</el-button>
                  <el-button size="small" @click="compressJson">压缩</el-button>
                  <el-button size="small" @click="clearJson">清空</el-button>
                  <el-button size="small" @click="validateJson">验证</el-button>
                </div>
              </div>
              
              <!-- JSON编辑器 -->
              <el-input 
                v-model="jsonBody" 
                type="textarea" 
                :rows="15" 
                placeholder='{\n  "username": "admin",\n  "password": "123456"\n}'
                class="json-editor"
                @blur="validateJson"
              />
              
              <!-- 错误提示 -->
              <div v-if="jsonError" class="json-error">
                <el-alert type="error" :closable="false" show-icon>
                  <template #title>
                    JSON格式错误: {{ jsonError }}
                  </template>
                </el-alert>
              </div>
            </div>

            <!-- 无Body -->
            <div v-else-if="bodyType === 'none'" style="text-align: center; padding: 40px; color: #909399;">
              该请求不包含Body内容
            </div>
          </el-tab-pane>

          <!-- 变量定义 -->
          <el-tab-pane label="变量定义" name="variables">
            <el-table :data="variableParams" border>
              <el-table-column label="变量名" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.key" placeholder="token" />
                </template>
              </el-table-column>
              <el-table-column label="变量值">
                <template #default="scope">
                  <el-input v-model="scope.row.value" placeholder="eyJhbGciOiJIUzI1NiIs..." />
                </template>
              </el-table-column>
              <el-table-column label="描述" width="200">
                <template #default="scope">
                  <el-input v-model="scope.row.description" placeholder="用户认证令牌" />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button link type="danger" @click="removeVariableParam(scope.$index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" @click="addVariableParam" style="margin-top: 12px">
              添加变量
            </el-button>
          </el-tab-pane>

          <!-- 调试输出内容 -->
          <el-tab-pane label="调试输出内容" name="debug">
            <div v-if="debugResult" class="debug-result-wrapper">
              <div class="debug-status-bar" :class="debugResult.status === 'completed' ? 'success' : 'failed'">
                <div class="status-content">
                  <strong>调试结果: {{ debugResult.status === 'completed' ? 'PASSED' : 'FAILED' }}</strong> 
                  <span class="separator">|</span> 
                  <span>请求方式: {{ debugResult.request?.method }}</span> 
                  <span class="separator">|</span> 
                  <span>请求URL: {{ debugResult.request?.url }}</span>
                </div>
                <el-icon><ArrowDown /></el-icon>
              </div>
              
              <div class="debug-detail">
                <div class="detail-row">
                  <div class="detail-label">请求URL:</div>
                  <div class="detail-value">{{ debugResult.request?.url }}</div>
                </div>
                
                <div class="detail-row">
                  <div class="detail-label">请求方式:</div>
                  <div class="detail-value">{{ debugResult.request?.method }}</div>
                </div>

                <div class="detail-block" v-if="debugResult.request?.headers">
                  <div class="detail-label">请求头:</div>
                  <JsonViewer :data="debugResult.request.headers" :default-expanded="true" />
                </div>

                <div class="detail-block" v-if="debugResult.request?.body || debugResult.request?.data || debugResult.request?.json">
                  <div class="detail-label">请求数据:</div>
                  <JsonViewer :data="getParsedRequestBody(debugResult.request)" :default-expanded="true" />
                </div>

                <div class="detail-block" v-if="debugResult.response?.body">
                  <div class="detail-label">响应数据:</div>
                  <JsonViewer :data="debugResult.response.body" :default-expanded="true" />
                </div>
                
                <div class="detail-block" v-if="debugResult.error">
                  <div class="detail-label text-danger">错误信息:</div>
                  <div class="code-box error-box">
                    <pre>{{ debugResult.error }}</pre>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="debug-result-wrapper">
              <div class="debug-status-bar preview">
                <div class="status-content">
                  <strong>请求预览</strong> 
                  <span class="separator">|</span> 
                  <span>请求方式: {{ ruleForm.request_method || 'GET' }}</span> 
                  <span class="separator">|</span> 
                  <span>请求URL: {{ ruleForm.request_url || '未设置' }}</span>
                </div>
              </div>
              
              <div class="debug-detail">
                <div class="detail-row">
                  <div class="detail-label">请求URL:</div>
                  <div class="detail-value">{{ ruleForm.request_url || '未设置' }}</div>
                </div>
                
                <div class="detail-row">
                  <div class="detail-label">请求方式:</div>
                  <div class="detail-value">{{ ruleForm.request_method || 'GET' }}</div>
                </div>

                <div class="detail-block" v-if="getRequestPreview().headers">
                  <div class="detail-label">请求头:</div>
                  <JsonViewer :data="getRequestPreview().headers" :default-expanded="true" />
                </div>

                <div class="detail-block" v-if="getRequestPreview().body">
                  <div class="detail-label">请求数据:</div>
                  <JsonViewer :data="getRequestPreview().body" :default-expanded="true" />
                </div>

                <div class="preview-hint" v-if="!ruleForm.request_url">
                  <el-empty description="请先配置接口URL和参数" :image-size="60" />
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { Connection, ArrowDown } from '@element-plus/icons-vue';
import { queryById, insertData, updateData, getMethods } from './apiinfo.js';
import { queryByPage as getProjectList } from '~/views/apitest/project/apiProject.js';
import { listExecutors, executeTask } from '~/views/apitest/task/apiTask.js';
import { insertData as insertCaseData, updateData as updateCaseData, queryByPage as queryCaseList, queryKeywordsByType } from '~/views/apitest/apiinfocase/apiInfoCase.js';
import { queryAll as queryOperationTypes } from '~/views/apitest/keyword/operationType.js';
import { useRouter, useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from 'element-plus';
import JsonViewer from '~/components/JsonViewer.vue';

const router = useRouter();
const route = useRoute();

// 是否编辑模式
const isEdit = ref(false);

// 加载状态
const submitting = ref(false);
const testing = ref(false);
const addingCase = ref(false);

// 项目列表
const projectList = ref([]);

// 执行器列表与当前选择
const executorList = ref([]);
const currentExecutorCode = ref('');

// 请求方法列表
const methodList = ref(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']);

// 当前激活的标签
const activeTab = ref('params');

// Body类型
const bodyType = ref('none');

// 参数列表（默认都有一行空数据）
const urlParams = ref([{ key: '', value: '', description: '' }]);
const headerParams = ref([{ key: '', value: '', description: '' }]);
const formDataParams = ref([{ key: '', value: '', description: '' }]);
const wwwFormParams = ref([{ key: '', value: '', description: '' }]);
const variableParams = ref([{ key: '', value: '', description: '' }]);

// 调试输出内容
const debugOutput = ref('');
const debugResult = ref(null);

// JSON Body
const jsonBody = ref('');
const jsonValidStatus = ref(''); // 'valid' | 'invalid' | ''
const jsonError = ref('');

// 表单数据
const ruleForm = reactive({
  id: null,
  project_id: null,
  api_name: '',
  request_method: 'POST',
  request_url: '',
  request_params: '',
  request_headers: '',
  debug_vars: '',
  request_form_datas: '',
  request_www_form_datas: '',
  requests_json_data: '',
  request_files: '',
  executor_code: ''
});

// 加载项目列表
const loadProjectList = () => {
  getProjectList({ page: 1, pageSize: 1000 }).then((res) => {
    if (res.data.code === 200) {
      projectList.value = res.data.data;
    }
  }).catch((error) => {
    console.error('加载项目列表失败:', error);
  });
};

// 加载执行器列表
const loadExecutors = async () => {
  try {
    const res = await listExecutors();
    if (res.data.code === 200) {
      executorList.value = res.data.data || [];
      if (!currentExecutorCode.value && executorList.value.length > 0) {
        currentExecutorCode.value = executorList.value[0].plugin_code;
      }
    }
  } catch (error) {
    console.error('加载执行器列表失败:', error);
  }
};

// 加载数据（编辑模式）
const loadData = (id) => {
  queryById(id).then((res) => {
    if (res.data.code === 200 && res.data.data) {
      const data = res.data.data;
      Object.keys(ruleForm).forEach(key => {
        if (data.hasOwnProperty(key)) {
          ruleForm[key] = data[key];
        }
      });
      
      // 恢复执行器选择
      if (data.executor_code) {
        currentExecutorCode.value = data.executor_code;
      }
      
      // 解析参数
      parseParams();
    } else {
      ElMessage.error('数据加载失败');
      goBack();
    }
  }).catch((error) => {
    console.error('数据加载失败:', error);
    ElMessage.error('数据加载失败，请稍后重试');
    goBack();
  });
};

// 解析参数
const parseParams = () => {
  try {
    // 解析URL参数 - 支持两种格式
    if (ruleForm.request_params) {
      const params = JSON.parse(ruleForm.request_params);
      if (Array.isArray(params)) {
        // 新格式: [{name, type, required, description, default}]
        urlParams.value = params.map(p => ({ 
          key: p.name, 
          value: String(p.default || ''), 
          description: p.description || `${p.type}${p.required ? ' (必填)' : ''}` 
        }));
      } else {
        // 旧格式: {key: value}
        urlParams.value = Object.entries(params).map(([key, value]) => ({ key, value: String(value), description: '' }));
      }
    }
    
    // 解析Header - 支持两种格式
    if (ruleForm.request_headers) {
      const headers = JSON.parse(ruleForm.request_headers);
      if (Array.isArray(headers)) {
        // 新格式: [{name, type, required, description, default}]
        headerParams.value = headers.map(h => ({ 
          key: h.name, 
          value: String(h.default || ''), 
          description: h.description || `${h.type}${h.required ? ' (必填)' : ''}` 
        }));
      } else {
        // 旧格式: {key: value}
        headerParams.value = Object.entries(headers).map(([key, value]) => ({ key, value: String(value), description: '' }));
      }
    }
    
    // 解析form-data - 支持两种格式
    if (ruleForm.request_form_datas) {
      const formDatas = JSON.parse(ruleForm.request_form_datas);
      if (Array.isArray(formDatas)) {
        // 新格式: [{name, type, required, description, default}]
        formDataParams.value = formDatas.map(f => ({ 
          key: f.name, 
          value: String(f.default || ''), 
          description: f.description || `${f.type}${f.required ? ' (必填)' : ''}` 
        }));
      } else {
        // 旧格式: {key: value}
        formDataParams.value = Object.entries(formDatas).map(([key, value]) => ({ key, value: String(value), description: '' }));
      }
      if (formDataParams.value.length > 0) bodyType.value = 'form-data';
    }
    
    // 解析www-form
    if (ruleForm.request_www_form_datas) {
      const wwwForms = JSON.parse(ruleForm.request_www_form_datas);
      wwwFormParams.value = Object.entries(wwwForms).map(([key, value]) => ({ key, value: String(value), description: '' }));
      if (wwwFormParams.value.length > 0) bodyType.value = 'x-www-form-urlencoded';
    }
    
    // 解析JSON Body
    if (ruleForm.requests_json_data) {
      jsonBody.value = typeof ruleForm.requests_json_data === 'string' 
        ? ruleForm.requests_json_data 
        : JSON.stringify(JSON.parse(ruleForm.requests_json_data), null, 2);
      if (jsonBody.value) bodyType.value = 'raw';
    }
    
    // 解析变量
    if (ruleForm.debug_vars) {
      const vars = JSON.parse(ruleForm.debug_vars);
      variableParams.value = Object.entries(vars).map(([key, value]) => ({ key, value: String(value), description: '' }));
    }
  } catch (error) {
    console.error('解析参数失败:', error);
  }
};

// 序列化参数
const serializeParams = () => {
  try {
    // 序列化URL参数
    if (urlParams.value.length > 0) {
      const params = {};
      urlParams.value.forEach(item => {
        if (item.key) params[item.key] = item.value || '';
      });
      ruleForm.request_params = JSON.stringify(params);
    }
    
    // 序列化Header
    if (headerParams.value.length > 0) {
      const headers = {};
      headerParams.value.forEach(item => {
        if (item.key) headers[item.key] = item.value || '';
      });
      ruleForm.request_headers = JSON.stringify(headers);
    }
    
    // 序列化form-data
    if (bodyType.value === 'form-data' && formDataParams.value.length > 0) {
      const formDatas = {};
      formDataParams.value.forEach(item => {
        if (item.key) formDatas[item.key] = item.value || '';
      });
      ruleForm.request_form_datas = JSON.stringify(formDatas);
    } else {
      ruleForm.request_form_datas = '';
    }
    
    // 序列化www-form
    if (bodyType.value === 'x-www-form-urlencoded' && wwwFormParams.value.length > 0) {
      const wwwForms = {};
      wwwFormParams.value.forEach(item => {
        if (item.key) wwwForms[item.key] = item.value || '';
      });
      ruleForm.request_www_form_datas = JSON.stringify(wwwForms);
    } else {
      ruleForm.request_www_form_datas = '';
    }
    
    // 序列化JSON Body
    if (bodyType.value === 'raw' && jsonBody.value) {
      ruleForm.requests_json_data = jsonBody.value;
    } else {
      ruleForm.requests_json_data = '';
    }
    
    // 序列化变量
    if (variableParams.value.length > 0) {
      const vars = {};
      variableParams.value.forEach(item => {
        if (item.key) vars[item.key] = item.value || '';
      });
      ruleForm.debug_vars = JSON.stringify(vars);
    }
    
    // 保存执行器选择
    ruleForm.executor_code = currentExecutorCode.value || '';
  } catch (error) {
    console.error('序列化参数失败:', error);
  }
};

// 添加URL参数
const addUrlParam = () => {
  urlParams.value.push({ key: '', value: '', description: '' });
};

// 删除URL参数
const removeUrlParam = (index) => {
  urlParams.value.splice(index, 1);
};

// 添加Header参数
const addHeaderParam = () => {
  headerParams.value.push({ key: '', value: '', description: '' });
};

// 删除Header参数
const removeHeaderParam = (index) => {
  headerParams.value.splice(index, 1);
};

// 添加form-data参数
const addFormDataParam = () => {
  formDataParams.value.push({ key: '', value: '', description: '' });
};

// 删除form-data参数
const removeFormDataParam = (index) => {
  formDataParams.value.splice(index, 1);
};

// 添加www-form参数
const addWwwFormParam = () => {
  wwwFormParams.value.push({ key: '', value: '', description: '' });
};

// 删除www-form参数
const removeWwwFormParam = (index) => {
  wwwFormParams.value.splice(index, 1);
};

// 添加变量
const addVariableParam = () => {
  variableParams.value.push({ key: '', value: '', description: '' });
};

// 删除变量
const removeVariableParam = (index) => {
  variableParams.value.splice(index, 1);
};

// ========== JSON处理方法 ==========

// 验证JSON格式
const validateJson = () => {
  if (!jsonBody.value.trim()) {
    jsonValidStatus.value = '';
    jsonError.value = '';
    return true;
  }
  
  try {
    JSON.parse(jsonBody.value);
    jsonValidStatus.value = 'valid';
    jsonError.value = '';
    ElMessage.success('JSON格式正确');
    return true;
  } catch (error) {
    jsonValidStatus.value = 'invalid';
    jsonError.value = error.message;
    return false;
  }
};

// 格式化JSON
const formatJson = () => {
  if (!jsonBody.value.trim()) {
    ElMessage.warning('请输入JSON内容');
    return;
  }
  
  try {
    const parsed = JSON.parse(jsonBody.value);
    jsonBody.value = JSON.stringify(parsed, null, 2);
    jsonValidStatus.value = 'valid';
    jsonError.value = '';
    ElMessage.success('格式化成功');
  } catch (error) {
    jsonValidStatus.value = 'invalid';
    jsonError.value = error.message;
    ElMessage.error('JSON格式错误，无法格式化');
  }
};

// 压缩JSON
const compressJson = () => {
  if (!jsonBody.value.trim()) {
    ElMessage.warning('请输入JSON内容');
    return;
  }
  
  try {
    const parsed = JSON.parse(jsonBody.value);
    jsonBody.value = JSON.stringify(parsed);
    jsonValidStatus.value = 'valid';
    jsonError.value = '';
    ElMessage.success('压缩成功');
  } catch (error) {
    jsonValidStatus.value = 'invalid';
    jsonError.value = error.message;
    ElMessage.error('JSON格式错误，无法压缩');
  }
};

// 清空JSON
const clearJson = () => {
  ElMessageBox.confirm('确定要清空JSON内容吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    jsonBody.value = '';
    jsonValidStatus.value = '';
    jsonError.value = '';
    ElMessage.success('已清空');
  }).catch(() => {});
};

// 提交表单
const submitForm = async () => {
  if (!ruleForm.api_name) {
    ElMessage.warning('请输入接口名称');
    return;
  }
  if (!ruleForm.request_url) {
    ElMessage.warning('请输入请求URL');
    return;
  }
  
  submitting.value = true;
  serializeParams();
  
  try {
    let res;
    if (isEdit.value) {
      res = await updateData(ruleForm);
    } else {
      const submitData = { ...ruleForm };
      delete submitData.id; // 新增时不需要id
      res = await insertData(submitData);
    }
      
    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
      if (!isEdit.value && res.data.data && res.data.data.id) {
        ruleForm.id = res.data.data.id;
        isEdit.value = true;
      }
    } else {
      ElMessage.error(res.data.msg || (isEdit.value ? '更新失败' : '创建失败'));
    }
  } catch (error) {
    console.error('保存失败:', error);
    ElMessage.error('保存失败，请稍后重试');
  } finally {
    submitting.value = false;
  }
};

// 生成接口测试用例YAML内容
const generateTestCaseYaml = () => {
  serializeParams();

  // 构建 body 对象（优先 JSON，其次 form-data / x-www-form-urlencoded）
  let body: any = null;
  try {
    if (ruleForm.requests_json_data) {
      // requests_json_data 存的就是 JSON 字符串
      body = JSON.parse(ruleForm.requests_json_data);
    } else if (ruleForm.request_form_datas) {
      body = JSON.parse(ruleForm.request_form_datas);
    } else if (ruleForm.request_www_form_datas) {
      body = JSON.parse(ruleForm.request_www_form_datas);
    }
  } catch (e) {
    // 如果解析失败，就原样作为字符串传给插件
    body = ruleForm.requests_json_data || ruleForm.request_form_datas || ruleForm.request_www_form_datas || null;
  }

  // 构建请求步骤参数（符合 api-engine 的 send_request 关键字格式）
  // send_request 内部使用 requests.Session().request(**kwargs)
  const stepParams: Record<string, any> = {
    '关键字': 'send_request',
    method: ruleForm.request_method || 'GET',
    url: (ruleForm.request_url || '').trim(),
  };

  // 添加请求头
  if (ruleForm.request_headers) {
    try {
      const headers = JSON.parse(ruleForm.request_headers);
      if (Object.keys(headers).length > 0) {
        stepParams.headers = headers;
      }
    } catch (e) {
      console.warn('解析请求头失败:', e);
    }
  }

  // 添加URL查询参数
  if (ruleForm.request_params) {
    try {
      const params = JSON.parse(ruleForm.request_params);
      if (Object.keys(params).length > 0) {
        stepParams.params = params;
      }
    } catch (e) {
      console.warn('解析查询参数失败:', e);
    }
  }

  // 添加请求体（根据类型选择 json 或 data）
  // requests 库：json 参数用于 JSON 数据，data 参数用于表单数据
  if (body !== null) {
    if (ruleForm.requests_json_data) {
      stepParams.json = body;
    } else {
      stepParams.data = body;
    }
  }

  // 构建测试用例结构（符合 api-engine 的 YAML 用例格式）
  const testCase = {
    desc: ruleForm.api_name || '接口调试',
    steps: [
      {
        ['发送请求']: stepParams
      }
    ]
  };

  // 目前后端 TaskScheduler + CommandExecutor 只是按“文本”写入临时 YAML 文件，
  // 这里先用 JSON 字符串，api_engine 内部会按 JSON/YAML 解析。
  return JSON.stringify(testCase, null, 2);
};

// 处理调试操作命令
const handleTestCommand = async (command: string) => {
  if (!ruleForm.api_name) {
    ElMessage.warning('请先输入接口名称');
    return;
  }
  if (!ruleForm.request_url) {
    ElMessage.warning('请先输入请求URL');
    return;
  }
  if (!currentExecutorCode.value) {
    ElMessage.warning('请选择执行器');
    return;
  }

  testing.value = true;
  activeTab.value = 'debug';
  debugOutput.value = '正在执行测试...';
  debugResult.value = null;
  
  try {
    // 生成测试用例YAML
    const testCaseContent = generateTestCaseYaml();
    
    // 调用执行器插件执行（同步等待结果）
    const res = await executeTask({
      plugin_code: currentExecutorCode.value,
      test_case_id: ruleForm.id ? parseInt(String(ruleForm.id)) : 0,
      test_case_content: testCaseContent,
      config: {}
    });
    
    if (res.data.code === 200) {
      const data = res.data.data;
      handleTaskResult(data);
      
    } else {
      ElMessage.error(res.data.msg || '执行失败');
      debugOutput.value = `执行失败: ${res.data.msg}`;
    }
  } catch (error) {
    console.error('调试操作失败:', error);
    ElMessage.error('操作失败，请稍后重试');
    debugOutput.value = `操作失败: ${error.message || error}`;
  } finally {
    testing.value = false;
  }
};

// 下载测试结果
const downloadTestResult = (result: any) => {
  try {
    // 构建下载内容
    const downloadData = {
      api_name: ruleForm.api_name,
      request_url: ruleForm.request_url,
      request_method: ruleForm.request_method,
      test_time: new Date().toISOString(),
      result: result
    };
    
    // 创建 Blob 并触发下载
    const jsonStr = JSON.stringify(downloadData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    // 生成文件名：接口名称_时间戳.json
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const safeName = (ruleForm.api_name || 'api_result').replace(/[\\/:*?"<>|]/g, '_');
    link.download = `${safeName}_${timestamp}.json`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    ElMessage.success('测试结果已下载');
  } catch (error) {
    console.error('下载失败:', error);
    ElMessage.error('下载失败');
  }
};


// 获取请求体显示内容
const getRequestBody = (request: any) => {
  if (!request) return '';
  if (request.json) return JSON.stringify(request.json, null, 2);
  if (request.data) {
    try {
      // 尝试解析JSON字符串
      if (typeof request.data === 'string' && (request.data.startsWith('{') || request.data.startsWith('['))) {
        return JSON.stringify(JSON.parse(request.data), null, 2);
      }
      return request.data;
    } catch (e) {
      return request.data;
    }
  }
  if (request.body) {
     if (typeof request.body === 'object') return JSON.stringify(request.body, null, 2);
     return request.body;
  }
  return '';
};

// 获取解析后的请求体对象（用于 JsonViewer）
const getParsedRequestBody = (request: any) => {
  if (!request) return {};
  if (request.json) return request.json;
  if (request.data) {
    try {
      if (typeof request.data === 'string' && (request.data.startsWith('{') || request.data.startsWith('['))) {
        return JSON.parse(request.data);
      }
      return { data: request.data };
    } catch (e) {
      return { data: request.data };
    }
  }
  if (request.body) {
    if (typeof request.body === 'object') return request.body;
    try {
      return JSON.parse(request.body);
    } catch (e) {
      return { body: request.body };
    }
  }
  return {};
};

// 生成请求预览数据（用于在未执行调试时显示）
const getRequestPreview = () => {
  // 获取请求头
  let headers: any = {};
  try {
    if (ruleForm.request_headers) {
      const parsed = JSON.parse(ruleForm.request_headers);
      if (Array.isArray(parsed)) {
        parsed.forEach(h => { if (h.name) headers[h.name] = h.default || ''; });
      } else {
        headers = parsed;
      }
    }
  } catch (e) {}
  // 添加默认 Content-Type
  if (!headers['Content-Type'] && (jsonBody.value || ruleForm.requests_json_data)) {
    headers['Content-Type'] = 'application/json';
  }

  // 获取请求体
  let body: any = null;
  try {
    if (jsonBody.value) {
      body = JSON.parse(jsonBody.value);
    } else if (ruleForm.requests_json_data) {
      body = JSON.parse(ruleForm.requests_json_data);
    } else if (ruleForm.request_form_datas) {
      body = JSON.parse(ruleForm.request_form_datas);
    } else if (ruleForm.request_www_form_datas) {
      body = JSON.parse(ruleForm.request_www_form_datas);
    }
  } catch (e) {}

  return {
    url: ruleForm.request_url || '',
    method: ruleForm.request_method || 'GET',
    headers: Object.keys(headers).length > 0 ? headers : null,
    body: body
  };
};

// 格式化测试结果为易读格式
const formatTestResult = (result: any): string => {
  const lines: string[] = [];
  const divider = '─'.repeat(50);
  
  // 标题
  const statusEmoji = result.status === 'completed' ? '✅' : '❌';
  const statusText = result.status === 'completed' ? '测试通过' : '测试失败';
  lines.push(`${statusEmoji} ${statusText}`);
  lines.push(divider);
  
  // 测试用例结果
  if (result.test_cases && result.test_cases.length > 0) {
    lines.push('');
    lines.push('【测试用例】');
    result.test_cases.forEach((tc: any, index: number) => {
      const icon = tc.status === 'PASSED' ? '✓' : '✗';
      const statusClass = tc.status === 'PASSED' ? '通过' : '失败';
      lines.push(`  ${index + 1}. ${tc.name} → ${statusClass}`);
    });
  }
  
  // 统计摘要
  if (result.summary) {
    lines.push('');
    lines.push('【执行统计】');
    lines.push(`  总数: ${result.summary.total}  |  通过: ${result.summary.passed}  |  失败: ${result.summary.failed}`);
    if (result.summary.duration) {
      const duration = result.summary.duration.replace(/\d+ passed in /, '');
      lines.push(`  耗时: ${duration}`);
    }
  }
  
  // 请求信息
  if (result.request && result.request.url) {
    lines.push('');
    lines.push('【请求详情】');
    lines.push(`  ${result.request.method} ${result.request.url}`);
    if (result.request.body && Object.keys(result.request.body).length > 0) {
      lines.push(`  请求体: ${JSON.stringify(result.request.body)}`);
    }
  }
  
  // 响应信息
  if (result.response && result.response.body) {
    lines.push('');
    lines.push('【响应结果】');
    const respBody = result.response.body;
    if (respBody.code !== undefined) {
      const codeIcon = respBody.code === 200 ? '✓' : '✗';
      lines.push(`  ${codeIcon} 状态码: ${respBody.code}`);
    }
    if (respBody.msg) {
      lines.push(`  消息: ${respBody.msg}`);
    }
    if (respBody.data) {
      // 只显示关键字段
      const keyFields = ['id', 'username', 'email', 'mobile', 'status', 'code', 'msg'];
      const summary: string[] = [];
      for (const key of keyFields) {
        if (respBody.data[key] !== undefined) {
          summary.push(`${key}: ${respBody.data[key]}`);
        }
      }
      if (summary.length > 0) {
        lines.push(`  关键数据: { ${summary.join(', ')} }`);
      }
      // 完整数据显示
      lines.push('');
      lines.push('【完整响应数据】');
      lines.push(JSON.stringify(respBody.data, null, 2));
    }
  }
  
  // 错误信息
  if (result.error) {
    lines.push('');
    lines.push('【错误信息】');
    lines.push(`  ${result.error}`);
  }
  
  return lines.join('\n');
};

// 处理任务结果
const handleTaskResult = (data: any) => {
  const result = data.result || data;
  const status = result.status;
  
  if (status === 'completed') {
    ElMessage.success('测试执行成功');
  } else if (status === 'failed') {
    ElMessage.warning('测试执行完成，但存在失败');
  } else if (status === 'timeout') {
    ElMessage.warning('测试执行超时');
  }
  
  // 使用格式化函数展示结果
  debugOutput.value = formatTestResult(result);
  debugResult.value = result;
  activeTab.value = 'debug';
  testing.value = false;
};

// 加入测试用例管理
const addToTestCase = async () => {
  if (!ruleForm.api_name) {
    ElMessage.warning('请先输入接口名称');
    return;
  }
  if (!ruleForm.request_url) {
    ElMessage.warning('请先输入请求URL');
    return;
  }
  
  addingCase.value = true;

  try {
    // 1. 获取操作类型ID (HTTP请求)
    let operationTypeId = 1; // 默认为1
    try {
      const opRes = await queryOperationTypes();
      if (opRes.data.code === 200 && Array.isArray(opRes.data.data)) {
        const op = opRes.data.data.find((item: any) => item.operation_type_name === 'HTTP请求');
        if (op) operationTypeId = op.id;
      }
    } catch (e) {
      console.warn('查询操作类型失败，使用默认ID=1', e);
    }

    // 2. 获取关键字列表并匹配ID
    let keywordId = null;
    const method = ruleForm.request_method || 'GET';
    
    // 判断Body类型
    const hasJsonBody = !!ruleForm.requests_json_data;
    const hasFormBody = !!ruleForm.request_form_datas || !!ruleForm.request_www_form_datas;
    
    let targetName = 'GET请求';
    if (method === 'GET') targetName = 'GET请求';
    else if (method === 'POST') {
      if (hasJsonBody) targetName = 'POST请求(JSON)';
      else if (hasFormBody) targetName = 'POST请求(表单)';
      else targetName = 'POST请求(JSON)';
    }
    else if (method === 'PUT') targetName = 'PUT请求';
    else if (method === 'DELETE') targetName = 'DELETE请求';
    else if (method === 'PATCH') targetName = 'PATCH请求';

    try {
      const kwRes = await queryKeywordsByType(operationTypeId);
      if (kwRes.data.code === 200 && Array.isArray(kwRes.data.data)) {
        const keywords = kwRes.data.data;
        const kw = keywords.find((item: any) => item.name === targetName);
        if (kw) {
          keywordId = kw.id;
        } else {
          // 降级：如果找不到精确匹配，尝试找包含 method 的
          const fuzzy = keywords.find((item: any) => item.name.includes(method));
          if (fuzzy) keywordId = fuzzy.id;
        }
      }
    } catch (e) {
      console.warn('查询关键字列表失败，将尝试使用默认ID', e);
    }
    
    // 3. 兜底策略：如果动态查找失败，使用标准初始化数据的ID
    if (!keywordId) {
      console.warn(`未动态匹配到关键字 '${targetName}'，使用默认ID兜底`);
      if (method === 'GET') keywordId = 1;
      else if (method === 'POST') {
        if (targetName.includes('表单')) keywordId = 3;
        else keywordId = 2;
      }
      else if (method === 'PUT') keywordId = 5;
      else if (method === 'DELETE') keywordId = 6;
      else if (method === 'PATCH') keywordId = 7;
      else keywordId = 1; // 实在不行就GET
    }
    
    if (!keywordId) {
      ElMessage.warning('未找到对应的关键字定义，请检查关键字配置');
      return;
    }

    // 先序列化当前参数
    serializeParams();
  
    // 重新确定 stepDesc (为了保持一致性)
    let stepDesc = `${method}请求`;
    
    if (method === 'GET') stepDesc = 'GET请求';
    else if (method === 'POST') {
        if (hasJsonBody) stepDesc = 'POST请求(JSON)';
        else if (hasFormBody) stepDesc = 'POST请求(表单)';
        else stepDesc = 'POST请求(JSON)';
    }
    else if (method === 'PUT') stepDesc = 'PUT请求';
    else if (method === 'DELETE') stepDesc = 'DELETE请求';
    else if (method === 'PATCH') stepDesc = 'PATCH请求';
    
    // 构建步骤数据（符合关键字参数格式）
    const stepData: Record<string, any> = {
      URL: ruleForm.request_url.trim(),
    };
    
    // 添加请求头
    if (ruleForm.request_headers) {
      try {
        const headers = JSON.parse(ruleForm.request_headers);
        if (Object.keys(headers).length > 0) {
          stepData.HEADERS = headers;
        }
      } catch (e) {
        console.warn('解析请求头失败:', e);
      }
    }
    
    // 添加URL查询参数
    if (ruleForm.request_params) {
      try {
        const params = JSON.parse(ruleForm.request_params);
        if (Object.keys(params).length > 0) {
          stepData.PARAMS = params;
        }
      } catch (e) {
        console.warn('解析查询参数失败:', e);
      }
    }
    
    // 添加请求体（DATA字段）
    if (ruleForm.requests_json_data) {
      try {
        stepData.DATA = JSON.parse(ruleForm.requests_json_data);
      } catch (e) {
        stepData.DATA = ruleForm.requests_json_data;
      }
    } else if (ruleForm.request_form_datas) {
      try {
        stepData.DATA = JSON.parse(ruleForm.request_form_datas);
      } catch (e) {
        stepData.DATA = ruleForm.request_form_datas;
      }
    } else if (ruleForm.request_www_form_datas) {
      try {
        stepData.DATA = JSON.parse(ruleForm.request_www_form_datas);
      } catch (e) {
        stepData.DATA = ruleForm.request_www_form_datas;
      }
    }
    
    // 构建测试用例数据
    const caseData: any = {
      project_id: ruleForm.project_id || null,
      case_name: ruleForm.api_name,
      case_desc: `接口调试自动生成: ${method} ${ruleForm.request_url}`,
      steps: [
        {
          run_order: 1,
          step_desc: stepDesc,
          operation_type_id: operationTypeId,
          keyword_id: keywordId,
          step_data: stepData
        }
      ]
    };
    
    // 1. 先查询是否存在同名用例
    let existingCaseId = null;
    try {
      const queryRes = await queryCaseList({
        page: 1,
        pageSize: 10,
        case_name: ruleForm.api_name,
        project_id: ruleForm.project_id || undefined
      });
      
      if (queryRes.data.code === 200 && queryRes.data.data && queryRes.data.data.length > 0) {
        // 精确匹配名称
        const exist = queryRes.data.data.find((item: any) => item.case_name === ruleForm.api_name);
        if (exist) {
          existingCaseId = exist.id;
        }
      }
    } catch (e) {
      console.warn('查询已存在用例失败:', e);
    }

    let res;
    if (existingCaseId) {
      // 2. 如果存在，询问是否覆盖
      try {
        await ElMessageBox.confirm(
          `检测到已存在名称为 "${ruleForm.api_name}" 的用例，是否覆盖更新？`,
          '用例已存在',
          {
            confirmButtonText: '覆盖更新',
            cancelButtonText: '创建新用例', // 用户也可以选择创建新的（如果后端允许重名的话，或者改名）- 这里逻辑改为取消就是不覆盖，直接新增可能导致重名，不如直接覆盖或者取消
            // 实际上用户可能想创建重复的，但这里为了方便覆盖，我们把 Cancel 当作 "不覆盖，作为新用例插入" 还是 "取消操作"？
            // 通常 Cancel 是取消操作。但这里为了灵活性，可以设为 DistinguishCancelAndClose
            distinguishCancelAndClose: true,
            confirmButtonClass: 'el-button--warning',
            type: 'warning'
          }
        );
        
        // 用户确认覆盖
        caseData.id = existingCaseId;
        res = await updateCaseData(caseData);
        
      } catch (action) {
        if (action === 'cancel') {
          // 用户点击"创建新用例" (对应 cancelButtonText)
          res = await insertCaseData(caseData);
        } else {
          // 用户点击关闭或按ESC
          addingCase.value = false;
          return;
        }
      }
    } else {
      // 3. 不存在，直接新增
      res = await insertCaseData(caseData);
    }

    if (res.data.code === 200) {
      ElMessage.success(existingCaseId && caseData.id ? '用例已覆盖更新' : '已成功加入测试用例管理');
      // 询问是否跳转到用例管理页面
      ElMessageBox.confirm(
        '是否立即跳转到测试用例管理页面？',
        '操作成功',
        {
          confirmButtonText: '立即跳转',
          cancelButtonText: '留在当前页',
          type: 'success'
        }
      ).then(() => {
        router.push('/ApiInfoCaseList');
      }).catch(() => {
        // 用户选择留在当前页
      });
    } else {
      ElMessage.error(res.data.msg || '操作失败');
    }
  } catch (error) {
    console.error('加入测试用例失败:', error);
    ElMessage.error('操作失败，请稍后重试');
  } finally {
    addingCase.value = false;
  }
};

// 返回列表页
const goBack = () => {
  router.push('/ApiInfoList');
};

// 页面加载时执行
onMounted(() => {
  loadProjectList();
  loadExecutors();
  
  // 检查是否为编辑模式
  const id = route.query.id;
  if (id) {
    isEdit.value = true;
    const idStr = Array.isArray(id) ? id[0] : id;
    loadData(parseInt(idStr));
  }
  // 新增模式已经在初始化时设置了默认空数据
});
</script>

<style scoped>
@import '~/styles/common-list.css';
@import '~/styles/common-form.css';

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-left .subtitle {
  color: #909399;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* 表单区块 */
.form-section {
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

/* 表单内容区 */
.form-content,
.api-config-content {
  padding: 16px;
  background: white;
  border-radius: 4px;
}

/* 请求行 */
.request-line {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.method-select {
  width: 140px;
  flex-shrink: 0;
}

.url-input {
  flex: 1;
}

/* 标签页 */
.params-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }
  
  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
  }
}

/* 表格样式 */
:deep(.el-table) {
  font-size: 14px;
  
  th {
    background: #f5f7fa;
    font-weight: 600;
  }
  
  .el-input__inner {
    border: 1px solid #dcdfe6;
    padding: 5px 10px;
  }
  
  .el-input__inner:focus {
    border-color: #409eff;
  }
}

/* 表单项样式 */
:deep(.el-form-item__label) {
  color: #606266;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

/* 禁用输入框样式 */
:deep(.el-input.is-disabled .el-input__inner) {
  background-color: #f5f7fa;
  color: #909399;
}

/* ========== JSON编辑器样式 ========== */
.json-editor-container {
  width: 100%;
}

.json-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border: 1px solid #dcdfe6;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
  margin-bottom: 0;
}

.json-toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.json-label {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}

.json-toolbar-right {
  display: flex;
  gap: 8px;
}

.json-toolbar-right .el-button {
  padding: 5px 15px;
  font-size: 13px;
}

.json-editor {
  border-radius: 0 0 4px 4px;
}

.json-editor :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  border-radius: 0 0 4px 4px;
  border-top: none;
  background-color: #fafafa;
  color: #2c3e50;
  padding: 12px;
  resize: vertical;
  min-height: 300px;
}

.json-editor :deep(.el-textarea__inner:focus) {
  background-color: #ffffff;
  border-color: #409eff;
}

.json-editor :deep(.el-textarea__inner::placeholder) {
  color: #a8abb2;
  font-style: italic;
}

.json-error {
  margin-top: 12px;
}

.json-error :deep(.el-alert) {
  padding: 12px 16px;
}

.json-error :deep(.el-alert__title) {
  font-size: 13px;
  line-height: 1.5;
  word-break: break-all;
}

/* 调试结果样式 */
.debug-result-wrapper {
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.debug-status-bar {
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
}

.debug-status-bar.success {
  background-color: #f0f9eb;
  color: #67c23a;
  border-bottom-color: #e1f3d8;
}

.debug-status-bar.failed {
  background-color: #fef0f0;
  color: #f56c6c;
  border-bottom-color: #fde2e2;
}

.debug-status-bar.preview {
  background-color: #ecf5ff;
  color: #409eff;
  border-bottom-color: #d9ecff;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.separator {
  color: #dcdfe6;
}

.debug-detail {
  padding: 20px;
}

.detail-row {
  display: flex;
  margin-bottom: 16px;
  font-size: 14px;
}

.detail-label {
  width: 80px;
  font-weight: 600;
  color: #606266;
  flex-shrink: 0;
}

.detail-value {
  color: #303133;
  word-break: break-all;
}

.detail-block {
  margin-bottom: 20px;
}

.detail-block .detail-label {
  margin-bottom: 8px;
  width: auto;
}

.code-box {
  background-color: #fafafa;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 12px;
  max-height: 400px;
  overflow: auto;
}

.code-box pre {
  margin: 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.text-danger {
  color: #f56c6c;
}

.error-box {
  background-color: #fef0f0;
  border-color: #fde2e2;
  color: #f56c6c;
}

.error-box pre {
  color: #f56c6c;
}

/* 空状态样式 */
.debug-empty-state {
  height: 400px;
  background-color: #fafafa;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #909399;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-text {
  font-size: 14px;
  margin: 0;
}

.preview-hint {
  padding: 20px;
  text-align: center;
}
</style>
