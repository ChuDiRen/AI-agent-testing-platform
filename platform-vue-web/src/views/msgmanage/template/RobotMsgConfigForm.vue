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
        <el-form-item label="选择机器人" prop="robot_id">
          <el-select 
            v-model="formData.robot_id" 
            placeholder="请选择机器人" 
            style="width: 100%"
            filterable
            @change="onRobotChange"
          >
            <el-option
              v-for="robot in robotList"
              :key="robot.id"
              :label="`${robot.robot_name} (${getRobotTypeName(robot.robot_type)})`"
              :value="robot.id"
            >
              <span style="float: left">{{ robot.robot_name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ getRobotTypeName(robot.robot_type) }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="消息类型" prop="msg_type">
          <el-radio-group v-model="formData.msg_type">
            <el-radio value="text">文本消息</el-radio>
            <el-radio value="markdown">Markdown</el-radio>
            <el-radio value="card">卡片消息</el-radio>
          </el-radio-group>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>不同机器人类型支持的消息格式可能不同</span>
          </div>
        </el-form-item>

        <el-form-item label="模板名称" prop="template_name">
          <el-input
            v-model="formData.template_name"
            placeholder="请输入模板名称，如：测试完成通知"
            maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="模板内容" prop="template_content">
          <el-input
            v-model="formData.template_content"
            type="textarea"
            :rows="12"
            :placeholder="getContentPlaceholder()"
            show-word-limit
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>使用 &#123;&#123;变量名&#125;&#125; 格式定义变量，如：&#123;&#123;test_name&#125;&#125;</span>
          </div>
        </el-form-item>

        <el-form-item label="变量说明" prop="variables">
          <el-input
            v-model="formData.variables"
            type="textarea"
            :rows="6"
            placeholder='请输入变量说明（JSON格式），例如：{"test_name": "测试名称", "test_result": "测试结果"}'
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>用于说明模板中使用的变量及其含义</span>
          </div>
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入模板描述信息"
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
          <el-button type="success" @click="onPreview">
            <el-icon><View /></el-icon>
            预览
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

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="模板预览" width="700px">
      <div class="preview-container">
        <el-alert
          title="模板信息"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <div><strong>模板名称：</strong>{{ formData.template_name || '未命名' }}</div>
          <div><strong>消息类型：</strong>{{ getMsgTypeName(formData.msg_type) }}</div>
          <div><strong>关联机器人：</strong>{{ selectedRobotName }}</div>
        </el-alert>

        <el-divider content-position="left">模板内容</el-divider>
        <div class="preview-content">
          <pre>{{ formData.template_content || '（无内容）' }}</pre>
        </div>

        <el-divider content-position="left">变量说明</el-divider>
        <div class="preview-variables">
          <pre>{{ formData.variables || '（无变量）' }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { InfoFilled, Check, View, RefreshLeft, Back } from '@element-plus/icons-vue';
import { useRouter, useRoute } from 'vue-router';
import { queryById, insertData, updateData } from './robotMsgConfig.js';
import { queryAll as queryAllRobots } from '~/views/msgmanage/robot/robotConfig.js';

const router = useRouter();
const route = useRoute();
const formRef = ref(null);

// 表单数据
const formData = reactive({
  id: null,
  robot_id: null,
  msg_type: 'text',
  template_name: '',
  template_content: '',
  variables: '',
  description: '',
  is_enabled: true
});

// 机器人列表
const robotList = ref([]);
const selectedRobotName = ref('');

// 表单标题
const formTitle = computed(() => {
  return formData.id ? '编辑消息模板' : '新增消息模板';
});

// 加载状态
const submitLoading = ref(false);
const previewVisible = ref(false);

// 表单验证规则
const rules = {
  robot_id: [
    { required: true, message: '请选择机器人', trigger: 'change' }
  ],
  msg_type: [
    { required: true, message: '请选择消息类型', trigger: 'change' }
  ],
  template_name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' },
    { min: 2, max: 255, message: '长度在 2 到 255 个字符', trigger: 'blur' }
  ],
  template_content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' }
  ]
};

// 加载机器人列表
const loadRobots = () => {
  queryAllRobots().then(res => {
    if (res.data.code === 200) {
      robotList.value = res.data.data || [];
    }
  }).catch(error => {
    console.error('加载机器人列表失败:', error);
  });
};

// 加载数据
const loadData = () => {
  const id = route.query.id;
  if (id) {
    queryById(id).then(res => {
      if (res.data.code === 200 && res.data.data) {
        Object.assign(formData, res.data.data);
        updateSelectedRobotName();
      } else {
        ElMessage.error(res.data.msg || '加载数据失败');
      }
    }).catch(error => {
      console.error('加载数据失败:', error);
      ElMessage.error('加载数据失败，请稍后重试');
    });
  }
};

// 机器人改变
const onRobotChange = () => {
  updateSelectedRobotName();
};

// 更新选中的机器人名称
const updateSelectedRobotName = () => {
  const robot = robotList.value.find(r => r.id === formData.robot_id);
  selectedRobotName.value = robot ? robot.robot_name : '';
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

// 预览
const onPreview = () => {
  if (!formData.template_name) {
    ElMessage.warning('请先填写模板名称');
    return;
  }
  if (!formData.template_content) {
    ElMessage.warning('请先填写模板内容');
    return;
  }
  previewVisible.value = true;
};

// 重置表单
const onReset = () => {
  formRef.value.resetFields();
};

// 返回列表
const goBack = () => {
  router.push('/RobotMsgConfigList');
};

// 获取内容占位符
const getContentPlaceholder = () => {
  const placeholders = {
    text: '请输入文本消息内容，例如：\n\n测试通知\n\n测试名称：{{test_name}}\n测试结果：{{test_result}}\n执行时间：{{test_time}}',
    markdown: '请输入Markdown格式内容，例如：\n\n# 测试通知\n\n**测试名称**：{{test_name}}\n**测试结果**：{{test_result}}\n**执行时间**：{{test_time}}',
    card: '请输入卡片消息JSON内容，例如：\n\n{\n  "title": "测试通知",\n  "text": "测试名称：{{test_name}}\\n测试结果：{{test_result}}"\n}'
  };
  return placeholders[formData.msg_type] || '请输入模板内容';
};

// 辅助方法
const getRobotTypeName = (type) => {
  const map = {
    wechat: '企业微信',
    dingtalk: '钉钉',
    feishu: '飞书'
  };
  return map[type] || type;
};

const getMsgTypeName = (type) => {
  const map = {
    text: '文本消息',
    markdown: 'Markdown',
    card: '卡片消息'
  };
  return map[type] || type;
};

// 初始化
onMounted(() => {
  loadRobots();
  loadData();
});
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.page-card {
  border-radius: 8px;
  max-width: 900px;
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

.preview-container {
  padding: 10px;
}

.preview-content,
.preview-variables {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.preview-content pre,
.preview-variables pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
