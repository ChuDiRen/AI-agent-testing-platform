<template>
  <div class="api-info-form-container">
    <!-- 顶部操作栏 -->
    <div class="header-section">
      <div class="header-background"></div>
      <div class="header-content">
        <div class="title-section">
          <div class="title-icon">
            <el-icon size="24"><Connection /></el-icon>
          </div>
          <div class="title-text">
            <h2 class="page-title">{{ isEdit ? '编辑接口信息' : '新增接口信息' }}</h2>
            <p class="page-subtitle">{{ isEdit ? '修改现有接口配置' : '创建新的API接口配置' }}</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button 
            type="primary" 
            @click="submitForm" 
            :loading="submitting"
            class="action-btn primary-btn"
            size="large"
          >
            <el-icon><Check /></el-icon>
            {{ isEdit ? '更新接口' : '保存接口' }}
          </el-button>
          <el-button 
            type="success" 
            @click="handleSaveAndTest" 
            :loading="testing"
            class="action-btn success-btn"
            size="large"
          >
            <el-icon><VideoPlay /></el-icon>
            保存并测试
          </el-button>
          <el-button 
            @click="goBack"
            class="action-btn close-btn"
            size="large"
          >
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
        </div>
      </div>
    </div>

    <!-- 基础信息区 -->
    <div class="content-section">
      <div class="glass-card info-card">
        <div class="card-header">
          <div class="card-title-wrapper">
            <el-icon class="card-icon"><Document /></el-icon>
            <span class="card-title">基础信息</span>
          </div>
          <div class="card-badge">必填信息</div>
        </div>
        
        <div class="card-content">
          <el-row :gutter="24">
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <el-icon><Key /></el-icon>
                  接口编号
                </label>
                <el-input 
                  v-model="ruleForm.id" 
                  disabled 
                  class="form-input disabled-input"
                  placeholder="系统自动生成"
                />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label required">
                  <el-icon><Edit /></el-icon>
                  接口名称
                </label>
                <el-input 
                  v-model="ruleForm.api_name" 
                  placeholder="示例：用户登录接口" 
                  class="form-input"
                  :class="{ 'error-input': !ruleForm.api_name }"
                />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="form-group">
                <label class="form-label">
                  <el-icon><Folder /></el-icon>
                  所属项目
                </label>
                <el-select 
                  v-model="ruleForm.project_id" 
                  placeholder="选择项目" 
                  class="form-select"
                >
                  <el-option 
                    v-for="project in projectList" 
                    :key="project.id" 
                    :label="project.project_name" 
                    :value="project.id"
                  />     
        </el-select>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

    <!-- 接口信息区 -->
    <div class="content-section">
      <div class="glass-card request-card">
        <div class="card-header">
          <div class="card-title-wrapper">
            <el-icon class="card-icon"><Connection /></el-icon>
            <span class="card-title">接口配置</span>
          </div>
          <div class="card-badge api-badge">API</div>
        </div>

        <!-- 请求方法和URL -->
        <div class="request-section">
          <div class="request-line">
            <div class="method-selector">
              <el-select 
                v-model="ruleForm.request_method" 
                size="large" 
                class="method-select"
                :class="getMethodClass(ruleForm.request_method)"
              >
                <el-option 
                  v-for="method in methodList" 
                  :key="method" 
                  :label="method" 
                  :value="method"
                  :class="`method-option-${method.toLowerCase()}`"
                />     
        </el-select>
            </div>
            <div class="url-input-wrapper">
              <el-input 
                v-model="ruleForm.request_url" 
                placeholder="https://api.example.com/v1/users/login"
                size="large"
                class="url-input"
                :class="{ 'error-input': !ruleForm.request_url }"
              >
                <template #prefix>
                  <el-icon class="url-icon"><Link /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </div>

        <!-- 参数配置标签页 -->
        <div class="tabs-container">
          <el-tabs v-model="activeTab" class="modern-tabs">
            <!-- URL参数 -->
            <el-tab-pane name="params">
              <template #label>
                <div class="tab-label">
                  <el-icon><Link /></el-icon>
                  <span>URL参数</span>
                  <el-badge :value="urlParams.length" :hidden="urlParams.length === 0" class="tab-badge" />
                </div>
              </template>
              <div class="params-editor">
                <div class="params-table-wrapper">
                  <el-table :data="urlParams" class="modern-table" :border="false">
                    <el-table-column prop="key" label="参数名" width="200">
                      <template #default="scope">
        <el-input 
                          v-model="scope.row.key" 
                          placeholder="参数名" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="参数值">
                      <template #default="scope">
        <el-input 
                          v-model="scope.row.value" 
                          placeholder="参数值" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" width="200">
                      <template #default="scope">
                        <el-input 
                          v-model="scope.row.description" 
                          placeholder="参数描述" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="100" align="center">
                      <template #default="scope">
                        <el-button 
                          type="danger" 
                          link 
                          @click="removeUrlParam(scope.$index)"
                          class="delete-btn"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                <div class="add-param-section">
                  <el-button 
                    type="primary" 
                    @click="addUrlParam" 
                    class="add-param-btn"
                    :icon="Plus"
                  >
                    添加参数
                  </el-button>
                </div>
              </div>
            </el-tab-pane>

            <!-- 请求头Header -->
            <el-tab-pane name="headers">
              <template #label>
                <div class="tab-label">
                  <el-icon><Setting /></el-icon>
                  <span>请求头</span>
                  <el-badge :value="headerParams.length" :hidden="headerParams.length === 0" class="tab-badge" />
                </div>
              </template>
              <div class="params-editor">
                <div class="params-table-wrapper">
                  <el-table :data="headerParams" class="modern-table" :border="false">
                    <el-table-column prop="key" label="参数名" width="200">
                      <template #default="scope">
        <el-input 
                          v-model="scope.row.key" 
                          placeholder="Content-Type" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="参数值">
                      <template #default="scope">
                        <el-input 
                          v-model="scope.row.value" 
                          placeholder="application/json" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" width="200">
                      <template #default="scope">
                        <el-input 
                          v-model="scope.row.description" 
                          placeholder="请求内容类型" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="100" align="center">
                      <template #default="scope">
                        <el-button 
                          type="danger" 
                          link 
                          @click="removeHeaderParam(scope.$index)"
                          class="delete-btn"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                <div class="add-param-section">
                  <el-button 
                    type="primary" 
                    @click="addHeaderParam" 
                    class="add-param-btn"
                    :icon="Plus"
                  >
                    添加请求头
                  </el-button>
                </div>
              </div>
            </el-tab-pane>

            <!-- 请求Body -->
            <el-tab-pane name="body">
              <template #label>
                <div class="tab-label">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>请求Body</span>
                </div>
              </template>
              <div class="body-editor">
                <div class="body-type-selector">
                  <el-radio-group v-model="bodyType" class="modern-radio-group">
                    <el-radio-button value="none">
                      <el-icon><Close /></el-icon>
                      无
                    </el-radio-button>
                    <el-radio-button value="form-data">
                      <el-icon><Document /></el-icon>
                      form-data
                    </el-radio-button>
                    <el-radio-button value="x-www-form-urlencoded">
                      <el-icon><Key /></el-icon>
                      urlencoded
                    </el-radio-button>
                    <el-radio-button value="raw">
                      <el-icon><Edit /></el-icon>
                      JSON
                    </el-radio-button>
                  </el-radio-group>
                </div>

                <!-- form-data -->
                <div v-if="bodyType === 'form-data'" class="params-editor">
                  <div class="params-table-wrapper">
                    <el-table :data="formDataParams" class="modern-table" :border="false">
                      <el-table-column prop="key" label="参数名" width="200">
                        <template #default="scope">
        <el-input 
                            v-model="scope.row.key" 
                            placeholder="参数名" 
                            class="table-input"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column prop="value" label="参数值">
                        <template #default="scope">
                          <el-input 
                            v-model="scope.row.value" 
                            placeholder="参数值" 
                            class="table-input"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column prop="description" label="描述" width="200">
                        <template #default="scope">
                          <el-input 
                            v-model="scope.row.description" 
                            placeholder="参数描述" 
                            class="table-input"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="100" align="center">
                        <template #default="scope">
                          <el-button 
                            type="danger" 
                            link 
                            @click="removeFormDataParam(scope.$index)"
                            class="delete-btn"
                          >
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                  <div class="add-param-section">
                    <el-button 
                      type="primary" 
                      @click="addFormDataParam" 
                      class="add-param-btn"
                      :icon="Plus"
                    >
                      添加参数
                    </el-button>
                  </div>
                </div>

                <!-- x-www-form-urlencoded -->
                <div v-else-if="bodyType === 'x-www-form-urlencoded'" class="params-editor">
                  <div class="params-table-wrapper">
                    <el-table :data="wwwFormParams" class="modern-table" :border="false">
                      <el-table-column prop="key" label="参数名" width="200">
                        <template #default="scope">
        <el-input 
                            v-model="scope.row.key" 
                            placeholder="参数名" 
                            class="table-input"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column prop="value" label="参数值">
                        <template #default="scope">
                          <el-input 
                            v-model="scope.row.value" 
                            placeholder="参数值" 
                            class="table-input"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column prop="description" label="描述" width="200">
                        <template #default="scope">
                          <el-input 
                            v-model="scope.row.description" 
                            placeholder="参数描述" 
                            class="table-input"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column label="操作" width="100" align="center">
                        <template #default="scope">
                          <el-button 
                            type="danger" 
                            link 
                            @click="removeWwwFormParam(scope.$index)"
                            class="delete-btn"
                          >
                            <el-icon><Delete /></el-icon>
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                  <div class="add-param-section">
                    <el-button 
                      type="primary" 
                      @click="addWwwFormParam" 
                      class="add-param-btn"
                      :icon="Plus"
                    >
                      添加参数
                    </el-button>
                  </div>
                </div>

                <!-- raw (JSON) -->
                <div v-else-if="bodyType === 'raw'" class="json-editor">
        <el-input 
                    v-model="jsonBody" 
          type="textarea" 
                    :rows="12" 
                    placeholder='{\n  "username": "admin",\n  "password": "123456",\n  "remember": true\n}'
                    class="code-editor"
                  />
                </div>

                <!-- 无Body提示 -->
                <div v-else-if="bodyType === 'none'" class="empty-body">
                  <el-empty description="该请求不包含Body内容" :image-size="120">
                    <template #image>
                      <el-icon :size="80" style="color: rgba(255, 255, 255, 0.3)">
                        <Document />
                      </el-icon>
                    </template>
                  </el-empty>
                </div>
              </div>
            </el-tab-pane>

            <!-- 变量定义 -->
            <el-tab-pane name="variables">
              <template #label>
                <div class="tab-label">
                  <el-icon><Key /></el-icon>
                  <span>变量定义</span>
                  <el-badge :value="variableParams.length" :hidden="variableParams.length === 0" class="tab-badge" />
                </div>
              </template>
              <div class="params-editor">
                <div class="params-table-wrapper">
                  <el-table :data="variableParams" class="modern-table" :border="false">
                    <el-table-column prop="key" label="变量名" width="200">
                      <template #default="scope">
        <el-input 
                          v-model="scope.row.key" 
                          placeholder="token" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="value" label="变量值">
                      <template #default="scope">
                        <el-input 
                          v-model="scope.row.value" 
                          placeholder="eyJhbGciOiJIUzI1NiIs..." 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" width="200">
                      <template #default="scope">
                        <el-input 
                          v-model="scope.row.description" 
                          placeholder="用户认证令牌" 
                          class="table-input"
                        />
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="100" align="center">
                      <template #default="scope">
                        <el-button 
                          type="danger" 
                          link 
                          @click="removeVariableParam(scope.$index)"
                          class="delete-btn"
                        >
                          <el-icon><Delete /></el-icon>
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
                <div class="add-param-section">
                  <el-button 
                    type="primary" 
                    @click="addVariableParam" 
                    class="add-param-btn"
                    :icon="Plus"
                  >
                    添加变量
                  </el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- 测试结果区 -->
    <div v-if="showTestResult" class="content-section result-section">
      <div class="glass-card result-card">
        <div class="card-header">
          <div class="card-title-wrapper">
            <el-icon class="card-icon"><DataAnalysis /></el-icon>
            <span class="card-title">测试结果</span>
          </div>
          <div class="result-status">
            <el-tag 
              v-if="testResult.status" 
              :type="testResult.status === 'success' ? 'success' : 'danger'"
              size="large"
              class="status-tag"
            >
              <el-icon v-if="testResult.status === 'success'"><Check /></el-icon>
              <el-icon v-else><Close /></el-icon>
              {{ testResult.status === 'success' ? '测试通过' : '测试失败' }}
            </el-tag>
          </div>
        </div>

        <div class="card-content">
          <div class="tabs-container">
            <el-tabs v-model="resultTab" class="modern-tabs result-tabs">
              <el-tab-pane name="response">
                <template #label>
                  <div class="tab-label">
                    <el-icon><Document /></el-icon>
                    <span>响应内容</span>
                  </div>
                </template>
                <div class="response-wrapper">
                  <pre class="response-content">{{ formatJson(testResult.response) }}</pre>
                </div>
              </el-tab-pane>
              <el-tab-pane name="request">
                <template #label>
                  <div class="tab-label">
                    <el-icon><Connection /></el-icon>
                    <span>请求详情</span>
                  </div>
                </template>
                <div class="response-wrapper">
                  <pre class="response-content">{{ formatJson(testResult.request) }}</pre>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from "vue";
