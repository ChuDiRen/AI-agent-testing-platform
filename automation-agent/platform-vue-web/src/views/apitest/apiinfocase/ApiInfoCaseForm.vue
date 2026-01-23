<template>
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
   <!-- 用例信息模块 -->
    <el-form-item>
      <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 100%">
   <!-- 用例信息模块 -->
    <el-form-item style="width: 1100px;">
      <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 100%">
       <!-- 功能1：测试用例步骤 -->
       <el-tab-pane label="当前用例步骤" name="当前用例步骤">
       <!-- 功能1-1 显示已经添加的所有步骤-->
        <el-table :data="tableDataCaseStep" row-key="id" class="table_data" max-height="500">
            <!-- 操作的按钮 --> 
            <el-table-column fixed="left" label="操作" width="80">
              <template #default="scope">
                <el-button link type="primary" size="small"
                  @click="updateAppCaseStep(scope.row)">
                  确认修改
                </el-button>
                <br />
                <el-button link type="primary" size="small" @click="onDelete(scope.row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>

            <!-- 显示的字段数据 --> 
            <el-table-column prop="run_order" label="执行顺序" width="120">
              <template #default="scope">
                 <!--<el-input style="width: 50px" v-model="scope.row.run_order" placeholder="顺序-数字类型"/>-->
                <el-input-number v-model="scope.row.run_order" :min="1" style="width: 107px" controls-position="right" placeholder="顺序"/>
              </template>
            </el-table-column>
            <el-table-column prop="step_desc" label="步骤描述" width="480">
              <template #default="scope">
                <el-input style="max-width: 600px; width: 360px" v-model="scope.row.step_desc"
                  placeholder="输入步骤描述"></el-input>
              </template>
            </el-table-column>
            <el-table-column prop="vaule" label="关键字操作" width="320">
              <template #default="scope">
                <el-cascader v-model="scope.row.value" :options="keyWordAllList" @change="onStepKeyModifyChange(scope.$index)" />
              </template>
            </el-table-column>
             
            <!-- 扩展部分的数据 -->      
            <el-table-column prop="ref_variable" label="关键字参数" type="expand" width="120" style="background-color: antiquewhite;">
              <template #default="scope">
                <!-- 循环遍历出所有的参数数据 -->
                <span style="margin-left: 10px;" v-for="variable in findKeyWordByName(scope.row.value[1]).keyword_desc">
                  <span style="margin-right: 10px;">{{ variable.name }}</span >
                    <!-- 如果是接口信息对象 -->
                    <el-select v-if="variable.name.endsWith('_接口信息')"
                              v-model="scope.row.ref_variable[variable.name]"
                              filterable placeholder="选择接口信息" 
                              style="width: 180px"  
                              clearable>
                    <!-- ref_name 即是写入到数据库当中的数据  -->
                    <el-option
                              v-for="dataRequest in dataRequestList"
                              :key="dataRequest.id"
                              :label="dataRequest.api_name"
                              :value="dataRequest.id" >
                    </el-option>
                    </el-select>
                    <!-- END 如果是接口信息对象 -->
                      
                    <!-- 如果是数据库信息对象 -->
                    <el-select v-else-if="variable.name.endsWith('_数据库')"
                              v-model="scope.row.ref_variable[variable.name]"
                              filterable placeholder="_数据库" 
                              style="width: 180px"  
                              clearable>
                    <!-- ref_name 即是写入到数据库当中的数据  -->
                    <el-option
                              v-for="database in databaseList"
                              :key="database.id"
                              :label="database.name"
                              :value="database.ref_name" >
                    </el-option>
                    </el-select>
                    <!-- END 如果是数据库信息对象 -->
                     

                    <!-- 普通参数就是一个输入框 -->
                    <el-input v-else style="width: 240px; margin: left 20px ;"
                              v-model="scope.row.ref_variable[variable.name]"
                              :placeholder="variable.placeholder">
                    </el-input>
                    <!-- END 普通参数就是一个输入框 -->
                </span>
              </template>
            </el-table-column>
        </el-table>
        <!-- 功能1-2 添加对应的测试用例步骤-->
        <div class="input-group">
            <el-input-number v-model="tmp_apiCaseStep.run_order"  :min="1" controls-position="right" placeholder="顺序"/>
            <el-input v-model="tmp_apiCaseStep.step_desc" placeholder="输入步骤描述"/>
              <!-- 1. 以级联的方式去进行数据的显示 -->
            <el-cascader :options="keyWordAllList" @change="onStepAddKeyHandleChange"/> 
              <!-- 2. 根据关键字参数生成对应的输入框 -->
              <!-- 1-1 根据关键字参数生成对应的输入框 -->
            <span v-if="tmp_apiCaseStep.keyword != undefined" v-for="variable in findKeyWordById(tmp_apiCaseStep.keyword.id).keyword_desc">
              <!-- 1-2 普通参数就是一个输入框 -->

            <!-- 扩展 如果是发送请求，则加载一个下拉列表  -->
            <el-select v-if="variable.name.endsWith('_接口信息')"
                v-model="tmp_apiCaseStep.ref_variable[variable.name]"
                filterable
                placeholder="选择接口信息"
                style="width: 180px"
                clearable
              >
               <!-- ref_name 即是写入到数据库当中的数据  -->
                <el-option
                  v-for="dataRequest in dataRequestList"
                  :key="dataRequest.id"
                  :label="dataRequest.api_name"
                  :value="dataRequest.id" 
                >
                </el-option>
            </el-select>

                <!-- 扩展 如果是数据库，则加载一个下拉列表  -->
                <el-select v-else-if="variable.name.endsWith('_数据库')"
                    v-model="tmp_apiCaseStep.ref_variable[variable.name]"
                    filterable
                    placeholder="选择数据库对象"
                    style="width: 180px"
                    clearable
                    >
                    <!-- ref_name 即是写入到数据库当中的数据  -->
                    <el-option
                        v-for="database in databaseList"
                        :key="database.id"
                        :label="database.name"
                        :value="database.ref_name" 
                    >
                    </el-option>
                </el-select>

              <el-input v-else  v-model="tmp_apiCaseStep.ref_variable[variable.name]" :placeholder="variable.placeholder" />
            </span>
            <!-- END 2. 根据关键字参数生成对应的输入框 -->
            <el-button style="width: 10%" @click="addApiInfoStep">添加</el-button>
        </div>
        <!-- END 功能1-2 添加对应的测试用例步骤-->

       </el-tab-pane>
       <!-- 功能2：变量定义 -->
       <el-tab-pane label="变量定义" name="变量定义">
          <!-- 2-1 变量描述的数据显示部分 -->
          <el-table  :data="apiInfo.param_data"   class="table_data"   max-height="250" >
          <el-table-column prop="key" label="变量名" style="width: 40%" />
          <el-table-column prop="value" label="变量值" style="width: 40%" />
          <el-table-column fixed="right" label="删除" style="width: 15%">
            <template #default="scope">
              <el-button link  type="primary"   size="small"  @click.prevent="deleteVars(scope.$index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
          <!-- 2-2 添加变量描述位置 -->
          <div class="input-group">
          <el-input v-model="vars.key" placeholder="变量名" style="width: 30%"  />
          <el-input v-model="vars.value" placeholder="变量描述" style="width: 30%"  />
          <el-button style="width: 20%" @click="onAddVars">添加</el-button>
          </div>
       </el-tab-pane>
       <!-- 功能3：前置脚本 -->
       <el-tab-pane label="执行前事件(pre)" name="执行前事件(pre)">
        <el-input v-model="apiInfo.pre_request" type="textarea" :rows="15" placeholder="执行前事件" />
       </el-tab-pane>
       <!-- 功能4：前置脚本 -->
       <el-tab-pane label="执行后事件(post)" name="执行后事件(post)">
       <el-input v-model="apiInfo.post_request" type="textarea" :rows="15" placeholder="执行后事件" />
       </el-tab-pane>
      </el-tabs>
    </el-form-item>
   <!--END 用例信息模块 -->
      </el-tabs>
    </el-form-item>
   <!--END 用例信息模块 -->
  </el-form>
