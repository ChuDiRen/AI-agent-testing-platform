<template>
  <div class="page-container">
    <el-card class="page-card">
      <template #header>
        <div class="card-header">
          <h3>{{ formTitle }}</h3>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="form-content"
      >
        <el-form-item label="机器人类型" prop="robot_type">
          <el-select v-model="formData.robot_type" placeholder="请选择机器人类型" style="width: 100%">
            <el-option label="企业微信" value="wechat">
              <span style="float: left">企业微信</span>
              <span style="float: right; color: #8492a6; font-size: 13px">推荐</span>
            </el-option>
            <el-option label="钉钉" value="dingtalk">
              <span style="float: left">钉钉</span>
              <span style="float: right; color: #8492a6; font-size: 13px">需要密钥</span>
            </el-option>
            <el-option label="飞书" value="feishu">
              <span style="float: left">飞书</span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="机器人名称" prop="robot_name">
          <el-input
            v-model="formData.robot_name"
            placeholder="请输入机器人名称，如：测试通知机器人"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="Webhook地址" prop="webhook_url">
          <el-input
            v-model="formData.webhook_url"
            type="textarea"
            :rows="3"
            placeholder="请输入Webhook地址，如：https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx"
            maxlength="500"
            show-word-limit
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>从机器人管理后台获取Webhook地址</span>
          </div>
        </el-form-item>

        <el-form-item 
          v-if="formData.robot_type === 'dingtalk'" 
          label="密钥" 
          prop="secret_key"
        >
          <el-input
            v-model="formData.secret_key"
            placeholder="请输入钉钉机器人密钥（加签密钥）"
            maxlength="255"
            show-word-limit
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>钉钉机器人需要配置加签密钥以确保安全</span>
          </div>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入机器人描述信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="是否启用" prop="is_enabled">
          <el-switch
            v-model="formData.is_enabled"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="onSubmit" :loading="submitLoading">
            <el-icon><Check /></el-icon>
            保存
          </el-button>
          <el-button @click="onTest" :loading="testLoading" :disabled="!canTest">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
          <el-button @click="onReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
          <el-button @click="goBack">
            <el-icon><Back /></el-icon>
            取消
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { InfoFilled, Check, Connection, RefreshLeft, Back } from '@element-plus/icons-vue';
import { useRouter, useRoute } from 'vue-router';
import { queryById, insertData, updateData, testConnection } from './robotConfig.js';

const router = useRouter();
const route = useRoute();
const formRef = ref(null);

// 表单数据
const formData = reactive({
  id: null,
  robot_type: 'wechat',
  robot_name: '',
  webhook_url: '',
  secret_key: '',
  description: '',
  is_enabled: true
});

// 表单标题
const formTitle = computed(() => {
  return formData.id ? '编辑机器人配置' : '新增机器人配置';
});

// 是否可以测试
const canTest = computed(() => {
  return formData.robot_name && formData.webhook_url;
});

// 加载状态
const submitLoading = ref(false);
const testLoading = ref(false);

// 表单验证规则
const rules = {
  robot_type: [
    { required: true, message: '请选择机器人类型', trigger: 'change' }
  ],
  robot_name: [
    { required: true, message: '请输入机器人名称', trigger: 'blur' },
    { min: 2, max: 255, message: '长度在 2 到 255 个字符', trigger: 'blur' }
  ],
  webhook_url: [
    { required: true, message: '请输入Webhook地址', trigger: 'blur' },
    { type: 'url', message: '请输入正确的URL格式', trigger: 'blur' }
  ],
  secret_key: [
    { 
      validator: (rule, value, callback) => {
        if (formData.robot_type === 'dingtalk' && !value) {
          callback(new Error('钉钉机器人需要配置密钥'));
        } else {
          callback();
        }
      }, 
      trigger: 'blur' 
    }
  ]
};

// 加载数据
const loadData = () => {
  const id = route.query.id;
  if (id) {
    queryById(id).then(res => {
      if (res.data.code === 200 && res.data.data) {
        Object.assign(formData, res.data.data);
      } else {
        ElMessage.error(res.data.msg || '加载数据失败');
      }
    }).catch(error => {
      console.error('加载数据失败:', error);
      ElMessage.error('加载数据失败，请稍后重试');
    });
  }
};

// 提交表单
const onSubmit = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      submitLoading.value = true;
      const apiCall = formData.id ? updateData(formData) : insertData(formData);
      
      apiCall.then(res => {
        submitLoading.value = false;
        if (res.data.code === 200) {
          ElMessage.success(formData.id ? '修改成功' : '添加成功');
          setTimeout(() => {
            goBack();
          }, 500);
        } else {
          ElMessage.error(res.data.msg || '操作失败');
        }
      }).catch(error => {
        submitLoading.value = false;
        console.error('提交失败:', error);
        ElMessage.error('操作失败，请稍后重试');
      });
    } else {
      ElMessage.warning('请填写必填项');
      return false;
    }
  });
};

// 测试连接
const onTest = () => {
  if (!canTest.value) {
    ElMessage.warning('请先填写机器人名称和Webhook地址');
    return;
  }

  testLoading.value = true;
  
  // 如果是新增，先保存再测试
  if (!formData.id) {
    formRef.value.validate((valid) => {
      if (valid) {
        insertData(formData).then(res => {
          if (res.data.code === 200) {
            formData.id = res.data.data.id;
            performTest();
          } else {
            testLoading.value = false;
            ElMessage.error(res.data.msg || '保存失败，无法测试');
          }
        }).catch(error => {
          testLoading.value = false;
          console.error('保存失败:', error);
          ElMessage.error('保存失败，请稍后重试');
        });
      } else {
        testLoading.value = false;
        ElMessage.warning('请填写必填项');
      }
    });
  } else {
    performTest();
  }
};

// 执行测试
const performTest = () => {
  testConnection({
    robot_id: formData.id,
    test_message: `【测试消息】来自 ${formData.robot_name}\n\n这是一条测试消息，用于验证机器人配置是否正确。\n\n发送时间：${new Date().toLocaleString()}`
  }).then(res => {
    testLoading.value = false;
    if (res.data.code === 200) {
      const result = res.data.data;
      ElMessage.success({
        message: `连接测试成功！\n响应时间: ${result.response_time}ms`,
        duration: 3000
      });
    } else {
      ElMessage.error(res.data.msg || '测试失败');
    }
  }).catch(error => {
    testLoading.value = false;
    console.error('测试失败:', error);
    ElMessage.error('测试失败，请检查配置是否正确');
  });
};

// 重置表单
const onReset = () => {
  formRef.value.resetFields();
};

// 返回列表
const goBack = () => {
  router.push('/RobotConfigList');
};

// 初始化
onMounted(() => {
  loadData();
});
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-card {
  border-radius: 8px;
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.form-content {
  padding: 20px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
}

.form-tip .el-icon {
  font-size: 14px;
}
</style>