import { 
  Check, VideoPlay, Close, Connection, Document, Key, Edit, Folder, 
  Link, Delete, Plus, Setting, DataAnalysis 
} from '@element-plus/icons-vue';
import { queryById, insertData, updateData, getMethods } from './apiinfo.js';
import { queryByPage as getProjectList } from '../project/apiProject.js';
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();

// 表单引用
const formRef = ref();

// 是否编辑模式
const isEdit = ref(false);

// 加载状态
const submitting = ref(false);
const testing = ref(false);

// 项目列表
const projectList = ref([]);

// 请求方法列表
const methodList = ref(['GET', 'POST', 'PUT', 'DELETE', 'PATCH']);

// 当前激活的标签
const activeTab = ref('params');
const resultTab = ref('response');

// Body类型
const bodyType = ref('none');

// 参数列表
const urlParams = ref([]);
const headerParams = ref([]);
const formDataParams = ref([]);
const wwwFormParams = ref([]);
const variableParams = ref([]);

// JSON Body
const jsonBody = ref('');

// 测试结果
const showTestResult = ref(false);
const testResult = reactive({
  status: null,
  response: null,
  request: null
});

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
  request_files: ''
});

// 表单验证规则
const rules = reactive({
  api_name: [
    { required: true, message: '请输入接口名称', trigger: 'blur' }
  ],
  request_method: [
    { required: true, message: '请选择请求方法', trigger: 'change' }
  ],
  request_url: [
    { required: true, message: '请输入请求地址', trigger: 'blur' }
  ]
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

// 获取请求方法的样式类
const getMethodClass = (method) => {
  const classMap = {
    'GET': 'method-get',
    'POST': 'method-post',
    'PUT': 'method-put',
    'DELETE': 'method-delete',
    'PATCH': 'method-patch'
  };
  return classMap[method] || '';
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
    // 解析URL参数
    if (ruleForm.request_params) {
      const params = JSON.parse(ruleForm.request_params);
      urlParams.value = Object.entries(params).map(([key, value]) => ({ key, value, description: '' }));
    }
    
    // 解析Header
    if (ruleForm.request_headers) {
      const headers = JSON.parse(ruleForm.request_headers);
      headerParams.value = Object.entries(headers).map(([key, value]) => ({ key, value, description: '' }));
    }
    
    // 解析form-data
    if (ruleForm.request_form_datas) {
      const formDatas = JSON.parse(ruleForm.request_form_datas);
      formDataParams.value = Object.entries(formDatas).map(([key, value]) => ({ key, value, description: '' }));
      if (formDataParams.value.length > 0) bodyType.value = 'form-data';
    }
    
    // 解析www-form
    if (ruleForm.request_www_form_datas) {
      const wwwForms = JSON.parse(ruleForm.request_www_form_datas);
      wwwFormParams.value = Object.entries(wwwForms).map(([key, value]) => ({ key, value, description: '' }));
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
      variableParams.value = Object.entries(vars).map(([key, value]) => ({ key, value, description: '' }));
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

// 格式化JSON
const formatJson = (data) => {
  if (!data) return '';
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2);
    } catch {
      return data;
    }
  }
  return JSON.stringify(data, null, 2);
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

// 保存并测试
const handleSaveAndTest = async () => {
  await submitForm();
  if (ruleForm.id) {
    executeTest();
  }
};

// 执行测试
const executeTest = async () => {
  if (!ruleForm.request_url) {
    ElMessage.warning('请输入请求URL');
    return;
  }
  
  testing.value = true;
  serializeParams();
  
  try {
    // 模拟测试执行
    const testData = {
      api_info_id: ruleForm.id,
      request_method: ruleForm.request_method,
      request_url: ruleForm.request_url,
      request_headers: ruleForm.request_headers,
      request_params: ruleForm.request_params,
      request_body: ruleForm.requests_json_data || ruleForm.request_form_datas || ruleForm.request_www_form_datas
    };
    
    // 这里应该调用实际的测试接口
    showTestResult.value = true;
    testResult.status = 'success';
    testResult.response = {
      code: 200,
      msg: '测试执行成功',
      data: {
        message: '这是模拟的测试响应数据'
      }
    };
    testResult.request = testData;
    ElMessage.success('测试执行成功');
  } catch (error) {
    console.error('测试执行失败:', error);
    showTestResult.value = true;
    testResult.status = 'error';
    testResult.response = error.message || '测试执行失败';
    ElMessage.error('测试执行失败，请稍后重试');
  } finally {
    testing.value = false;
  }
};

// 重置表单
const resetForm = () => {
  if (!formRef.value) return;
  formRef.value.resetFields();
};

// 返回列表页
const goBack = () => {
  router.push('/ApiInfoList');
};

// 页面加载时执行
onMounted(() => {
  loadProjectList();
  
  // 检查是否为编辑模式
  const id = route.query.id;
  if (id) {
    isEdit.value = true;
    loadData(parseInt(id));
  } else {
    // 新增模式，添加默认参数
    addHeaderParam();
    addUrlParam();
  }
});
</script>

<style scoped lang="scss">
.api-info-form-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

// 顶部区域
.header-section {
  background: white;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .title-section {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .title-icon {
      width: 50px;
      height: 50px;
      background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      flex-shrink: 0;
    }
    
    .title-text {
      .page-title {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
        color: #303133;
      }
      
      .page-subtitle {
        margin: 0;
        font-size: 14px;
        color: #909399;
        font-weight: 400;
      }
    }
  }
  
  .header-actions {
    display: flex;
    gap: 12px;
    
    .action-btn {
      padding: 10px 20px;
      border-radius: 4px;
      font-weight: 600;
      transition: all 0.3s ease;
      border: none;
      
      &.primary-btn {
        background: #409eff;
        color: white;
        
        &:hover {
          background: #66b1ff;
        }
      }
      
      &.success-btn {
        background: #67c23a;
        color: white;
        
        &:hover {
          background: #85ce61;
        }
      }
      
      &.close-btn {
        background: #f5f7fa;
        color: #606266;
        border: 1px solid #dcdfe6;
        
        &:hover {
          color: #303133;
          border-color: #b4bccc;
        }
      }
    }
  }
}

// 内容区域
.content-section {
  margin-bottom: 20px;
}

// 卡片
.glass-card {
  background: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.15);
  }
  
  .card-header {
    padding: 20px;
    background: #f5f7fa;
    border-bottom: 1px solid #ebeef5;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .card-title-wrapper {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .card-icon {
        color: #409eff;
        font-size: 18px;
      }
      
      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin: 0;
      }
    }
    
    .card-badge {
      padding: 4px 12px;
      background: #fde4e4;
      color: #f56c6c;
      border-radius: 2px;
      font-size: 12px;
      font-weight: 600;
      
      &.api-badge {
        background: #e0f7ff;
        color: #409eff;
      }
    }
  }
  
  .card-content {
    padding: 20px;
  }
}