</template>

<script lang="ts" setup>
import { reactive, ref } from "vue";
import { queryById, insertData, updateData } from "./ApiInfoCase.js"; // 不同页面不同的接口
import type { FormInstance, FormRules } from "element-plus";
import { useRouter } from "vue-router";
import { ElMessage } from 'element-plus';
import Breadcrumb from "../../Breadcrumb.vue";

// 获取当前路由的实例
const router = useRouter(); 

// 初始化搜索 - 用例搜索
const searchForm = reactive({});

// 表单实例
const ruleFormRef = ref<FormInstance>(); 

// 设置后续的默认的选择的Tab
const tabActiveName = ref("当前用例步骤");

// 变量 - 用例的所有数据
const apiInfo = reactive({
  id: 0,
  project_id: "请选择项目",
  case_name: "",
  case_desc: "",
  param_data: [] as any[],
  pre_request: "", // 执行前事件
  post_request: "", // 执行后事件
});

// 变量- 是否下拉列表
const options = [
  {
    value: "1",
    label: "是",
  },
  {
    value: "0",
    label: "否",
  },
];

// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive<any>({
  project_id: [{ required: true, message: "必填项", trigger: "blur" }],
  case_name: [{ required: true, message: "必填项", trigger: "blur" }],
});

// 加载对应的所有项目的数据
import { queryAllProject as queryAllProject } from "../project/ApiProject.js"; // 不同页面不同的接口
const projectList = ref([
  {
    id: 0,
    project_name: "",
    project_desc: "",
  },
]);
function getProjectList() {
  queryAllProject().then((res) => {
    projectList.value = res.data.data;
  });
}
getProjectList();

