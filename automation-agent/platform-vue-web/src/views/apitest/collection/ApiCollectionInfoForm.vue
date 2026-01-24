<template>
  <div>
  <!-- 模块1 ： 头部的按钮和标题 -->
  <div class="form-wrapper">
    <div class="form-info">| API测试计划</div>
    <el-form-item class="form-buttons">
      <el-button type="primary" @click="closeForm">关闭</el-button>
    </el-form-item>
  </div>

  <!-- 模块2 ： 表单信息 -->
  <el-form ref="ruleFormRef" :model="apicollection" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
    <!-- 模块2-1： 基础信息维护 -->
    <el-form-item label="项目名称" prop="project_id">
      <el-select v-model="apicollection.project_id" placeholder="请选择项目" clearable filterable>
        <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
      </el-select>
    </el-form-item>

    <el-form-item label="集合名称" prop="collection_name">
      <el-input v-model="apicollection.collection_name" placeholder="请输入集合名称" />
    </el-form-item>

    <el-form-item label="集合描述" prop="collection_desc">
      <el-input v-model="apicollection.collection_desc" type="textarea" placeholder="请输入集合描述" />
    </el-form-item>

    <!-- 模块2-2 -- 用例信息\运行配置信息\其它等等维护 -->
    <el-form-item label="">
      <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 1120px">
        <!-- TAB1 -- 用例信息维护 -->
        <el-tab-pane label="用例维护" name="用例维护">
          <!-- 用例维护的位置 -->
          <el-table :data="tableDataCaseInfo" style="width: 100%">
            <el-table-column prop="id" label="编号" style="width: 5%" />
            <el-table-column prop="case_name" label="用例名称" style="width: 30%" :show-overflow-tooltip="true" />
            <el-table-column prop="run_order" label="执行顺序" style="width: 10%">
              <template #default="scope">
                <el-input v-model="scope.row.run_order" placeholder="执行顺序" style="width: 80px" />
              </template>
            </el-table-column>
            <el-table-column prop="ddt_param_data" label="数据驱动" style="width: 40%">
              <template #default="case_scope">
                <el-collapse>
                  <el-collapse-item :title="'数据组: ' + (ddt_data_index + 1)" v-for="(ddt_data, ddt_data_index) in case_scope.row.ddt_param_data" :key="ddt_data_index">
                    <!-- 位置1 : 显示对应的数据 -->
                    <el-table :data="ddt_data" class="table_data" max-height="250">
                      <el-table-column prop="key" label="变量名" style="width: 40%" />
                      <el-table-column prop="value" label="变量值" style="width: 40%" />
                      <el-table-column fixed="right" label="删除" style="width: 15%">
                        <template #default="ddt_data_scope">
                          <el-button link type="primary" size="small" @click.prevent="deleteDdtParams(case_scope.$index,ddt_data_index, ddt_data_scope.$index)">
                            删除
                          </el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                    <!-- 添加变量的位置 -->
                    <div class="input-group">
                      <el-input v-model="temp_ddt_params.key" placeholder="变量名" style="width: 40%" />
                      <el-input v-model="temp_ddt_params.value" placeholder="变量值" style="width: 40%" />
                      <el-button style="width: 15%" @click="onAddDdtParams(case_scope.$index,ddt_data_index)">添加</el-button>
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="操作" style="width: 15%">
              <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="deleteApiCases(scope.$index)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <!-- 添加用例位置 -->
          <el-button type="primary" link @click="shoApiInfosDialog" style="margin-top: 20px;"> + 添加用例</el-button>
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
          <!-- 全局变量的添加 -->
          <div class="input-group">
            <el-input v-model="vars.key" placeholder="变量名" style="width: 40%" />
            <el-input v-model="vars.value" placeholder="变量值" style="width: 40%" />
            <el-button style="width: 15%" @click="onAddVars">添加</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-form-item>
  </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { queryById, insertData, updateData } from "@/api/ApiCollectionInfo";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";

const router = useRouter();

// 表单实例
const ruleFormRef = ref();

// 表单数据
const apicollection = reactive({
  id: 0,
  project_id: "请选择项目",
  devices_id: 0,
  collection_name: "",
  collection_desc: "",
  collection_env: [],
  collection_params: []
});