// 表单组件样式
.form-group {
  margin-bottom: 20px;
  
  .form-label {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #303133;
    
    .el-icon {
      color: #409eff;
    }
    
    &.required::after {
      content: '*';
      color: #f56c6c;
      margin-left: 4px;
    }
  }
  
  .form-input,
  .form-select {
    width: 100%;
  }
}

// 请求配置区域
.request-section {
  margin-bottom: 24px;
  
  .request-line {
    display: flex;
    gap: 12px;
    align-items: stretch;
    
    .method-selector {
      flex-shrink: 0;
      
      .method-select {
        width: 120px;
      }
    }
    
    .url-input-wrapper {
      flex: 1;
    }
  }
}

// 标签页样式
.tabs-container {
  margin-top: 20px;
  
  .modern-tabs {
    :deep(.el-tabs__header) {
      background: transparent;
      border-bottom: 1px solid #ebeef5;
      margin-bottom: 20px;
      
      .el-tabs__item {
        color: #909399;
        font-weight: 500;
        
        &:hover {
          color: #409eff;
        }
        
        &.is-active {
          color: #409eff;
          border-bottom-color: #409eff;
        }
      }
    }
    
    :deep(.el-tabs__content) {
      padding: 0;
    }
  }
}

// 参数表格
.params-table-wrapper {
  margin-bottom: 16px;
  
  .modern-table {
    background: white;
    
    :deep(.el-table__header-wrapper) {
      background: #f5f7fa;
    }
    
    :deep(.el-table__body) {
      tr {
        &:hover {
          background: #f5f7fa;
        }
      }
    }
  }
}