// ----------------------功能部分-------------------------------
// 功能：保存的数据
const onSubmit = () => {
  if (apiInfo.project_id == "请选择项目") {
    ElMessage.error("请选择项目");
    return;
  }

  // 提交之前记得把数组修改为json字符串
  let data = {
    id: apiInfo.id,
    project_id: apiInfo.project_id,
    case_name: apiInfo.case_name,
    case_desc: apiInfo.case_desc,
    param_data: JSON.stringify(apiInfo.param_data),
    pre_request: apiInfo.pre_request, // 执行前事件
    post_request: apiInfo.post_request, // 执行后事件
  };

  if (apiInfo.id > 0) {
    updateData(data).then((res: { data: { code: number; msg: string } }) => {
      if (res.data.code == 200) {
        // router.push("/ApiInfoCaseList"); // 跳转回列表页面 - 不同的页面，不同的路径
        // 重新加载当前的页面数据
        loadData(data.id);
      }
    });
  } else {
    insertData(data).then((res: { data: { code: number; msg: string } }) => {
      if (res.data.code == 200) {
        // router.push("/ApiInfoCaseList"); // 跳转回列表页面 - 不同的页面，不同的路径
        // 重新加载当前的页面数据
        loadData(res.data.data.id);
      }
    });
  }
};

// 功能：加载对应的数据
const loadData = async (id: number) => {
  const res = await queryById(id);
  // 不同的页面，不同的表单字段 (注意这里的res.data.data.xxx，xxx是接口返回的字段，不同的接口，字段不同)
  // 注意:此处将 后台的json字符串转变为对象
  apiInfo.id = res.data.data.id;
  apiInfo.project_id = res.data.data.project_id;
  apiInfo.case_name = res.data.data.case_name;
  apiInfo.case_desc = res.data.data.case_desc;
  apiInfo.param_data = JSON.parse(res.data.data.param_data);
  apiInfo.pre_request = res.data.data.pre_request; // 执行前事件
  apiInfo.post_request = res.data.data.post_request; // 执行后事件

  // 触发加载请求数据
  loaddataRequestList()

  // 触发加载当前用例步骤数据
  loadCaseStep()

  // 加载数据库信息
  loadDatabaseInfos() // 初始化加载一次   
};

let query_id = router.currentRoute.value.query.id;
apiInfo.id = query_id ? Number(query_id) : 0;

if (apiInfo.id > 0) {
  // 当ID大于0的时候，加载当前用例的信息
  loadData(apiInfo.id);
  // 获取其它的信息
  getProjectList();
}

