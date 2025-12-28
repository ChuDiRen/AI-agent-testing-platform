<template>
  <!-- 模块1 ： 头部的按钮和标题 -->
  <div class="form-wrapper">
    <div class="form-info">| API测试计划</div>
    <el-form-item class="form-buttons">
      <el-button type="primary" @click="submitForm(ruleFormRef)">
        保存
      </el-button>
      <el-button @click="closeForm()">关闭</el-button>
    </el-form-item>
  </div>

  <!-- 模块2：主题内容信息 -->
  <el-form ref="ruleFormRef" :model="apicollection" :rules="rules" :inline="true" class="demo-form-inline">
  <!-- 模块2-1 -- 基础信息维护 -->
  <el-form-item label="测试计划名称：" prop="collection_name">
      <el-input v-model="apicollection.collection_name"  style="width: 480px"/>
    </el-form-item>
    <el-form-item label="所属项目：" prop="id">
      <el-select v-model="apicollection.project_id" placeholder="选择所属项目" clearable filterable>
        <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
      </el-select>
    </el-form-item>
    <el-form-item label="测试计划描述：" prop="collection_desc" >
      <el-input v-model="apicollection.collection_desc"  style="width: 480px"/>
    </el-form-item>
   <!--模块2-2 -- 用例信息\运行配置信息\其它等等维护 -->
  <el-form-item label="">
      <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 1120px">
        <el-tab-pane label="用例维护" name="用例维护">
          <!-- TAB1 -- 用例维护的位置 -->
           <!-- 用例维护的位置 -->
          <el-table :data="tableDataCaseInfo"  row-key="id" style="width: 100%">
              <el-table-column fixed="left" label="操作" width="180">
                  <template #default="scope">
                    <el-button link type="primary" size="small" @click.prevent="editCaseParamData(scope.$index)">
                        确认修改
                    </el-button>
                    <el-button link type="primary" size="small" @click.prevent="deleteApiCases(scope.$index)">
                        删除
                    </el-button>
                  </template>
              </el-table-column>
              <el-table-column prop="run_order" label="顺序" width="120" >
                  <template #default="scope">
                    <!-- <el-input style="width: 50px" v-model="scope.row.run_order" placeholder="顺序-数字类型"/> -->
                    <el-input-number v-model="scope.row.run_order" :min="1" style="width: 107px" controls-position="right" placeholder="顺序"/>
                  </template>
              </el-table-column>
              <el-table-column prop="case_name" label="用例名称" :show-overflow-tooltip="true" />
              <el-table-column prop="param_data" label="变量依赖说明" :show-overflow-tooltip="true" />
              <el-table-column prop="ddt_param_data" label="DDT数据驱动" type="expand" width="120"
                              style="background-color: darksalmon;">
                  <!--可以到时候为一个用例设置多组不同的数据 -->
                  <template #default="case_scope">
                    <!-- 位置1 : 输入描述名称,添加数据 -->
                    <el-input v-model="temp_desc" placeholder="desc参数-测试数据组标题" style="width: 40%;margin-left: 10px;" />
                    <el-button style="width: 15%;margin-left: 10px;" @click="onAddDdtParamsGroup(case_scope.$index)">添加一组数据</el-button>
                    <!-- END 位置1 : 输入描述名称,添加数据 -->

                   <!-- 位置2 : 添加对应的数据显示位置 -->
