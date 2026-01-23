<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
     
      <el-form-item label="项目编号" prop="id">
        <el-input v-model="ruleForm.id" disabled />
      </el-form-item>
      
      <el-form-item label="是否启动" prop="is_enabled">
        <el-radio-group v-model="ruleForm.is_enabled" class="ml-4">
        <el-radio value="true" size="large">启动</el-radio>
        <el-radio value="false" size="large">不启动</el-radio>
        </el-radio-group>
      </el-form-item>
  
      <el-form-item label="所属操作类型ID" prop="operation_type_id">
      <el-select v-model="ruleForm.operation_type_id" placeholder="选择关键字类型" clearable filterable>
      <el-option v-for="operationType in operationTypeList" :key="operationType.id" :label="operationType.operation_type_name" :value="operationType.id"/>     
      </el-select>
      </el-form-item>
  
      <el-form-item label="关键字名称" prop="name">
        <el-input v-model="ruleForm.name" placeholder="关键字名称"/>
      </el-form-item>
  
      <el-form-item label="关键字方法名" prop="keyword_fun_name">
        <el-input v-model="ruleForm.keyword_fun_name" placeholder="英文的方法名，如果您填写代码体，需要和代码体的类名一致" />
      </el-form-item>
  
  
      <el-form-item label="" prop="keyword_value">
        <el-tabs class="demo-tabs" v-model="tabActiveName" style="width: 1120px">
        <!-- 第一个Tab，维护对应的代码提 -->
        <el-tab-pane label="代码体" name="代码体">
          <!-- 1-1 多行文本框 -->
          <el-input v-model="ruleForm.keyword_value" :rows="15" type="textarea" placeholder="请输入对应的代码体，可生成对应的关键字"/>
          <el-button  @click="code_example">生成示例代码</el-button>
          <!-- 1-2 代码示例按钮 -->
        </el-tab-pane>
         <!-- END -- 第一个Tab，维护对应的代码提 -->

                 <!-- 第二个Tab，维护对应的变量描述 -->
        <el-tab-pane label="变量描述" name="变量描述">
          <!-- 2-1 变量描述的数据显示部分 -->
          <el-table  :data="ruleForm.keyword_desc"   class="table_data"   max-height="250" >
          <el-table-column prop="name" label="变量名" style="width: 40%" />
          <el-table-column prop="placeholder" label="变量描述" style="width: 40%" />
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
          <el-input v-model="vars.name" placeholder="变量名" style="width: 30%"  />
          <el-input v-model="vars.placeholder" placeholder="变量描述" style="width: 30%"  />
          <el-button style="width: 30%" @click="onAddVars">添加</el-button>
          </div>
        </el-tab-pane>
        <!-- END 第二个Tab，维护对应的变量描述 -->

        </el-tabs>  
      </el-form-item>
  
  
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
        <el-button type="primary" @click="keywordFile(ruleFormRef)">生成关键字文件</el-button>
        <el-button @click="resetForm(ruleFormRef)">清空</el-button>
        <el-button type="primary" @click="closeForm(ruleFormRef)">关闭</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
  
  <script setup>
  import { ref, reactive } from "vue";
  import { queryById, insertData, updateData } from './ApiKeyWord.js'; // 不同页面不同的接口
  import { useRouter } from "vue-router";
  import Breadcrumb from "../../Breadcrumb.vue";
  const router = useRouter();
  
  
  // 表单实例
  const ruleFormRef = ref();
  
  // 表单数据
  const ruleForm = reactive({
    id: 0,
    name: "",
    keyword_desc: [],
    keyword_fun_name: '',
    keyword_value: '',
    operation_type_id: '',
    is_enabled: 'true'
  });
  
  
  import { queryAll } from "./ApiOperationType.js"; // 不同页面不同的接口
  const operationTypeList = ref([{
  id: 0,
  operation_type_name: '',
  create_time: ''
  }]);
  function getOperationTypeList() {
  queryAll().then((res) => {
    operationTypeList.value = res.data.data;
  });
  }
  getOperationTypeList();
  
  
  // 表单验证规则
  const rules = reactive({
    name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    keyword_fun_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    is_enabled: [
      { required: true, message: '必填项', trigger: 'blur' }
    ]
  });
  
  // 提交表单
  const submitForm = async (form) => {
    if (!form) return;
    await form.validate((valid, fields) => {
      if (!valid) {
        return;
      }
      // 有ID代表是修改，没有ID代表是新增
      if (ruleForm.id > 0) {
        updateData({
          id: ruleForm.id,
          name: ruleForm.name,
          keyword_desc: JSON.stringify(ruleForm.keyword_desc),
          keyword_fun_name: ruleForm.keyword_fun_name,
          keyword_value: ruleForm.keyword_value,
          operation_type_id: ruleForm.operation_type_id,
          is_enabled: ruleForm.is_enabled
        }).then((res) => {
          if (res.data.code == 200) {
            router.push('/ApikeywordList'); // 跳转回列表页面
          }
        });
      } else {
        insertData({
          id: ruleForm.id,
          name: ruleForm.name,
          keyword_desc: JSON.stringify(ruleForm.keyword_desc),
          keyword_fun_name: ruleForm.keyword_fun_name,
          keyword_value: ruleForm.keyword_value,
          operation_type_id: ruleForm.operation_type_id,
          is_enabled: ruleForm.is_enabled
        }).then((res) => {
          console.log(res)
          if (res.data.code == 200) {
            router.push('/ApikeywordList'); // 跳转回列表页面
          }
        });
      }
    });
  };
  
  // 重置表单
  const resetForm = (form) => {
    if (!form) return;
    form.resetFields();
  };
  
  // 关闭表单 - 回到数据列表页
  const closeForm = () => {
    router.back();
  };
  
  // 加载表单数据
  const loadData = async (id) => {
    const res = await queryById(id);
    ruleForm.id = res.data.data.id;
    ruleForm.name = res.data.data.name;
    ruleForm.keyword_desc = JSON.parse(res.data.data.keyword_desc);
    ruleForm.operation_type_id = res.data.data.operation_type_id;
    ruleForm.keyword_fun_name = res.data.data.keyword_fun_name;
    ruleForm.keyword_value = res.data.data.keyword_value;
    ruleForm.is_enabled = res.data.data.is_enabled;
  };
  
  // 如果有id参数，说明是编辑，需要获取数据
  let query_id = router.currentRoute.value.query.id;
  ruleForm.id = query_id ? Number(query_id) : 0;
  if (ruleForm.id > 0) {
    loadData(ruleForm.id);
  }
  
  // 默认设置选择的tab页面
  const tabActiveName = ref("代码体");
  

  