// 功能：关闭按钮方法
const onCancel = () => {
  router.push("/ApiInfoCaseList");
};

// ----------------------扩展方法：关键字 变量定义---------------------------
const vars = reactive({
key: "",
value: "",
});

const deleteVars = (index: number) => {
  // splice() 方法可以在任意位置修改数组,并返回被删除的元素 （下标,个数）
apiInfo.param_data.splice(index, 1);
};

const onAddVars = () => {
// 保存起来
apiInfo.param_data.push({
  key: vars.key,
  value: vars.value,
});
// 置空
vars.key = "";
vars.value = "";
};
// ----------------------END 关键字 变量定义---------------------------


// ----------------------扩展方法：添加用例步骤数据---------------------------
// 1. 变量- 添加用例步骤数据 - 临时数据存放
const tmp_apiCaseStep = reactive({
  id: 0,
  run_order: 0,
  step_desc: "",
  operation_type: undefined,
  keyword: undefined,
  ref_variable: {}, // 保存关键对应的参数值
});

// 2. 字段- 加载操作方法-关键字  
import { queryAll as queryAllApiKey, queryAllKeyWordList as queryAllKeyWordList,} from "../keyword/ApiKeyWord.js"; // 不同页面不同的接口
  
const keyWordAllList = ref([]); // 关键字类型+关键字-树形数据

// 后台查询 关键字_类型-树形数据 -- 这个方法会被后续添加新的内容被舍弃
// function getKeyWordList() {
//   queryAllKeyWordList().then((res) => {
//     keyWordAllList.value = res.data.data;
//     // 把关键字中的 参数描述由json内容转换为 js 对象
//     keyWordAllList.value.forEach((keywordType, index) => {
//     // 遍历每一个 分类下的 children
//       var children = keyWordAllList.value[index]["children"]
//       children.forEach((keyword, i) => {
//         var data = JSON.parse(children[i]["keyword_desc"])
//         children[i]["keyword_desc"] = data
//       });
//     });
//     console.log("关键字类型+关键字-上下级树形数据加载完毕")
//     console.log(keyWordAllList.value)
//   });
// }
// getKeyWordList();
// ----------------------END 3.0 添加测试用例之关键字数据显示---------------------------



// ----------------------4.0 增加测试用例步骤功能之关键字数据动态显示对应的数据---------------------------
const keyWordList = ref([
  {
    id: 0,
    name: "--无--",
    keyword_desc: "[]",
    keyword_fun_name: "",
    operation_type_id: "",
    is_ture: "",
  },
]);

// 后台查询 关键字_类型-树形数据
function getKeyWordList() {
  // 请求接口1： 加载所有的关键字方法的数据 
  queryAllApiKey().then((res) => {
    // keyWordList.value = res.data.data;
    keyWordList.value.push(...res.data.data);
    // 把关键字中的 参数描述由json内容转换为 js 对象
    keyWordList.value.forEach((keyword, index) => {
      try {
        keyWordList.value[index]["keyword_desc"] = JSON.parse(keyWordList.value[index]["keyword_desc"])
      } catch (e) {
        console.warn("关键字描述解析失败:", keyWordList.value[index]["keyword_desc"], e);
        keyWordList.value[index]["keyword_desc"] = []
      }
    });

    console.log("关键字数据加载完毕")
    console.log(keyWordList.value)
  });

  // 请求接口2：加载对应的树状数据 
  queryAllKeyWordList().then((res) => {
    keyWordAllList.value = res.data.data;
    // 把关键字中的 参数描述由json内容转换为 js 对象
    keyWordAllList.value.forEach((keywordType, index) => {
    // 遍历每一个 分类下的 children
      var children = keyWordAllList.value[index]["children"]
      children.forEach((keyword, i) => {
        try {
          var data = JSON.parse(children[i]["keyword_desc"])
          children[i]["keyword_desc"] = data
        } catch (e) {
          console.warn("关键字描述解析失败:", children[i]["keyword_desc"], e);
          children[i]["keyword_desc"] = []
        }
      });
    });
    console.log("关键字类型+关键字-上下级树形数据加载完毕")
    console.log(keyWordAllList.value)
  });
}
getKeyWordList();