<el-collapse style="margin-top: 10px;">
    <el-collapse-item 
      v-for="(ddt_data, ddt_data_index) in case_scope.row.ddt_param_data" 
      :key="ddt_data_index" 
      :name="ddt_data_index"
    >
    <!-- 显示对应的标题 -->
      <template #title>
        <div style="vertical-align: middle;" class="chapters_style_1">
          <el-button  style="margin-left: 10px; " @click="onDeleteDdtParamsGroup(case_scope.$index, ddt_data_index)">删除</el-button>
          <span style="margin-left: 10px; "> 第 {{ddt_data_index + 1}} 组 : {{ ddt_data[0].value }}</span>
        </div>
      </template>
     <!-- END 显示对应的标题 -->
     
        <!-- 显示变量的位置 -->
        <el-table :data="ddt_data" class="table_data" max-height="250">
          <el-table-column prop="key" label="变量名" style="width: 40%" >
            <template #default="ddt_data_scope">
              <el-input v-model="ddt_data_scope.row.key" placeholder="变量名称"></el-input>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="变量值" style="width: 40%" >
            <template #default="ddt_data_scope">
              <el-input v-model="ddt_data_scope.row.value" placeholder="变量值"></el-input>
            </template>
          </el-table-column>
          <el-table-column fixed="right" label="删除" style="width: 15%">
            <template #default="ddt_data_scope">
              <el-button link type="primary" size="small" @click.prevent="deleteDdtParams(case_scope.$index,ddt_data_index, ddt_data_scope.$index)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table> 
        <!-- END 显示变量的位置 -->

        <!-- 添加变量的位置 -->
        <div class="input-group">
          <el-input v-model="temp_ddt_params.key" placeholder="变量名" style="width: 40%" />
          <el-input v-model="temp_ddt_params.value" placeholder="变量值" style="width: 40%" />
          <el-button style="width: 15%" @click="onAddDdtParams(case_scope.$index,ddt_data_index)">添加</el-button>
        </div>
        <!-- END 添加变量的位置 -->
      </el-collapse-item>
    </el-collapse>
    <!-- END 位置2 : 添加对应的数据显示位置 -->
                  </template>
                  <!--END 可以到时候为一个用例设置多组不同的数据 -->
              </el-table-column>
          </el-table>
           <!-- END 用例维护的位置 -->
            <!-- 添加用例位置 -->
            <el-button type="primary" link @click="shoApiInfosDialog" style="margin-top: 20px;"> + 添加用例</el-button>
            <!-- END 添加用例位置 -->
        </el-tab-pane>
        <el-tab-pane label="运行环境配置" name="运行环境配置">
          <!-- TAB2 -- 运行环境配置 -->

          <!-- 全局变量的显示 -->
          <el-divider content-position="center">全局环境变量</el-divider>
          <el-table :data="apicollection.collection_env" class="table_data" max-height="250">
            <el-table-column prop="key" label="变量名" style="width: 40%" />
            <el-table-column prop="value" label="变量值" style="width: 40%" />
            <el-table-column fixed="right" label="删除" style="width: 15%">
              <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="deleteVars(scope.$index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <!-- END全局变量的显示 -->
          <!-- 全局变量的添加 -->
          <div class="input-group">
            <el-input v-model="vars.key" placeholder="变量名" style="width: 40%" />
            <el-input v-model="vars.value" placeholder="变量值" style="width: 40%" />
            <el-button style="width: 15%" @click="onAddVars">添加</el-button>
          </div>
           <!-- END 全局变量的添加 -->
        </el-tab-pane>

         <!-- Jenkins配置的添加  -->
        <el-tab-pane label="Jenkins环境配置" name="Jenkins环境配置">
          <el-divider content-position="center">配置说明</el-divider>
          <el-text class="mx-1" type="danger" style="margin-bottom: 20px;">如果您需要进行CICD，在Jenkins配置请求当前的接口即可。配置的信息内容如下：</el-text>
          <p> <el-tag type="primary" style="margin-left: 20px;width: 100px;">PATH：</el-tag> <el-tag type="info" style="margin-left: 20px;">/ApiCollectionInfo/excuteTest</el-tag></p>
          <p> <el-tag type="primary" style="margin-left: 20px;width: 100px;">请求头：</el-tag><el-tag type="info" style="margin-left: 20px;">Content-Type: application/json</el-tag></p>
          <p> <el-tag type="primary" style="margin-left: 20px;width: 100px;">请求方法：</el-tag><el-tag type="info" style="margin-left: 20px;">POST</el-tag></p>
          <p> <el-tag type="primary" style="margin-left: 20px;width: 100px;">请求参数：</el-tag><el-tag type="info" style="margin-left: 20px;" v-model="JenkinsInfo"> {"id":{{JenkinsInfo}}}</el-tag></p>
        </el-tab-pane>
         <!-- END Jenkins配置的添加  -->


         
         <!-- 机器人通知配置  -->
        <el-tab-pane label="机器人通知配置" name="机器人通知配置">
          <!-- 机器人显示 -->
            <!-- 机器人列表表格 -->
          <el-table :data="robotsList" style="width: 100%">
            <el-table-column prop="id" label="编号"/>
            <el-table-column prop="robot_name" label="机器人别名" />
            <el-table-column prop="robot_type" label="机器人类型">
              <template #default="scope">
                {{ getRobotTypeLabel(scope.row.robot_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="is_enabled" label="是否启用">
              <template #default="scope">
                <el-switch 
                  v-model="scope.row.is_enabled" 
                  :active-value="1" 
                  :inactive-value="0" 
                  @change="toggleRobotStatus(scope.row)" 
                />
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" width="100">
              <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="deleteRobot(scope.row.id)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 机器人添加 -->
          <!-- 添加机器人链接 -->
          <el-button type="primary" link @click="showAddRobotDialog">+ 添加机器人</el-button>

           <!-- 添加机器人弹窗 -->
          <el-dialog v-model="addRobotDialogVisible" title="添加机器人">
            <!-- 弹窗的搜索条件 -->
          <el-form-item label="机器人别名：" style="margin-left: 10px; margin-right: 10px; ">
            <el-input v-model="searchRobotName" placeholder="根据机器人别名筛选" clearable style="width: 200px; display: inline-block; vertical-align: middle;" />
            <el-button type="primary" @click="loadRobots()" style="margin-left: 10px; vertical-align: middle;">查询</el-button>
          </el-form-item>
            <!-- END 弹窗的搜索条件 -->
           <el-divider></el-divider>
            <!-- 显示对应的所有数据 -->
            <el-table :data="availableRobotsList" style="width: 100%">
              <el-table-column prop="robot_name" label="机器人别名" />
              <el-table-column prop="robot_type" label="机器人类型">
                <template #default="scope">
                  {{ getRobotTypeLabel(scope.row.robot_type) }}
                </template>
              </el-table-column>
              <el-table-column fixed="right" label="操作" width="100">
                <template #default="scope">
                  <el-button type="primary" size="small" @click.prevent="addRobot(scope.$index)">
                    添加
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <!-- END显示对应的所有数据 -->

            <!-- 分页控件 -->
            <div class="demo-pagination-block">
              <el-pagination 
                v-model:current-page="currentPage" 
                v-model:page-size="pageSize" 
                :page-sizes="[5, 10, 20, 30, 50]"
                layout="total, sizes, prev, pager, next, jumper" 
                :total="totalRobots" 
                @size-change="handleSizeChanged"
                @current-change="handleCurrentChanged" />
            </div>
            <!-- END 分页控件 -->
          </el-dialog>

        </el-tab-pane>
         <!-- END 机器人通知配置  -->


      </el-tabs>
    </el-form-item>
   <!--END 模块2-2 -- 用例信息\运行配置信息\其它等等维护 -->
  </el-form>
  
  <!-- 弹窗 - 弹窗加载用例列表 -->
  <el-dialog v-model="infoDialogFormVisible" title="添加用例">
    <!-- 弹窗的搜索条件 -->
    <el-form-item label="项目名称：" style="margin-left: 10px; margin-right: 10px">
      <el-select v-model="searchForm.project_id" placeholder="根据项目名称筛选" clearable filterable style="width: 200px">
        <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
      </el-select>
      <el-form-item label="API用例名称：" style="margin-left: 10px; margin-right: 10px">
        <el-input v-model="searchForm.case_name" placeholder="根据API用例名称筛选" clearable />
      </el-form-item>
      <el-button type="primary" @click="loadApiInfos()">查询</el-button>
    </el-form-item>
    <!-- END 弹窗的搜索条件 -->

    <!-- 显示对应的所有数据 -->
    <el-table :data="apiInfoList" style="width: 100%">
      <el-table-column prop="id" label="用例编号" style="width: 5%" />
      <el-table-column prop="case_name" label="用例名称" style="width: 30%" :show-overflow-tooltip="true" />
      <el-table-column prop="case_desc" label="用例描述" style="width: 60%" :show-overflow-tooltip="true" />
      <el-table-column fixed="right" label="操作" style="width: 5%">
        <template #default="scope">
          <el-button type="primary" size="small" @click.prevent="addApiInfo(scope.$index)">
            添加
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <!-- END显示对应的所有数据 -->

     <!-- 分页 -->
        <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination 
        v-model:current-page= "currentApiInfoPage" 
        v-model:page-size= "apiInfoPageSize" 
        :page-sizes="[5, 10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper" 
        :total="apiInfoTotal" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
       </div>
    <!-- END 分页 -->
  </el-dialog>
  <!-- END 弹窗 - 弹窗加载用例列表 -->
  <div></div>

</template>

<script lang="ts" setup>
import { ref, reactive } from "vue";
import { queryById, insertData, updateData } from "./ApiCollectionInfo.js"; // 不同页面不同的接口
import { ElMessage, type FormInstance, type FormRules } from "element-plus";
import { useRouter } from "vue-router";
const router = useRouter();


// 表单实例
const ruleFormRef = ref<FormInstance>();

// 表单数据 - 不同的页面，不同的表单字段
const apicollection = reactive({
  id: 0,
  project_id: "请选择项目",
  devices_id: 0,
  collection_name: "",
  collection_desc: "",
  collection_env: [] as any[],
  collection_params: [] as any[]
});

// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive<any>({
  project_id: [{ required: true, message: "必填项", trigger: "blur" }],
  collection_name: [{ required: true, message: "必填项", trigger: "blur" }],
  collection_desc: [{ required: true, message: "必填项", trigger: "blur" }],
});


// 提交表单
const submitForm = async (form: FormInstance | undefined) => {
  // 1. 校验表单 2.提交集合基础信息 3.提交用例信息
  if (!form) return;
  
  if (apicollection.project_id == "请选择项目") {
    ElMessage.error("请选择项目");
    return;
  }

  await form.validate((valid, fields) => {
    if (!valid) {
      return;
    }
    var collection_data = {
      id: apicollection.id,
      project_id: apicollection.project_id,
      collection_name: apicollection.collection_name,
      collection_desc: apicollection.collection_desc,
      collection_env: JSON.stringify(apicollection.collection_env)
    }
    // 有ID 代表是修改， 没ID 代表是新增
    if (apicollection.id > 0) {
      updateData(collection_data).then(
        (res: { data: { code: number; msg: string } }) => {
          if (res.data.code == 200) {
            // router.push("/ApiCollectionList"); // 跳转回列表页面 - 不同的页面，不同的路径
          }
        }
      );
    } else {
      insertData(collection_data).then(
        (res: { data: { code: number; msg: string } }) => {
          if (res.data.code == 200) {
            // router.push("/ApiCollectionList"); // 跳转回列表页面 - 不同的页面，不同的路径
            loadData(res.data.data.id);
          }
        }
      );
    }
  });
};

// 关闭表单 - 回到数据列表页 - 不同的页面，不同的路径
const closeForm = () => {
  router.push("/ApiCollectionInfoList");
};

const JenkinsInfo=  ref("")
// 加载表单数据
const loadData = async (id: number) => {
  const res = await queryById(id);
  // 不同的页面，不同的表单字段 (注意这里的res.data.data.xxx，xxx是接口返回的字段，不同的接口，字段不同)
  apicollection.id = res.data.data.id;
  apicollection.project_id = res.data.data.project_id;
  apicollection.collection_name = res.data.data.collection_name;
  apicollection.collection_desc = res.data.data.collection_desc;
  apicollection.collection_env = JSON.parse(res.data.data.collection_env);

  // 加载测试用例数据
  getApiCaseInfo()

  // 初始化ID的值
  JenkinsInfo.value = res.data.data.id;

  // 加载机器人数据 
  loadMsgRobots()

};

// 如果有id参数，说明是编辑，需要获取数据
console.log(router);
let query_id = router.currentRoute.value.query.id;
apicollection.id = query_id ? Number(query_id) : 0;

if (apicollection.id > 0) {
  loadData(apicollection.id);
}

// 如果有其他逻辑，请添加
// 1. 加载项目
import { queryAllProject } from "../project/ApiProject.js"; // 不同页面不同的接口
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


// ---------------------功能1: Tab页面默认选择---------------------------
const tabActiveName = ref("用例维护"); // tab页
// ---------------------功能2: 全局变量的显示和添加---------------------------
const vars = reactive({
  key: "",
  value: "",
});

const deleteVars = (index: number) => {
  apicollection.collection_env.splice(index, 1);
};

const onAddVars = () => {
  // 保存起来
  apicollection.collection_env.push({
    key: vars.key,
    value: vars.value,
  });
  // 置空
  vars.key = "";
  vars.value = "";
};
// ---------------------END 功能2: 全局变量的显示和添加---------------------------

// ---------------------功能3: 获取当前用例列表---------------------------
import {
  queryByPage as queryByPageForDetail,
  insertData as insertDataForDetail,
  updateData as updateDataForDetail,
  deleteData as deleteDataForDetail,
} from "./ApiCollectionDetail.js"; // 不同页面不同的接口
const searchForm = reactive({ "project_id": '', "case_name": '' })// 搜索
const tableDataCaseInfo = ref([]);

function getApiCaseInfo() {
  let searchData = searchForm;
  searchData["page"] = 1;
  searchData["pageSize"] = 9999;
  searchData["collection_info_id"] = apicollection.id;
  const total = ref(0);

  queryByPageForDetail(searchData).then(
    (res: { data: { data: never[]; total: number; msg: string } }) => {
      tableDataCaseInfo.value = res.data.data;
      // json字符串转 js对象
      tableDataCaseInfo.value.forEach((item, index) => {
      tableDataCaseInfo.value[index]["ddt_param_data"] = JSON.parse(tableDataCaseInfo.value[index]["ddt_param_data"])
      });
      total.value = res.data.total;
    }
  );
}
// ---------------------END 功能3: 获取当前用例列表---------------------------

// ---------------------功能4: 删除用例列表---------------------------
// 
const deleteApiCases = (index: number) => {
  deleteDataForDetail(tableDataCaseInfo.value[index]["id"]).then((res: {}) => {
  getApiCaseInfo() // 重新加载列表
  })
};
// ---------------------END 功能4: 删除用例列表---------------------------

// ---------------------功能5: 显示弹窗相关的数据---------------------------
// 显示弹窗的点击事件
import { ElMessageBox } from 'element-plus' // 弹窗
import type { Action } from 'element-plus'


const infoDialogFormVisible = ref(false) // 是否展示弹窗

function shoApiInfosDialog() {
  // 如果是新建集合,提示将自动保存,获取到ID之后再进行用例关联
  if (apicollection.id == 0) {
    ElMessageBox.alert("该操作，将自动【保存】该测试用例", "提示", {
      // if you want to disable its autofocus
      // autofocus: false,
      confirmButtonText: "我已知晓,继续",
      callback: (action: Action) => {
        if (action == "confirm") {
          // 提交之前记得把数组修改为json字符串
          var collection_data = {
            id: apicollection.id,
            project_id: apicollection.project_id,
            devices_id: apicollection.devices_id,
            collection_name: apicollection.collection_name,
            collection_desc: apicollection.collection_desc,
            collection_env: JSON.stringify(apicollection.collection_env)
          }
          // 提交数据
          insertData(collection_data).then(
            (res: { data: { data: any; code: number; msg: string } }) => {
              if (res.data.code == 200) {
                infoDialogFormVisible.value = true;
                loadData(res.data.data.id);
                // 打开页面的同时加载当前测试用例页面的数据
                // loadAppInfos()
              }
            }
          );
        }
      },
    });
  } else {
    infoDialogFormVisible.value = true;
      // 打开页面的同时加载当前测试用例页面的数据
    loadApiInfos()
  }
}
// ---------------------END 功能5: 显示弹窗相关的数据---------------------------



// -------6-2 分页相关的-----
const apiInfoPageSize = ref(5); // 每页大小
const apiInfoTotal = ref(0);  // 总数
const currentApiInfoPage = ref(1) // 页码


// 变更页大小
const handleSizeChange = (val: number) => {
    console.log("页大小变化:" + val)
    apiInfoPageSize.value = val
    loadApiInfos()
}

// 变更页码
const handleCurrentChange = (val: number) => {
    console.log("页码变化:" + val)
    currentApiInfoPage.value = val
    loadApiInfos()
}
// -------END 分页相关的-----


// -------6-3 显示当前的数据-------
import { queryByPage as queryApiInfoByPage } from "../apiinfocase/ApiInfoCase.js"; // 不同页面不同的接口

const apiInfoList = ref([] as any[]); // 关联的用例

function loadApiInfos() {
  let searchData = searchForm;
  searchData["page"] = currentApiInfoPage.value;
  searchData["pageSize"] = apiInfoPageSize.value;
   queryApiInfoByPage(searchData).then(
    (res: { data: { data: never[]; total: number; msg: string } }) => {
      console.log(res.data.data);
      apiInfoList.value = res.data.data;
      apiInfoTotal.value = res.data.total;
    }
  );
}
// -------END 6-3 显示当前的数据-------


// -------6-4 添加当前的数据到对应的测试计划当中-------
function addApiInfo(index: number) {
  // console.log("当前点击的CASE",appInfoList.value[index])

  let InsertData = {
    collection_info_id: apicollection.id,
    api_case_info_id: apiInfoList.value[index].id,
    ddt_param_data: JSON.stringify([]),
    run_order: 1,
  };

  insertDataForDetail(InsertData).then(
    (res: { data: { code: number; msg: string } }) => {
      // 添加成功,刷新列表
      if (res.data.code == 200) {
        // 重新加载一下前置用例，并且及时刷新页面
        getApiCaseInfo()
        loadData(apicollection.id);
      }
    }
  );
}
// -------END 6-4 添加当前的数据到对应的测试计划当中-------


// ---------------------功能7: 增删改查DDT相关的数据---------------------------
// 1. 临时存储 数据变量
const temp_ddt_params = reactive([]); 

// 2. 保存一组数据
const temp_desc = ref("") // 临时存储 数据描述
const onAddDdtParamsGroup = (case_index: number, ) => {
  // 获取用例需要的参数
  let case_param_data = JSON.parse(tableDataCaseInfo.value[case_index].param_data)
  // 插入元素到指定位置-标题
  case_param_data.splice(0, 0, {
    "key": "desc",
    "value": temp_desc.value
  })
  console.log("当前的参数为：",case_param_data)
  // 插入到 测试计划的指定用例中
  tableDataCaseInfo.value[case_index].ddt_param_data.push(reactive(case_param_data))
  // 清空 desc 内容
  temp_desc.value=""
  console.log("当前的所有数据为",tableDataCaseInfo.value)
  // 所以我们就可以通过下标获取对应的数据
  // console.log(tableDataCaseInfo.value[0]["ddt_param_data"])
}
// ---------------------END 功能7: 增删改查DDT相关的数据---------------------------


// 3. 删除一组数据
const onDeleteDdtParamsGroup =(case_scope_index, ddt_data_index) => {
  // case_scope_index 哪一条用例 ddt_data_index 第几组 
  tableDataCaseInfo.value[case_scope_index].ddt_param_data.splice(ddt_data_index, 1);
}

// 4.删除某个变量
const deleteDdtParams = (case_scope_index: number, ddt_data_index: number, row: number) => {
  // case_scope_index 哪一条用例 ddt_data_index 第几组  row 第几个变量
  tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index].splice(row, 1);
};

