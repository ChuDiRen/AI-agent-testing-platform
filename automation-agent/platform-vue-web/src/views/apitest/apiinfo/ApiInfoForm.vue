<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <el-form ref="ruleFormRef"  :inline="true"  :model="apiInfo" :rules="rules"  class="demo-form-inline">
    <!-- 模块 - 基础信息部分 - 按钮部分 -->
    <div class="form-wrapper">
      <div class="form-info">| 基础信息</div>
      <el-form-item class="form-buttons">
        <el-button type="primary" @click="onSubmit()">保存</el-button>
        <el-dropdown  trigger="click">
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
        <el-button  @click="onCancel">关闭</el-button>
      </el-form-item>
    </div>
    <!-- END 模块 - 基础信息部分 - 按钮部分 -->

    <!-- 模块 - 基础信息部分 - 字段部分 -->
    <div> 
    <el-form-item label="接口编号：">
      <el-input v-model="apiInfo.id" placeholder="接口编号" clearable disabled />
    </el-form-item>
    <el-form-item label="接口名称：">
      <el-input v-model="apiInfo.api_name" placeholder="输入接口名称" clearable prop="api_name" />
    </el-form-item>
    <el-form-item label="所属项目ID：" prop="project_id"  >
      <el-select v-model="apiInfo.project_id" placeholder="选择所属项目" filterable clearable>
        <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
      </el-select>
    </el-form-item>
    </div>
    <el-form-item label="接口描述：">
      <el-input v-model="apiInfo.case_desc" style="width: 600px" :rows="3" type="textarea" placeholder="请输入接口描述" />
    </el-form-item>
    <!-- END 模块 - 基础信息部分 - 字段部分 -->

    <!-- 模块 - 接口信息部分 - 字段部分 -->
    <div class="form-wrapper">
      <div class="form-info">| 接口信息</div>
    </div>

     <el-select
          v-model="apiInfo.request_method"
          placeholder="请求方式"
          style="width: 100px; margin-left: 0px;"
     >
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
    <!-- END 模块 - 接口信息部分 - 字段部分 -->

    <!-- 模块 - 接口信息部分 - 请求参数部分 -->
    <el-form-item style="margin-top: 10px;">
    <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 1150px;">
    <el-tab-pane label="URL参数" name="URL参数">
      <!-- 维护对应URL参数  -->
      <!-- 显示 - 显示对应URL参数 -->
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
      <!-- END 显示对应URL参数 -->

      <!-- 添加 - 添加对应URL参数 -->  
       <div id="addData">
          <el-input v-model="requestParams.key"  placeholder="输入参数名" style="width: 30%" />
          <el-input v-model="requestParams.value" placeholder="输入参数"   style="width: 30%" />
          <el-button style="width: 20%" @click="onAddParams">添加</el-button>
       </div>
      <!-- END 添加对应URL参数  -->
    </el-tab-pane>
    <el-tab-pane label="请求头Header" name="请求头Header">
     <!-- END 显示对应Header参数 -->
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
         <!-- END 显示对应Header参数 -->

        <!-- 添加 - 添加对应Header参数 -->  
          <div id="addData">
          <el-input v-model="requestHeaders.key"  placeholder="输入请求头名" style="width: 30%" />
          <el-input v-model="requestHeaders.value" placeholder="输入请求头参数"   style="width: 30%" />
          <el-button style="width: 20%" @click="onAddHeaders">添加</el-button>
          </div>
        <!-- END - 添加对应Header参数 -->  
   </el-tab-pane>

    <el-tab-pane label="请求Body" name="请求Body">
      <!-- 请求数据：form-data 、x-www-form-data 、json、files -->
      <el-tabs class="demo-tabs" model-value="form-data">
           <!-- Body-form-data  -->
            <el-tab-pane label="form-data" name="form-data">
              <el-table  :data="apiInfo.request_form_datas" style="width: 100%"  max-height="250" >
                <el-table-column  prop="key"  label="表单参数名" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="表单参数名" />
                    <span v-else>{{ scope.row.key }}</span>
                  </template>
                </el-table-column>
                <el-table-column  prop="value"  label="表单参数" style="width: 30%">
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="表单参数" />
                    <span v-else>{{ scope.row.value }}</span>
                  </template>
                </el-table-column>
                <el-table-column fixed="right" label="操作" style="width: 20%">
                  <template #default="scope">
                    <el-button link type="primary"  size="small"    @click.prevent="toggleEdit(scope.row)">
                      {{ scope.row.editing ? '确认' : '修改' }}
                    </el-button>
                    <el-button  link  type="primary"  size="small" @click.prevent="deleteBodyFormDatas(scope.$index)" >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div id="addData">
                <el-input v-model="requestBodyFormDatas.key"  placeholder="输入表单参数名"  style="width: 30%"/>
                <el-input v-model="requestBodyFormDatas.value"  placeholder="输入表单参数"  style="width: 30%" />
                <el-button style="width: 20%" @click="onAddBodyFormDatas">添加</el-button>
              </div>
            </el-tab-pane>
            <!-- END Body-form-data  -->
            
            <!-- Body-x-www-form-data -->
            <el-tab-pane label="x-www-form-data" name="x-www-form-data">
              <el-table   :data="apiInfo.request_www_form_datas"    style="width: 100%"    max-height="250">
                <el-table-column prop="key" label="表单参数名" style="width: 30%" >
                  <template #default="scope">
                    <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="表单参数名" />
                    <span v-else>{{ scope.row.key }}</span>
                  </template>
                </el-table-column>
                <el-table-column   prop="value" label="表单参数" style="width: 30%" >
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
                    <el-button link type="primary" size="small" @click.prevent="deleteBodyWwwFormDatas(scope.$index)" >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div id="addData">
                <el-input v-model="requestBodyWwwFormDatas.key"  placeholder="输入表单参数名" style="width: 30%"/>
                <el-input v-model="requestBodyWwwFormDatas.value" placeholder="输入表单参数" style="width: 30%"/>
                <el-button style="width: 20%" @click="onAddBodyWwwFormDatas">添加</el-button>
              </div>
            </el-tab-pane>
            <!-- END Body-x-www-form-data -->

            <!-- Body-json -->
            <el-tab-pane label="json" name="json">
              <el-input v-model="apiInfo.requests_json_data"  type="textarea" :rows="10" placeholder="请输入内容"/>
            </el-tab-pane>
            <!-- END Body-json -->

            <!-- Body-files -->            
            <el-tab-pane label="files" name="files">
            <el-table :data="apiInfo.request_files" style="width: 100%"  max-height="250">
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
                    <el-button link type="primary" size="small" @click.prevent="deleteBodyFilesFormDatas(scope.$index)" >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
              <div id="addData">
                <el-input v-model="requestFilesFormDatas.key" placeholder="输入表单参数名" style="width: 30%" />
                <el-input v-model="requestFilesFormDatas.value" placeholder="输入表单参数" style="width: 30%"/>
                <el-button style="width: 20%" @click="onAddBodyFilesFormDatas">添加</el-button>
              </div>
            </el-tab-pane>
            <!-- END Body-files -->  
      </el-tabs>
       <!-- END 请求数据：form-data 、x-www-form-data 、json、files -->
    </el-tab-pane>

    <el-tab-pane label="变量定义" name="变量定义">
         <!-- 显示对应变量参数 -->
          <el-table :data="apiInfo.debug_vars"  style="width: 100%"  max-height="250" >
            <el-table-column prop="key" label="变量名" style="width: 30%">
              <template #default="scope">
                <el-input v-if="scope.row.editing" v-model="scope.row.key" placeholder="变量名" />
                <span v-else>{{ scope.row.key }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="value" label="变量" style="width: 30%">
              <template #default="scope">
                <el-input v-if="scope.row.editing" v-model="scope.row.value" placeholder="变量" />
                <span v-else>{{ scope.row.value }}</span>
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" style="width: 20%">
              <template #default="scope">
                <el-button link type="primary" size="small"  @click.prevent="toggleEdit(scope.row)">
                  {{ scope.row.editing ? '确认' : '修改' }}
                </el-button>
                <el-button link  type="primary" size="small" @click.prevent="deleteVars(scope.$index)" >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <!-- END 显示对应变量参数 -->

          <!-- 添加对应变量参数 -->  
          <div id="addData">
          <el-input v-model="debugVars.key" placeholder="输入变量名"  style="width: 30%"/>
          <el-input v-model="debugVars.value" placeholder="输入变量" style="width: 30%"/>
          <el-button style="width: 20%" @click="onAddVars">添加</el-button>
          </div>
          <!-- END - 添加对应变量参数 -->  
    </el-tab-pane>

    <el-tab-pane label="调试输出内容" name="调试输出内容">
      <el-collapse v-model="activeDebugResultPanel" accordion>
        <el-collapse-item name="resultDetails">
        <template #title>
          <span :class="['debug-panel-title', debugResult.test_result?.toLowerCase()]">
            {{ debugPanelTitle }}
          </span>
        </template>
        <div class="debug-detail-section">
          <div class="debug-row">
            <strong class="label">请求URL:</strong> {{ debugResult.url }}
          </div>
          <div class="debug-row">
            <strong class="label">请求方式:</strong> {{ debugResult.method }}
          </div>
          <div class="debug-row">
            <strong class="label">请求头:</strong>
            <el-input v-model="debugResult.headers" type="textarea" :rows="4" readonly />
          </div>
          <div class="debug-row">
            <strong class="label">请求数据:</strong>
            <el-input v-model="debugResult.body" type="textarea" :rows="4" readonly />
          </div>
          <div class="debug-row">
            <strong class="label">响应数据:</strong>
            <el-input v-model="debugResult.response" type="textarea" :rows="6" readonly />
          </div>
        </div>
      </el-collapse-item>
      </el-collapse>
    </el-tab-pane> 

    </el-tabs>
    </el-form-item>
    <!-- END 模块 - 接口信息部分 - 请求参数部分 -->
  </el-form>
</div>
</template>
  
<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { queryById, insertData, updateData } from "@/api/ApiInfo"; // 不同页面不同的接口
import { ElMessage } from 'element-plus';
import { useRouter } from "vue-router";
import Breadcrumb from "../../Breadcrumb.vue";

const router = useRouter();
// 表单实例
const ruleFormRef = ref();
const tabActiveName = ref("URL参数");

const apiInfo = reactive({
  id:0,
  project_id: "请选择项目" ,
  api_name: "",
  request_method: "",
  request_url: "",
  request_params: [],
  request_headers: [],
  debug_vars: [],
  request_form_datas: [],
  request_www_form_datas: [],
  requests_json_data: "",
  request_files: [],
});
// 1. 加载项目
import { queryAllProject } from "@/api/ApiProject"; // 不同页面不同的接口
const projectList = ref([{
  id: 0,
  project_name: '',
  project_desc: ''
}]);
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data;
  });
}
getProjectList();