// 请求接口3：加载关键字类型
import { queryAll } from "../keyword/ApiOperationType.js"; // 不同页面不同的接口
const operationTypeList = ref([
  {
    id: 0,
    operation_type_name: "--无--",
    ex_fun_name: "--无--",
    create_time: "",
  },
]);
function getOperationTypeList() {
  queryAll().then((res) => {
    operationTypeList.value = res.data.data;
  });

  console.log("关键字类型-数据加载完毕")
  console.log(operationTypeList.value)
}
getOperationTypeList();


function findKeyWordById(key_word_id) { // 根据关键字ID查找关键字信息
  console.log("根据ID查找关键字信息:" + key_word_id)
  var result = {}
  // 所以我们需要获取所有的关键字数据，可以添加到：getKeyWordList 方法中
  keyWordList.value.forEach((keyword, index) => {
    if (key_word_id == keyword.id) result = keyword
  });
  return result
}

//  当前用例步骤-添加事件
const onStepAddKeyHandleChange = (value) => {
  console.log("当前选择的数据是", value);

  //  选择对应的操作之后动态的修改提示信息 --  找到对应的关键字
  const foundItemKW = keyWordList.value.find(
    (item) => item.keyword_fun_name === value[1]
  );
  console.log("当前需要查找的foundItemKW：",foundItemKW)
   
  //  选择对应的操作之后动态的修改提示信息 --  找到对应的操作类型
  const foundItemOP = operationTypeList.value.find(
    (item) => item.ex_fun_name === value[0]
  );
  console.log("当前需要查找的foundItemOP：",foundItemOP)

  // 如果存在则赋值给 appCaseStep 对象 
  if (foundItemKW) {
    console.log(foundItemKW.keyword_desc); // 输出找到的 keyword_desc
    tmp_apiCaseStep.keyword = foundItemKW;
  } else {
    console.log("没有找到 keyword_fun_name 对应的项");
  }

  if (foundItemOP) {
    tmp_apiCaseStep.operation_type = foundItemOP;
  } else {
    console.log("没有找到 keyword_fun_name 对应的项");
  }
};
// ----------------------END 4.0 增加测试用例步骤功能之关键字数据动态显示对应的数据---------------------------



// --------------------END 5.0 加载对应的数据库数据 --------------------
const projectChange = (value: number) => {
  // 触发加载请求数据
  loaddataRequestList()
    // 触发数据库信息加载
  loadDatabaseInfos()
};


import { queryByPage as queryApiInfoList } from "../apiinfo/ApiInfo.js"; // 不同页面不同的接口
// TODO 拓展 加载接口信息
const dataRequestList = ref([]);
const loaddataRequestList = async () => {
  let searchData = {};
  searchData["project_id"] = apiInfo.project_id;
  searchData["page"] = 1;
  searchData["pageSize"] = 99999; // 理论无限大

  queryApiInfoList(searchData).then(
      (res: { data: { data: never[]; total: number; msg: string } }) => {
        console.log("-------接口信息查询返回值------", res.data.data);
        dataRequestList.value = [] // 清空已有的数据库信息
        dataRequestList.value.push(...res.data.data); // 重新放置新的接口数据库信息
      }
    );
  
}
// --------------------END 5.0 加载对应的数据库数据 --------------------

// ---------------------6.0 添加对应的测试步骤---------------------------
import { ElMessageBox } from "element-plus"; // 弹窗
import type { Action } from "element-plus";

import {
  queryByPage as queryByPageForStep,
  insertData as insertDataForStep,
  updateData as updateDataForStep,
  deleteData as deleteDataForStep,
} from "./ApiInfoStep.js"; // 不同页面不同的接口