// 5.添加某个变量
const onAddDdtParams = (case_scope_index, ddt_data_index) => {
  // case_scope_index 哪一条用例 ddt_data_index 第几组 
  // 保存起来
  tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index].push({
    key: temp_ddt_params.key,
    value: temp_ddt_params.value,
  });
  // 置空
  temp_ddt_params.key = "";
  temp_ddt_params.value = "";
};

// 6. 确认修改一组数据 
import { updateData as updateApiCaseCol } from "./ApiCollectionDetail.js"; // 不同页面不同的接口

const editCaseParamData = (index: number) => {
  // 修改运行参数与执行顺序
  updateApiCaseCol({
    "id": tableDataCaseInfo.value[index].id,
    "ddt_param_data": JSON.stringify(tableDataCaseInfo.value[index].ddt_param_data),
    "run_order": tableDataCaseInfo.value[index].run_order
  }).then((res: { data: { code: number; msg: string; }; }) => {
    if (res.data.code == 200) {
      console.log("用例执行信息修改成功")
    }
  })
};



// ---------------------------扩展： 机器人添加-------------------------------
const robotsList = ref([]); // 机器人数据
const totalRobots = ref(0); // 总数

import {queryByPage as querymsgrobots} from "./apiRobotMsg.js"
// 分页查询 robot 
function loadMsgRobots() {
  const data = {
    coll_id: query_id,
    coll_type:"api" // 固定传当前的测试用例集合类型
  }
   querymsgrobots(data).then((res) => {
    console.log("查询到msg表格数据",res.data.data)
    robotsList.value = res.data.data;
    totalRobots.value = res.data.total;
  })
}