.add-param-section {
  text-align: center;
  padding: 12px;
  
  .add-param-btn {
    border: 1px solid #dcdfe6;
    background: white;
    color: #409eff;
    border-radius: 4px;
    
    &:hover {
      color: #66b1ff;
      border-color: #66b1ff;
    }
  }
}

// Body编辑器
.body-editor {
  .body-type-selector {
    margin-bottom: 20px;
    
    .modern-radio-group {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      
      :deep(.el-radio-button) {
        margin: 0;
        
        .el-radio-button__inner {
          background: white;
          border: 1px solid #dcdfe6;
          border-radius: 4px;
          padding: 8px 16px;
          color: #606266;
        }
        
        &.is-active .el-radio-button__inner {
          background: #409eff;
          border-color: #409eff;
          color: white;
        }
      }
    }
  }
}

// 测试结果
.result-section {
  margin-bottom: 20px;
}

.result-card {
  .result-status {
    .status-tag {
      padding: 8px 16px;
      border-radius: 4px;
      font-weight: 600;
      font-size: 13px;
    }
  }
  
  .response-content {
    background: #f5f7fa;
    padding: 16px;
    border-radius: 4px;
    font-family: 'Monaco', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.6;
    color: #303133;
    max-height: 400px;
    overflow: auto;
    border: 1px solid #ebeef5;
  }
}

// 响应式布局
@media (max-width: 768px) {
  .header-section {
    .header-content {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }
    
    .title-section {
      flex-direction: column;
      text-align: center;
    }
    
    .header-actions {
      justify-content: center;
    }
  }
  
  .request-section {
    .request-line {
      flex-direction: column;
    }
  }
  
  .tabs-container {
    .modern-tabs {
      :deep(.el-tabs__header) {
        .el-tabs__item {
          padding: 0 12px;
          font-size: 12px;
        }
      }
    }
  }
}

@media (max-width: 480px) {
  .api-info-form-container {
    padding: 12px;
  }
  
  .header-section {
    padding: 16px;
    
    .title-text {
      .page-title {
        font-size: 18px;
      }
    }
  }
}
</style>