// 3. 如果有id参数，说明是编辑，需要获取数据
const loadData = async (id) => {
  const res = await queryById(id)
  // 不同的页面，不同的表单字段 (注意这里的res.data.data.xxx，xxx是接口返回的字段，不同的接口，字段不同)
  // 注意:此处将 后台的json字符串转变为对象
  apiInfo.id = res.data.data.id
  apiInfo.project_id = res.data.data.project_id
  apiInfo.api_name = res.data.data.api_name
  apiInfo.request_method = res.data.data.request_method
  apiInfo.request_url = res.data.data.request_url
  apiInfo.request_params = JSON.parse(res.data.data.request_params) //将json对象转换为json字符串，传给后端,
  apiInfo.request_headers = JSON.parse(res.data.data.request_headers)
  apiInfo.debug_vars = JSON.parse(res.data.data.debug_vars)
  apiInfo.request_form_datas = JSON.parse(res.data.data.request_form_datas) // 请求中的 form-data
  apiInfo.request_www_form_datas = JSON.parse(res.data.data.request_www_form_datas) // 请求中的 x-www-form-data
  apiInfo.requests_json_data = res.data.data.requests_json_data // 请求中的 json 数据
  apiInfo.request_files = JSON.parse(res.data.data.request_files) // 请求中的 x-www-form-data
}
let query_id = router.currentRoute.value.query.id
apiInfo.id = query_id ? Number(query_id) : 0