// 机器人类型
function getRobotTypeLabel(type) {
  console.log("type的值为：", type);
  if (type === "1" || type === 1) {
    return '企业微信';
  } else if (type === "2" || type === 2) {
    return '钉钉';
  } else if (type === "3" || type === 3) {
    return '飞书';
  } else {
    return '未知';
  }
}

// 删除机器人
import {deleteData as deleteRobotById} from './apiRobotMsg.js'
// 删除机器人
const deleteRobot = (index: number) => {
  console.log(index);
  deleteRobotById(index).then((res: {}) => { 
    console.log("机器人删除成功");
    loadMsgRobots()
  });
  robotsList.value.splice(index, 1);
};



// 机器人弹窗显示
const addRobotDialogVisible = ref(false);

// 分页相关数据
const currentPage = ref(1); // 当前页码
const pageSize = ref(5); // 每页大小
// 显示添加机器人弹窗
function showAddRobotDialog() {
  // 如果是新建集合,提示将自动保存,获取到ID之后再进行用例关联
    if (apicollection.id == 0) {
      if (apicollection.project_id == '请选择项目') {
      ElMessage.error('请选择对应的项目');
      return;
    } 

    ElMessageBox.alert("该操作，将自动【保存】该测试用例", "提示", {
      // if you want to disable its autofocus
      // autofocus: false,
      confirmButtonText: "我已知晓,继续",
      callback: (action: Action) => {
        if (action == "confirm") {
          // 提交之前记得把数组修改为json字符串
          var collection_data = {
            id: apicollection.id,
            project_id: apicollection.project_id,
            // browser_id: apicollection.browser_id,
            collection_name: apicollection.collection_name,
            collection_desc: apicollection.collection_desc,
            collection_env: JSON.stringify(apicollection.collection_env)
          }

          // 提交数据
          insertData(collection_data).then(
            (res: { data: { data: any; code: number; msg: string } }) => {
              if (res.data.code == 200) {
                query_id = res.data.data.id
                
                addRobotDialogVisible.value = true;
                // 打开页面的同时加载当前页面的数据
                // loadApiInfos()
                loadData(res.data.data.id);
              }
            }
          );
        }
      },
    });
  } else {
    // 打开页面的同时加载当前页面的数据
    addRobotDialogVisible.value = true;
    loadRobots();
  }
}


