<template>
  <div>
     <!-- 面包屑导航 -->
   <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
      <el-form-item label="机器人ID" prop="id">
        <el-input v-model="ruleForm.id" disabled />
      </el-form-item>
      <el-form-item label="机器人别名" prop="robot_name"  >
        <el-input v-model="ruleForm.robot_name" placeholder="请机器人名称"/>
      </el-form-item>
      <el-form-item label="机器人URL" prop="webhook_url"  >
        <el-input v-model="ruleForm.webhook_url" placeholder="机器人WebHook URL" />
      </el-form-item>
      <el-form-item label="安全参数" prop="keywords" >
        <el-input v-model="ruleForm.keywords" placeholder="请输入安全参数" />
      </el-form-item>
      <el-form-item>
        <el-row :rows="20">
            <el-col :span="17">
              <el-input
                v-model="ruleForm.message_template"
                type="textarea"
                :rows="15"
                placeholder="请选择你要发送的消息模板,如:${status} 表示本次测试通过情况 ,${report_url}表示本次报告地址 ,${coll_name}表示本次用例名"
              />
            </el-col>
            <el-col :span="1" />
            <el-col :span="6">
              <el-link
                href="https://hctestedu.com"
                target="_blank"
                type="danger"
                style="width: 100%"
                >消息体情况说明</el-link
              >
              <el-link
                type="success"
                style="width: 100%"
                @click="msg_json1"
                >消息体模板1</el-link
              >
              <el-link
                type="success"
                style="width: 100%"
                @click="msg_json2"
                >消息体模板2</el-link
              >
          
            </el-col>
          </el-row>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
        <el-button @click="resetForm(ruleFormRef)">清空</el-button>
        <el-button @click="closeForm()">关闭</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
  
  <script setup>
  import { ref, reactive } from "vue";
  import { queryById, insertData, updateData } from './RobotConfig.js'; // 不同页面不同的接口
  import Breadcrumb from "../Breadcrumb.vue";
  import { useRouter } from "vue-router";
  
  const router = useRouter();
  
  // 1. 表单实例
  const ruleFormRef = ref();
  
  // 2. 表单数据
  const ruleForm = reactive({
    id: 0,
    robot_name: '',
    robot_type: 2,  // 钉钉机器人类型，1：企业微信，2：钉钉人，3：飞书
    webhook_url: '',
    keywords: '',
    message_template: ''
  });
  
  // 3. 表单验证规则
  const rules = reactive<any>({
    robot_name: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    webhook_url: [
      { required: true, message: '必填项', trigger: 'blur' }
    ],
    message_template:[
      { required: true, message: '必填项', trigger: 'blur' }
    ]
  });
  
  // 4. 提交表单
  const submitForm = async (form) => {
    if (!form) return;
    await form.validate((valid, fields) => {
      if (!valid) {
        return;
      }
      // 有ID代表是修改，没有ID代表是新增
      if (ruleForm.id > 0) {
        updateData(ruleForm).then((res) => {
          if (res.data.code == 200) {
            router.push('/DingDingMsgManageList'); // 跳转回列表页面
          }
        });
      } else {
        insertData(ruleForm).then((res) => {
          console.log(res)
          if (res.data.code == 200) {
            router.push('/DingDingMsgManageList'); // 跳转回列表页面
          }
        });
      }
    });
  };
  
  // 5. 重置表单
  const resetForm = (form) => {
    if (!form) return;
    form.resetFields();
  };
  
  // 6. 关闭表单 - 回到数据列表页
  const closeForm = () => {
    router.back();
  };
  
  // 7. 加载表单数据
  const loadData = async (id) => {
    const res = await queryById(id);
    ruleForm.id = res.data.data.id;
    ruleForm.robot_name = res.data.data.robot_name;
    ruleForm.webhook_url = res.data.data.webhook_url;
    ruleForm.keywords = res.data.data.keywords;
    ruleForm.message_template = res.data.data.message_template;
  };
  
  // 8. 如果有id参数，说明是编辑，需要获取数据
  let query_id = router.currentRoute.value.query.id;
  ruleForm.id = query_id ? Number(query_id) : 0;

  if (ruleForm.id > 0) {
    loadData(ruleForm.id);
  }

  const msg_json1 = () => {
  ruleForm.message_template = "本次测试结果为：{{status}}\n\n[查看报告]({{report_url}})\n\n[查看项目]({{coll_name}})";
}

const msg_json2 = () => {
  ruleForm.message_template = "测试结果通知：测试名称 {{coll_name}} \n\n 测试结果 : {{status}}\n\n[报告地址]({{report_url}})\n\n备注：温馨提示：点击报告地址可查看详细测试数据";
}
  
  </script>
  