function addApiInfoStep(data) {
  if (apiInfo.id == 0) { // 如果测试用例没保存，则提示保存
    ElMessageBox.alert("请先保存该测试用例，再添加测试步骤。", "提示", {
      confirmButtonText: "确认保存",
      callback: (action: Action) => {
        // 提交数据
        // onSubmit();
        if (action == "confirm") {
          // 提交之前记得把数组修改为json字符串
          let data = {
            id: apiInfo.id,
            project_id: apiInfo.project_id,
            case_name: apiInfo.case_name,
            case_desc: apiInfo.case_desc,
            param_data: JSON.stringify(apiInfo.param_data),
            pre_request: apiInfo.pre_request, // 执行前事件
            post_request: apiInfo.post_request, // 执行后事件
            // module_id: apiInfo.module_id,
          };
          // 提交数据
          insertData(data).then(
            (res: { data: { data: any; code: number; msg: string } }) => {
              if (res.data.code == 200) {
                data.id = res.data.data.id;
                // 添加成功,刷新数据
                loadData(data.id);
              }
            }
          );
        }
      },
    });
  } else { 
    // 如果是发送请求（send_request）则把当前选择得接口的参数数据回显到变量定义中
    if (tmp_apiCaseStep.keyword.keyword_fun_name == "send_request") {

       // 增加提示：当前接口的变量会写入到当前用例中，请自行手动维护
        ElMessageBox.alert(
          "当前接口的变量会写入到当前用例中，请自行手动维护。",
          "提示",
          {
            confirmButtonText: "知道了",
            type: "info",
            callback: (action) => {
              // 用户点击“知道了”之后继续执行后续逻辑
              console.log("用户已确认");
            }
          }
        );

      // 假设 tmp_apiCaseStep 是你的响应参数对象
        const refVariable = tmp_apiCaseStep.ref_variable;

        // 1. 获取 "_接口信息" 的值，例如 2
        const interfaceId = refVariable["_接口信息"];

        console.log("=======接口ID：=======", interfaceId);

        // 2. 在 dataRequestList 中查找 id === interfaceId 的项
        const matchedRequest = dataRequestList.value.find(
          (item) => item.id === interfaceId
        );

        // 3. 如果找到了对应的接口数据，取出 debug_vars
        if (matchedRequest) {
          const debugVars = matchedRequest.debug_vars;
          console.log("找到的 debug_vars:", debugVars);

          // 可以在这里进行后续操作，比如赋值给其他变量
          // apiInfo.param_data.push(...JSON.parse(debugVars));
          console.log("======apiInfo.param_data:=======", apiInfo.param_data);

          JSON.parse(debugVars).forEach((data, index) => {
          apiInfo.param_data.push(data)
        }
        )
            // 保存当前接口，不然加进去的数据没有了
          onSubmit()
        } else {
          console.warn("未找到对应 ID 的接口信息");
        }
    }
    
    // 如果是新增加测试步骤，则调用新增接口
    var insertStepData = {
      api_case_info_id: apiInfo.id,
      key_word_id: tmp_apiCaseStep.keyword.id,
      step_desc: tmp_apiCaseStep.step_desc,
      ref_variable: JSON.stringify(tmp_apiCaseStep.ref_variable),
      run_order: tmp_apiCaseStep.run_order,
    };
    insertDataForStep(insertStepData).then(
      (res: { data: { code: number; msg: string } }) => {
        // 添加成功,刷新列表
        if (res.data.code == 200) {
          loadData(apiInfo.id);
        }
        // 添加完毕，清除之前的参数内容
        tmp_apiCaseStep.ref_variable = {}
      }
    );
  }
}
// ---------------------END 6.0 添加对应的测试步骤---------------------------



 // --------------------7.0 测试步骤数据回显---------------------------
//  加载对应的测试步骤数据

import {queryAllTree as queryAllTree } from "./ApiInfoStep.js"; // 不同页面不同的接口
// 表格数据
const tableDataCaseStep = ref([]);
// --加载对应的测试步骤方法
function loadCaseStep() { 
     // 加载测试步骤的数据
    let searchData = searchForm;
    searchData["page"] = 1;
    searchData["pageSize"] = 9999;
    searchData["api_case_info_id"] = apiInfo.id;
    const total = ref(0);

    queryAllTree(searchData).then(
    (res: { data: { data: never[]; total: number; msg: string } }) => {
      tableDataCaseStep.value = res.data.data;
      // 把 ref_variable 数据由 json字符串转换为 js 对象
      tableDataCaseStep.value.forEach((step, index) => {
        tableDataCaseStep.value[index]["ref_variable"] = JSON.parse(tableDataCaseStep.value[index]["ref_variable"])
      });
      total.value = res.data.total;
});
 }