if (apiInfo.id > 0) {
  loadData(apiInfo.id)
}

// 4. 表单操作
// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive({
  api_name: [
    { required: true, message: '必填项', trigger: 'blur' }
  ],
  module_desc: [
    { required: true, message: '必填项', trigger: 'blur' }
  ]
});

const onSubmit = () => {
  // 当项目ID没有选择的时候，提示
  if (apiInfo.project_id == '请选择项目') {
    ElMessage.error('请选择对应的项目');
    return;
  } 

  // 提交之前记得把数组修改为json字符串
  let data = {
      id:apiInfo.id,
      project_id: apiInfo.project_id ,
      api_name: apiInfo.api_name,
      request_method: apiInfo.request_method,
      request_url: apiInfo.request_url,
      request_params: JSON.stringify(apiInfo.request_params), //将json对象转换为json字符串，传给后端,
      request_headers: JSON.stringify(apiInfo.request_headers),
      debug_vars: JSON.stringify(apiInfo.debug_vars),
      request_form_datas: JSON.stringify(apiInfo.request_form_datas), // 请求中的 form-data
      request_www_form_datas: JSON.stringify(apiInfo.request_www_form_datas), // 请求中的 x-www-form-data
      requests_json_data: apiInfo.requests_json_data, // 请求中的 json 数据
      request_files: JSON.stringify(apiInfo.request_files), // 请求中的 文件的数据
    }

  if (apiInfo.id > 0) {
    updateData(data).then((res) => {
        if (res.data.code == 200) {
        loadData(apiInfo.id)
          // router.push('/ApiInfoList') // 跳转回列表页面 - 不同的页面，不同的路径
        }
      })
  } else {
    insertData(data).then((res) => {
      if (res.data.code == 200) {
      loadData(res.data.data.id)
        // router.push('/ApiInfoList') // 跳转回列表页面 - 不同的页面，不同的路径
      }
    });
  }
};

