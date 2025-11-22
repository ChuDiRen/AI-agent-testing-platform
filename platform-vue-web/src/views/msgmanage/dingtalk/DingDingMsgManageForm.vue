<template>
  <div class="form-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h3>{{ ruleForm.id > 0 ? '编辑钉钉机器人' : '新增钉钉机器人' }}</h3>
        </div>
      </template>

      <el-form 
        ref="ruleFormRef" 
        :model="ruleForm" 
        :rules="rules" 
        label-width="120px" 
        class="demo-ruleForm" 
        status-icon
      >
        <el-form-item label="配置编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>

        <el-form-item label="机器人名称" prop="robot_name">
          <el-input 
            v-model="ruleForm.robot_name" 
            placeholder="请输入机器人名称，如：测试通知机器人" 
          />
        </el-form-item>

        <el-form-item label="Webhook地址" prop="webhook_url">
          <el-input 
            v-model="ruleForm.webhook_url" 
            type="textarea"
            :rows="3"
            placeholder="请输入钉钉机器人Webhook地址" 
          />
        </el-form-item>

        <el-form-item label="密钥" prop="secret_key">
          <el-input 
            v-model="ruleForm.secret_key" 
            placeholder="请输入密钥(加签必填)" 
            show-password
          />
          <span class="form-tip">钉钉机器人安全设置为"加签"时必填</span>
        </el-form-item>

        <el-form-item label="是否启用" prop="is_enabled">
          <el-switch 
            v-model="ruleForm.is_enabled"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
          <el-button @click="resetForm(ruleFormRef)">清空</el-button>
          <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue";
import type { FormInstance, FormRules } from 'element-plus';
import { useRouter } from "vue-router";
import { ElMessage } from 'element-plus';
import { queryById, insertData, updateData } from './dingtalk.js';

const router = useRouter();

// 表单实例
const ruleFormRef = ref<FormInstance>();

// 表单数据
const ruleForm = reactive({
  id: 0,
  robot_type: 'dingtalk',  // 固定为钉钉
  robot_name: '',
  webhook_url: '',
  secret_key: '',
  is_enabled: true
});

// 表单验证规则
const rules = reactive<FormRules>({
  robot_name: [
    { required: true, message: '机器人名称为必填项', trigger: 'blur' }
  ],
  webhook_url: [
    { required: true, message: 'Webhook地址为必填项', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ]
});

// 提交表单
const submitForm = async (form: FormInstance | undefined) => {
  if (!form) return;
  await form.validate((valid, fields) => {
    if (!valid) {
      return;
    }
    // 有ID代表是修改，没有ID代表是新增
    if (ruleForm.id > 0) {
      updateData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
        if (res.data.code == 200) {
          ElMessage.success('更新成功');
          router.push('/DingDingMsgManageList');
        } else {
          ElMessage.error(res.data.msg || '更新失败');
        }
      }).catch((error: any) => {
        console.error('更新失败:', error);
        ElMessage.error('更新失败，请稍后重试');
      });
    } else {
      insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
        if (res.data.code == 200) {
          ElMessage.success('新增成功');
          router.push('/DingDingMsgManageList');
        } else {
          ElMessage.error(res.data.msg || '新增失败');
        }
      }).catch((error: any) => {
        console.error('新增失败:', error);
        ElMessage.error('新增失败，请稍后重试');
      });
    }
  });
};

// 重置表单
const resetForm = (form: FormInstance | undefined) => {
  if (!form) return;
  form.resetFields();
};

// 关闭表单 - 回到数据列表页
const closeForm = () => {
  router.push('/DingDingMsgManageList');
};

// 加载表单数据
const loadData = async (id: number) => {
  const res = await queryById(id);
  ruleForm.id = res.data.data.id;
  ruleForm.robot_type = res.data.data.robot_type;
  ruleForm.robot_name = res.data.data.robot_name;
  ruleForm.webhook_url = res.data.data.webhook_url;
  ruleForm.secret_key = res.data.data.secret_key;
  ruleForm.is_enabled = res.data.data.is_enabled;
};

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id;
ruleForm.id = query_id ? Number(query_id) : 0;

if (ruleForm.id > 0) {
  loadData(ruleForm.id);
}
</script>

<style scoped>
.form-container {
  padding: 20px;
}

.form-card {
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.demo-ruleForm {
  padding: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 10px;
}
</style>