// 6-1 点击关联事件
function findKeyWordByName(key_word_name) { // 根据关键字ID查找关键字信息
  console.log("根据NAME查找关键字信息:" + key_word_name)
  var result = {}
  keyWordList.value.forEach((keyword, index) => {
    if (key_word_name == keyword.keyword_fun_name) result = keyword
  });
  return result
}
// 6-2 点击修改对应的数据key_word_id，方便后期修改数据
const onStepKeyModifyChange = (index) => { 
  const foundItemKW = keyWordList.value.find(
    (item) => item.keyword_fun_name === tableDataCaseStep.value[index].value[1]
  );

  console.log("初始的关键字ID",tableDataCaseStep.value[index].key_word_id)
  // 当点击，则把对应的当前点击的ID 给当前值，方便后期修改数据
  tableDataCaseStep.value[index].key_word_id = foundItemKW.id
  console.log("修改后的关键字ID",tableDataCaseStep.value[index].key_word_id)

  findKeyWordByName(tableDataCaseStep.value[index].value[1]).keyword_desc
};

// ---------------------END 7.0 测试步骤数据回显---------------------------


// --------------------8.0 测试步骤删除、修改数据---------------------------

// 当前用例步骤：删除
const onDelete = (id: number) => {
  deleteDataForStep(id).then((res: {}) => {
    // getAppCasePre()
    loadData(apiInfo.id);
  });
};

// 当前用例步骤：修改
function updateAppCaseStep(data) {
  console.log("当前修改步骤的数据为",data)
  updateDataForStep({
    id: data.id,
    app_info_id: data.app_info_id,
    key_word_id: data.key_word_id,
    step_desc: data.step_desc,
    ref_variable: JSON.stringify(data.ref_variable),
    run_order: data.run_order,
  }).then(
    (res: { data: { code: number; msg: string } }) => {
      // 添加成功,刷新列表
      if (res.data.code == 200) {
        loadData(apiInfo.id);
      }
    }
  );
}
// --------------------END 8.0 测试步骤删除、修改数据---------------------------


// --------------------9.0 测试执行用例---------------------------
import { excuteTest } from "./ApiInfoCase.js"; // 不同页面不同的接口
const okExecuteTest = () => {
  //  当没有数据则提示用户
  if (apiInfo.id < 1) {
    ElMessage.error("请添加用例数据并保存");
    return;
  }
  
  //  加载当前测试用例的数据
  let searchData = reactive({});
  searchData["id"] = apiInfo.id;
  
  // 执行测试用例-调用接口
  // 成功则打开页面
  ElMessage.success("开始执行测试用例");

  excuteTest(searchData).then((res: {}) => {
    window.open(import.meta.env.VITE_APP_API_URL+"/ApiReportViewer/" + res.data.data.report_id + "/index.html", '_blank');
  });
};

// --------------------END 9.0 测试执行用例---------------------------


import { queryByPage as queryByPageList } from "../project/DbBaseManage.js"; // 不同页面不同的接口

// TODO 拓展 加载数据库
const databaseList = ref([]);
const loadDatabaseInfos = async () => {
  let searchData = {};
  searchData["project_id"] = apiInfo.project_id;
  searchData["page"] = 1;
  searchData["pageSize"] = 99999; // 理论无限大
    
  // 搜索条件，启动的数据
  searchData["is_enabled"] = "1";
  queryByPageList(searchData).then(
      (res: { data: { data: never[]; total: number; msg: string } }) => {
        console.log("-------数据库信息查询返回值------", res.data.data);
        databaseList.value = [] // 清空已有的数据库信息
        databaseList.value.push(...res.data.data); // 重新放置新的项目数据库信息
      }
    );
}
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

/* ---------------------调整当前用例步骤的样式--------------------- */
.input-group .el-input {
  width: 180px;
  /* 根据需要调整间隔大小 */
  margin-left: 10px;
}

.input-group .el-button {
  width: 120px;
  /* 根据需要调整间隔大小 */
  margin-left: 10px;
}

.el-table__expanded-cell {
  background-color: beige;
}
</style>