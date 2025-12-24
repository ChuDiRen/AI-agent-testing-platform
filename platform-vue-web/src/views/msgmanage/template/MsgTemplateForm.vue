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
        <el-form-item label="模板编码" prop="template_code">
          <el-input
            v-model="formData.template_code"
            placeholder="请输入模板编码，如：VERIFY_CODE_SMS"
            maxlength="50"
            show-word-limit
            :disabled="isEdit"
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>模板编码唯一标识，创建后不可修改</span>
          </div>
        </el-form-item>

        <el-form-item label="模板名称" prop="template_name">
          <el-input
            v-model="formData.template_name"
            placeholder="请输入模板名称，如：短信验证码模板"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="模板类型" prop="template_type">
          <el-select v-model="formData.template_type" placeholder="请选择模板类型" style="width: 100%">
            <el-option
              v-for="type in templateTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="渠道类型" prop="channel_type">
          <el-select v-model="formData.channel_type" placeholder="请选择渠道类型" style="width: 100%">
            <el-option
              v-for="channel in channelTypes"
              :key="channel.value"
              :label="channel.label"
              :value="channel.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="消息标题" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入消息标题（站内消息/邮件使用）"
            maxlength="200"
            show-word-limit
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>站内消息和邮件需要标题，短信和推送不需要</span>
          </div>
        </el-form-item>

        <el-form-item label="模板内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="6"
            placeholder="请输入模板内容，支持变量替换，如：您好 {{userName}}，您的验证码是 {{code}}"
            maxlength="5000"
            show-word-limit
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>使用 {{variableName}} 格式定义变量，下方添加变量后会自动提取</span>
          </div>
        </el-form-item>

        <el-form-item label="模板变量">
          <div class="variables-container">
            <div
              v-for="(variable, index) in formData.variables"
              :key="index"
              class="variable-item"
            >
              <el-input
                v-model="variable.name"
                placeholder="变量名"
                style="width: 150px"
              >
                <template #prepend>{{"{{"}}</template>
                <template #append>{{"}}"}}</template>
              </el-input>
              <el-input
                v-model="variable.desc"
                placeholder="变量描述"
                style="width: 200px"
              />
              <el-input
                v-model="variable.default_value"
                placeholder="默认值（可选）"
                style="flex: 1"
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="removeVariable(index)"
              />
            </div>
            <el-button
              type="primary"
              :icon="Plus"
              @click="addVariable"
              plain
              style="width: 100%"
            >
              添加变量
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="示例参数">
          <el-input
            v-model="exampleParamsJson"
            type="textarea"
            :rows="4"
            placeholder='请输入示例参数JSON，用于预览模板效果，如：{"code": "123456", "userName": "张三"}'
            @blur="validateExampleParams"
          />
          <div class="form-tip">
            <el-icon><InfoFilled /></el            >
            <span>示例参数用于模板预览，需包含所有定义的变量</span>
          </div>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="formData.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>

        <el-form-item label="备注" prop="remark">
          <el-input
            v-model="formData.remark"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item>
          <el-space>
            <el-button type="primary" @click="onSubmit" :loading="submitLoading">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
            <el-button @click="onPreview" :loading="previewLoading">
              <el-icon><View /></el-icon>
              预览效果
            </el-button>
            <el-button @click="onReset">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
            <el-button @click="goBack">
              <el-icon><Back /></el-icon>
              取消
            </el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="模板预览"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="标题">
          <div class="preview-content">{{ previewData.title }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="内容">
          <pre class="preview-content">{{ previewData.content }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  InfoFilled,
  Check,
  View,
  RefreshLeft,
  Back,
  Plus,
  Delete
} from '@element-plus/icons-vue';
import { useRouter, useRoute } from 'vue-router';
import {
  queryById,
  insertData,
  updateData,
  previewTemplate,
  getTemplateTypes,
  getChannelTypes
} from './template.js';

const router = useRouter();
const route = useRoute();

// 是否为编辑模式
const isEdit = computed(() => !!route.query.id);

// 表单标题
const formTitle = computed(() => isEdit.value ? '编辑消息模板' : '新增消息模板');

// 表单引用
const formRef = ref(null);

// 表单数据
const formData = reactive({
  template_code: '',
  template_name: '',
  template_type: '',
  channel_type: '',
  title: '',
  content: '',
  variables: [],
  status: 1,
  remark: ''
});

// 示例参数 JSON 字符串
const exampleParamsJson = ref('{}');

// 提交加载状态
const submitLoading = ref(false);

// 预览相关
const previewVisible = ref(false);
const previewLoading = ref(false);
const previewData = ref({
  title: '',
  content: ''
});

// 模板类型和渠道类型
const templateTypes = ref([]);
const channelTypes = ref([]);

// 表单验证规则
const rules = {
  template_code: [
    { required: true, message: '请输入模板编码', trigger: 'blur' },
    { pattern: /^[A-Z0-9_]+$/, message: '模板编码只能包含大写字母、数字和下划线', trigger: 'blur' }
  ],
  template_name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  template_type: [
    { required: true, message: '请选择模板类型', trigger: 'change' }
  ],
  channel_type: [
    { required: true, message: '请选择渠道类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入模板内容', trigger: 'blur' }
  ]
};

// 加载类型和渠道数据
const loadTypesAndChannels = async () => {
  try {
    const [typesRes, channelsRes] = await Promise.all([
      getTemplateTypes(),
      getChannelTypes()
    ]);

    if (typesRes.data.code === 200) {
      templateTypes.value = typesRes.data.data || [];
    }
    if (channelsRes.data.code === 200) {
      channelTypes.value = channelsRes.data.data || [];
    }
  } catch (error) {
    console.error('加载类型数据失败:', error);
  }
};

// 加载模板详情（编辑模式）
const loadTemplateDetail = async () => {
  if (!route.query.id) return;

  try {
    const res = await queryById(route.query.id);
    if (res.data.code === 200) {
      const data = res.data.data;
      Object.assign(formData, {
        template_code: data.template_code,
        template_name: data.template_name,
        template_type: data.template_type,
        channel_type: data.channel_type,
        title: data.title,
        content: data.content,
        variables: data.variables || [],
        status: data.status,
        remark: data.remark
      });
      exampleParamsJson.value = JSON.stringify(data.example_params || {}, null, 2);
    } else {
      ElMessage.error(res.data.msg || '加载失败');
      goBack();
    }
  } catch (error) {
    console.error('加载模板详情失败:', error);
    ElMessage.error('加载失败，请稍后重试');
    goBack();
  }
};

// 添加变量
const addVariable = () => {
  formData.variables.push({
    name: '',
    desc: '',
    default_value: ''
  });
};

// 删除变量
const removeVariable = (index) => {
  formData.variables.splice(index, 1);
};

// 验证示例参数
const validateExampleParams = () => {
  try {
    JSON.parse(exampleParamsJson.value);
  } catch (error) {
    ElMessage.warning('示例参数JSON格式不正确');
  }
};

// 提交表单
const onSubmit = async () => {
  try {
    await formRef.value.validate();

    // 验证示例参数
    let exampleParams = {};
    try {
      exampleParams = JSON.parse(exampleParamsJson.value || '{}');
    } catch (error) {
      ElMessage.error('示例参数JSON格式不正确');
      return;
    }

    // 验证变量定义
    const invalidVariables = formData.variables.filter(v => !v.name);
    if (invalidVariables.length > 0) {
      ElMessage.error('请完善变量定义（变量名不能为空）');
      return;
    }

    submitLoading.value = true;

    const submitData = {
      ...formData,
      example_params: exampleParams
    };

    let res;
    if (isEdit.value) {
      submitData.id = parseInt(route.query.id);
      res = await updateData(submitData);
    } else {
      res = await insertData(submitData);
    }

    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '新增成功');
      goBack();
    } else {
      ElMessage.error(res.data.msg || '操作失败');
    }
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error);
      ElMessage.error('操作失败，请稍后重试');
    }
  } finally {
    submitLoading.value = false;
  }
};

// 预览模板
const onPreview = async () => {
  try {
    await formRef.value.validate(['template_code', 'content']);

    previewLoading.value = true;

    let exampleParams = {};
    try {
      exampleParams = JSON.parse(exampleParamsJson.value || '{}');
    } catch (error) {
      exampleParams = {};
    }

    const res = await previewTemplate({
      template_code: formData.template_code,
      params: exampleParams
    });

    if (res.data.code === 200) {
      previewData.value = res.data.data;
      previewVisible.value = true;
    } else {
      ElMessage.error(res.data.msg || '预览失败');
    }
  } catch (error) {
    if (error !== false) {
      console.error('预览失败:', error);
      ElMessage.error('预览失败，请稍后重试');
    }
  } finally {
    previewLoading.value = false;
  }
};

// 重置表单
const onReset = () => {
  formRef.value.resetFields();
  formData.variables = [];
  exampleParamsJson.value = '{}';
};

// 返回列表
const goBack = () => {
  router.back();
};

// 初始化
onMounted(() => {
  loadTypesAndChannels();
  loadTemplateDetail();
});
</script>

<style scoped>
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

.form-content {
  max-width: 800px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.variables-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.variable-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.preview-content {
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 300px;
  overflow-y: auto;
}
</style>