const onCancel = () => {
  router.push('/ApiInfoList')
};

// ==================  扩展：请求URL参数 - 增加、删除、修改 ==================
const requestParams = reactive({
  key: "",
  value: "",
});

const deleteParams = (index) => {
  apiInfo.request_params.splice(index, 1);
};

// 参数添加
const onAddParams = () => {
  // 保存起来
  apiInfo.request_params.push({
    key: requestParams.key,
    value: requestParams.value,
  });
  // 置空
  requestParams.key = "";
  requestParams.value = "";
};

// 修改
const toggleEdit = (row) => {
  if (row.editing) {
    // 调用 onSubmit 函数
    row.editing = false;
    // 恢复所有行的编辑状态
    apiInfo.request_params.forEach((param) => {
      param.editing = false;
    });
    // ...
    apiInfo.request_headers.forEach((header) => {
      header.editing = false;
    });
    
    apiInfo.debug_vars.forEach((debugVar) => {
      debugVar.editing = false;
    });
    

    onSubmit();
  } else {
    // 进入编辑状态
    row.editing = true;
  }
};
// ================== END 扩展：请求URL参数 - 增加、删除、修改 ==================


// ==================  扩展：请求Headers参数 - 增加、删除、修改 ==================
const requestHeaders = reactive({
  key: "",
  value: "",
});

const deleteHeaders = (index) => {
  apiInfo.request_headers.splice(index, 1);
};

// 参数添加
const onAddHeaders = () => {
  // 保存起来
  apiInfo.request_headers.push({
    key: requestHeaders.key,
    value: requestHeaders.value,
  });
  // 置空
  requestHeaders.key = "";
  requestHeaders.value = "";
};
// ==================  扩展：请求Headers参数 - 增加、删除、修改 ==================

// ==================  扩展：变量定义 - 增加、删除、修改 ==================
// debugVars 变量定义
const debugVars = reactive({
  key: "",
  value: "",
});

const deleteVars = (index) => {
  apiInfo.debug_vars.splice(index, 1);
};

const onAddVars = () => {
  // 保存起来
  apiInfo.debug_vars.push({
    key: debugVars.key,
    value: debugVars.value,
  });
  // 置空
  debugVars.key = "";
  debugVars.value = "";
};
// ==================  END 扩展：变量定义 - 增加、删除、修改 ==================


// ================== 扩展：请求BODY维护==================