// 表单验证规则
const rules = reactive({
  project_id: [{ required: true, message: "必填项", trigger: "blur" }],
  collection_name: [{ required: true, message: "必填项", trigger: "blur" }],
  collection_desc: [{ required: true, message: "必填项", trigger: "blur" }],
});

// 提交表单
const submitForm = async (form) => {
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
        (res) => {
          if (res.data.code == 200) {
            // 修改成功
          }
        }
      );
    } else {
      insertData(collection_data).then(
        (res) => {
          if (res.data.code == 200) {
            loadData(res.data.data.id);
          }
        }
      );
    }
  });
};

// 关闭表单 - 回到数据列表页
const closeForm = () => {
  router.back();
};

// 加载表单数据
const loadData = async (id) => {
  const res = await queryById(id);
  apicollection.id = res.data.data.id;
  apicollection.project_id = res.data.data.project_id;
  apicollection.collection_name = res.data.data.collection_name;
  apicollection.collection_desc = res.data.data.collection_desc;
  apicollection.collection_env = JSON.parse(res.data.data.collection_env);
};

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id;
apicollection.id = query_id ? Number(query_id) : 0;

if (apicollection.id > 0) {
  loadData(apicollection.id);
}

// 加载项目
import { queryAllProject } from "@/api/ApiProject";
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

// Tab页面默认选择
const tabActiveName = ref("用例维护");

// 全局变量的显示和添加
const vars = reactive({
  key: "",
  value: "",
});

const deleteVars = (index) => {
  apicollection.collection_env.splice(index, 1);
};

const onAddVars = () => {
  apicollection.collection_env.push({
    key: vars.key,
    value: vars.value,
  });
  vars.key = "";
  vars.value = "";
};

// 获取当前用例列表
import {
  queryByPage as queryByPageForDetail,
  deleteData as deleteDataForDetail,
} from "./ApiCollectionDetail.js";

const searchForm = reactive({ "project_id": '', "case_name": '' });
const tableDataCaseInfo = ref([]);

function getApiCaseInfo() {
  let searchData = searchForm;
  searchData["page"] = 1;
  searchData["pageSize"] = 9999;
  searchData["collection_info_id"] = apicollection.id;
  
  queryByPageForDetail(searchData).then(
    (res) => {
      tableDataCaseInfo.value = res.data.data;
      tableDataCaseInfo.value.forEach((item, index) => {
        tableDataCaseInfo.value[index]["ddt_param_data"] = JSON.parse(tableDataCaseInfo.value[index]["ddt_param_data"])
      });
    }
  );
}

// 删除用例列表
const deleteApiCases = (index) => {
  deleteDataForDetail(tableDataCaseInfo.value[index]["id"]).then((res) => {
    getApiCaseInfo()
  })
};

// 显示弹窗相关的数据
import { ElMessageBox } from 'element-plus';
const infoDialogFormVisible = ref(false);

function shoApiInfosDialog() {
  if (apicollection.id == 0) {
    ElMessageBox.alert("该操作，将自动【保存】该测试用例", "提示", {
      confirmButtonText: "我已知晓,继续",
      callback: (action) => {
        if (action == "confirm") {
          var collection_data = {
            id: apicollection.id,
            project_id: apicollection.project_id,
            devices_id: apicollection.devices_id,
            collection_name: apicollection.collection_name,
            collection_desc: apicollection.collection_desc,
            collection_env: JSON.stringify(apicollection.collection_env)
          }
          insertData(collection_data).then(
            (res) => {
              if (res.data.code == 200) {
                infoDialogFormVisible.value = true;
                loadData(res.data.data.id);
              }
            }
          );
        }
      },
    });
  } else {
    infoDialogFormVisible.value = true;
  }
}

// DDT相关的数据
const temp_ddt_params = reactive([]);
const temp_desc = ref("");

const onAddDdtParamsGroup = (case_index) => {
  let case_param_data = JSON.parse(tableDataCaseInfo.value[case_index].param_data)
  case_param_data.splice(0, 0, {
    "key": "desc",
    "value": temp_desc.value
  })
  tableDataCaseInfo.value[case_index].ddt_param_data.push(reactive(case_param_data))
  temp_desc.value = ""
};