//  --------------扩展功能： 增加示例代码 -------
const code_example = () => {
let code = `# -*- coding: UTF-8 -*-
# --示例代码--请根据需要编写
from apprun.core.globalContext import g_context # 引入全局变量

class assert_title: # class名称 必须与关键字名称一致
def __init__(self,driver:appdriver): # 这里不用动，获取浏览器驱动的
  self.driver = driver

# 新增关键字: title断言
def assert_title(self, **kwargs): # 方法名称 必须与关键字名称一致
  # kwargs 是你要从外部接收的参数，可以理解为一个字典
  # 1. 按需引入相关依赖包（如果是平台本身没有的，记得在平台上进行相关的安装 pip install ）
  # from selenium.appdriver.common.by import By
  # 2. 编写具体关键字内容
  assert EC.title_is(kwargs['数据内容')(self.driver)
`;
ruleForm.keyword_value = code;
};
//  --------------END 扩展功能： 增加示例代码 -------


// ----------------------扩展功能： 关键字变量定义---------------------------
const vars = reactive({
name: "",
placeholder: "",
});

const deleteVars = (index) => {
  // splice() 方法可以在任意位置修改数组,并返回被删除的元素 （下标,个数）
ruleForm.keyword_desc.splice(index, 1);
};

const onAddVars = () => {
// 保存起来
ruleForm.keyword_desc.push({
  name: vars.name,
  placeholder: vars.placeholder,
});
// 置空
vars.name = "";
vars.placeholder = "";
};
// ----------------------END 扩展功能： 关键字变量定义---------------------------


// ---------------------- 扩展功能：生成关键字文件方法---------------------------
import {keywordFile as generateFile } from './ApiKeyWord.js'; // 不同页面不同的接口

const keywordFile = async (form) => {
  if (!form) return;
  await form.validate((valid, fields) => {
    if (!valid) {
      return;
    }
    // 有ID代表是则代表是直接生成
    if (ruleForm.id > 0) {
      generateFile(ruleForm).then((res) => { });
    } else {
      //  先插入数据再生成文件
      insertData({
        id: ruleForm.id,
        name: ruleForm.name,
        keyword_desc: JSON.stringify(ruleForm.keyword_desc),
        keyword_fun_name: ruleForm.keyword_fun_name,
        keyword_value: ruleForm.keyword_value,
        operation_type_id: ruleForm.operation_type_id,
        is_enabled: ruleForm.is_enabled
      }).then((res) => {
        if (res.data.code == 200) {
          generateFile(ruleForm).then((res) => { });
        }
      });
    }
  });
};
// ---------------------- END 扩展功能：生成关键字文件方法---------------------------

  </script>
  