// requestBodyFormDatas 变量定义
const requestBodyFormDatas = reactive({
  key: "",
  value: "",
});

const deleteBodyFormDatas = (index) => {
  apiInfo.request_form_datas.splice(index, 1);
};

const onAddBodyFormDatas = () => {
  // 保存起来
  apiInfo.request_form_datas.push({
    key: requestBodyFormDatas.key,
    value: requestBodyFormDatas.value,
  });
  // 置空
  requestBodyFormDatas.key = "";
  requestBodyFormDatas.value = "";
};

// requestBodyWwwFormDatas 变量定义
const requestBodyWwwFormDatas = reactive({
  key: "",
  value: "",
});

const deleteBodyWwwFormDatas = (index) => {
  apiInfo.request_www_form_datas.splice(index, 1);
};

const onAddBodyWwwFormDatas = () => {
  // 保存起来
  apiInfo.request_www_form_datas.push({
    key: requestBodyWwwFormDatas.key,
    value: requestBodyWwwFormDatas.value,
  });
  // 置空
  requestBodyWwwFormDatas.key = "";
  requestBodyWwwFormDatas.value = "";
};

// requestFilesFormDatas 变量定义
const requestFilesFormDatas = reactive({
  key: "file",
  value: "",
});

const deleteBodyFilesFormDatas = (index) => {
  apiInfo.request_files.splice(index, 1);
};

const onAddBodyFilesFormDatas = () => {
  // 保存起来
  apiInfo.request_files.push({
    key: requestFilesFormDatas.key,
    value: requestFilesFormDatas.value,
  });
  // 置空
  requestFilesFormDatas.key = "file";
  requestFilesFormDatas.value = "";
};
// ==================  END 扩展：请求BODY维护==================


// ================== 扩展：调试请求==================
import { doDebugRequest } from "@/api/ApiInfo"
const debugRequest = () => {
  tabActiveName.value = "调试输出内容";

  if (apiInfo.id < 1) {
    ElMessage.error("请保存请求参数后再进行调试");
    return;
  }

  // apiInfo.download_response = false; 

  doDebugRequest(apiInfo).then((res) => {
    const responseData = res.data; // 假设返回结构为 { code, data, msg }

    if (responseData.code === 200 && responseData.data) {
      // 成功获取数据
      ElMessage.warning("调试成功，请查看调试结果面板");

      const resultData = responseData.data.output;

      debugResult.test_result = resultData.test_result || "未知";
      debugResult.method = resultData.method || "未知";
      debugResult.url = resultData.url || "未知";
      debugResult.headers = JSON.stringify(resultData.headers, null, 2);
      debugResult.body = JSON.stringify(resultData.body, null, 2);
      debugResult.response = resultData.response || "未知";

    } else {
      ElMessage.error("调试失败，未获取到有效数据");
    }
  });
};
// ==================  END 扩展：调试请求==================



// ==================  扩展：折叠面板状态数据==================
// 折叠面板状态
const activeDebugResultPanel = ref("resultDetails");

// 调试结果对象
const debugResult = reactive({
  test_result: "",
  method: "",
  url: "",
  headers: "",
  body: "",
  response: ""
});

// 动态计算折叠面板标题
const debugPanelTitle = computed(() => {
  return `   调试结果: ${debugResult.test_result || "未知"} | 请求方式: ${
    debugResult.method || "未知"
  } | 请求URL: ${debugResult.url || "未知"}`;
});
// ==================  END 扩展：折叠面板状态数据==================



// ==================  扩展：发送请求并且下载请求结果==================

const downloadUrl = ref(null)
const debugRequestandDownload = () => {
  console.log("当前要进行调试并下载的接口：",apiInfo);
  tabActiveName.value = "调试输出内容";
  apiInfo.download_response = true; // 添加下载响应数据的标记
  doDebugRequest(apiInfo).then((res)=>{
    //  页面显示对应的字段
    //  console.log(res)
     const responseData = res.data; // 假设返回结构为 { code, data, msg }

    if (responseData.code === 200 && responseData.data) {
      const resultData = responseData.data.output;

      debugResult.test_result = resultData.test_result || "未知";
      debugResult.method = resultData.method || "未知";
      debugResult.url = resultData.url || "未知";
      debugResult.headers = JSON.stringify(resultData.headers, null, 2);
      debugResult.body = JSON.stringify(resultData.body, null, 2);
      debugResult.response = resultData.response || "未知";
    } else {
      ElMessage.error("调试失败，未获取到有效数据");
    }

    downloadUrl.value =  res.data.data.output.current_response_file_path
    console.log("下载地址：",downloadUrl.value)
  })
};