const onDeleteDdtParamsGroup = (case_scope_index, ddt_data_index) => {
  tableDataCaseInfo.value[case_scope_index].ddt_param_data.splice(ddt_data_index, 1);
};

const deleteDdtParams = (case_scope_index, ddt_data_index, row) => {
  tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index].splice(row, 1);
};

const onAddDdtParams = (case_scope_index, ddt_data_index) => {
  tableDataCaseInfo.value[case_scope_index].ddt_param_data[ddt_data_index].push({
    key: temp_ddt_params.key,
    value: temp_ddt_params.value,
  });
  temp_ddt_params.key = "";
  temp_ddt_params.value = "";
};

// 机器人相关
const robotsList = ref([]);
const totalRobots = ref(0);

import {queryByPage as querymsgrobots} from "@/api/ApiRobotMsg";

function loadMsgRobots() {
  const data = {
    coll_id: query_id,
    coll_type:"api"
  }
  querymsgrobots(data).then((res) => {
    robotsList.value = res.data.data;
    totalRobots.value = res.data.total;
  })
}

function getRobotTypeLabel(type) {
  if (!type) {
    return '未知类型';
  }
  if (type === "1" || type === 1) {
    return '企业微信';
  } else if (type === "2" || type === 2) {
    return '钉钉';
  } else if (type === "3" || type === 3) {
    return '飞书';
  } else {
    return '未知类型';
  }
}

import {deleteData as deleteRobotById} from '@/api/ApiRobotMsg';
const deleteRobot = (index) => {
  deleteRobotById(index).then((res) => { 
    loadMsgRobots()
  });
  robotsList.value.splice(index, 1);
};

const addRobotDialogVisible = ref(false);
const currentPage = ref(1);
const pageSize = ref(5);

function showAddRobotDialog() {
  if (apicollection.id == 0) {
    if (apicollection.project_id == '请选择项目') {
      ElMessage.error('请选择对应的项目');
      return;
    }
    ElMessageBox.alert("该操作，将自动【保存】该测试用例", "提示", {
      confirmButtonText: "我已知晓,继续",
      callback: (action) => {
        if (action == "confirm") {
          var collection_data = {
            id: apicollection.id,
            project_id: apicollection.project_id,
            collection_name: apicollection.collection_name,
            collection_desc: apicollection.collection_desc,
            collection_env: JSON.stringify(apicollection.collection_env)
          }
          insertData(collection_data).then(
            (res) => {
              if (res.data.code == 200) {
                query_id = res.data.data.id
                addRobotDialogVisible.value = true;
                loadData(res.data.data.id);
              }
            }
          );
        }
      },
    });
  } else {
    addRobotDialogVisible.value = true;
  }
}

import {queryByRobtPage} from "@/api/ApiRobotMsg";
const availableRobotsList = ref([]);
const searchRobotName = ref("");

const loadRobots = () => {
  const searchData = {
    coll_type: "api",
    coll_id: query_id,
    page: currentPage.value,
    pageSize: pageSize.value,
    robot_name: searchRobotName.value
  };
  queryByRobtPage(searchData).then((res) => {
    availableRobotsList.value = res.data.data;
    totalRobots.value = res.data.total;
  });
};

import { insertData as insertRobot } from "@/api/ApiRobotMsg";
const addRobot = (index) => {
  const robotToAdd = availableRobotsList.value[index];
  let msgRobot = {
    "robot_name": robotToAdd.robot_name,
    "robot_type": robotToAdd.robot_type,
    "coll_id": query_id,
    "robot_id": robotToAdd.id,
    "coll_type":"api",
    "is_enabled": "1"
  }
  insertRobot(msgRobot).then((res) => {
    loadMsgRobots()
  });
  availableRobotsList.value.splice(index, 1);
};

import { updateData as updateRobot } from "@/api/ApiRobotMsg";
const toggleRobotStatus = (row) => {
  updateRobot({
    "id": row.id,
    "is_enabled": row.is_enabled
  }).then((res) => {
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