//  查询可用机器人
import {queryByRobtPage} from "./ApiRobotMsg.js"
const availableRobotsList = ref([]);
const searchRobotName = ref("");

const loadRobots = () => {
  console.log("查询可用机器人")
  const searchData = {
    coll_type: "api",
    coll_id: query_id,
    page: currentPage.value,
    pageSize: pageSize.value,
    robot_name: searchRobotName.value
  };
  queryByRobtPage(searchData).then((res) => {
    console.log(res.data.data)
    availableRobotsList.value = res.data.data;
    totalRobots.value = res.data.total;
  });
};


// 添加机器人操作
import { insertData as insertRobot } from "./apiRobotMsg.js";
// 添加机器人
const addRobot = (index: number) => {
  const robotToAdd = availableRobotsList.value[index];
  console.log("添加机器人",robotToAdd)
  let msgRobot = {
    "robot_name": robotToAdd.robot_name,
    "robot_type": robotToAdd.robot_type,
    "coll_id": query_id,
     "robot_id": robotToAdd.id,
     "coll_type":"api",
    "is_enabled": "1"
  }
  insertRobot(msgRobot).then((res) => {
    console.log(res.data.data)
    loadMsgRobots()
  });
  availableRobotsList.value.splice(index, 1);
};


// 更改启用状态
import { updateData as updateRobot } from "./apiRobotMsg.js";
const toggleRobotStatus = (row) => {
  // 这里可以添加更新机器人状态的逻辑
  console.log('机器人状态变更:', row.id, '状态:', row.is_enabled);
  // 例如调用API更新状态
  updateRobot({
    "id": row.id,
    "is_enabled": row.is_enabled
  }).then((res) => {
    console.log(res.data.data)
    loadMsgRobots()
  });
};


</script>

<style>
.el-divider__text{
  background-color: unset;
}

.el-collapse-item__header{
  background-color: beige;
}
</style>