const downloadResponseData = () => {
  //  当没有数据则提示用户
  if (apiInfo.id < 1) {
    ElMessage.error("请添加请求参数或者保存请求参数后，再进行调试");
    return;
  }

  // 调用调试请求以触发下载URL的生成
  debugRequestandDownload();

  // 定义轮询函数
  const pollForDownloadUrl = (resolve, reject) => {
    const maxRetries = 50; // 最大重试次数
    let retries = 0;
    const intervalTime = 100; // 每次轮询间隔时间（毫秒）

    const checkDownloadUrl = () => {
      if (downloadUrl.value) {
        resolve(downloadUrl.value);
      } else if (retries < maxRetries) {
        retries++;
        setTimeout(checkDownloadUrl, intervalTime);
      } else {
        reject('超时：未获取到有效的下载链接');
      }
    };

    checkDownloadUrl();
  };

  // 使用Promise进行轮询
  new Promise(pollForDownloadUrl)
    .then((url) => {
      // 打开页面
      console.log('下载链接：', url);


      window.open(downloadUrl.value, '_blank'); // 打开下载链接
      downloadUrl.value = null; // 重置下载链接
    })
    .catch((error) => {
      ElMessage.error(error); // 提示错误信息
    });
};

// ==================  END 扩展：发送请求并且下载请求结果==================

</script>



<style>
/* 控制保存和取消按钮右对齐 */
.form-wrapper {
  margin-bottom: 20px;
  /* 根据需要调整间隔大小 */
  border-bottom: 1px solid #ccc;
  /* 添加横线，颜色和粗细可以根据需要调整 */
  display: flex;
  align-items: center;
  /* 垂直居中 */
  justify-content: space-between;
  /* 水平分布，使得两端元素靠边 */
}
.demo-form-inline .el-select {
  --el-select-width: 145px;
  margin-right: 10px;
  /* 设置右边距 */
  margin-left: 5px;
  /* 设置右边距 */
}
/* 控制添加的间隙 */
.input-group {
  margin-top: 15px;
  /* 根据需要调整间隔大小 */
}
/* 更改 el-select 的宽度 */  
.el-select {  
  width: 200px; /* 设置你想要的宽度 */  
}  

/* 调整id =addData 的div 添加元素宽度*/
#addData {
  width: 1000px;
  margin-top: 20px;
}

/* ----------折叠面板样式-------------- */
.debug-detail-section {
  padding: 20px;
  border: 1px solid #e1e1e1;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.debug-info-row {
  margin-bottom: 15px;
}

.debug-row {
  margin-bottom: 20px;
}

.debug-row:last-child {
  margin-bottom: 0;
}

.label {
  font-weight: bold;
  display: inline-block;
  width: 100px;
  vertical-align: top;
  color: #303133;
}

.debug-value {
  display: inline-block;
  padding: 2px 0;
  color: #606266;
}

.debug-content {
  margin-top: 8px;
}

.debug-textarea .el-textarea__inner {
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  transition: border-color 0.2s cubic-bezier(0.645, 0.045, 0.355, 1);
}

.debug-textarea .el-textarea__inner:hover {
  border-color: #c0c4cc;
}

.debug-textarea .el-textarea__inner:focus {
  border-color: #409eff;
}

/* 标题颜色控制 */
.el-collapse-item__header {
  font-weight: bold !important;
  background-color: #f5f7fa;
  padding-left: 15px;
  border-radius: 4px;
}

/* 自定义状态颜色 */
.debug-panel-title.passed {
  color: #67c23a; /* 绿色 */
}

.debug-panel-title.failed {
  color: #f56c6c; /* 红色 */
}

.debug-panel-title.unknown {
  color: #909399; /* 灰色 */
}

.debug-panel-title {
  font-weight: bold;
}
</style>
  