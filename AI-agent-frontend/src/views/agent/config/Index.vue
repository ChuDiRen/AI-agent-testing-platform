<template>
  <div class="agent-config-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>AI代理配置</span>
          <el-button type="primary" @click="handleSaveConfig">保存配置</el-button>
        </div>
      </template>
      
      <el-form :model="configForm" label-width="120px" :rules="rules" ref="configFormRef">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基础配置" name="basic">
            <el-form-item label="代理名称" prop="name">
              <el-input v-model="configForm.name" placeholder="请输入代理名称" />
            </el-form-item>
            
            <el-form-item label="代理类型" prop="type">
              <el-select v-model="configForm.type" placeholder="请选择代理类型" style="width: 100%">
                <el-option label="对话型" value="conversation" />
                <el-option label="分析型" value="analysis" />
                <el-option label="开发型" value="development" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="描述" prop="description">
              <el-input v-model="configForm.description" type="textarea" rows="3" placeholder="请输入代理描述" />
            </el-form-item>
            
            <el-form-item label="最大响应时间" prop="maxResponseTime">
              <el-input-number v-model="configForm.maxResponseTime" :min="1" :max="60" />
              <span class="form-item-hint">秒</span>
            </el-form-item>
            
            <el-form-item label="启用状态" prop="enabled">
              <el-switch v-model="configForm.enabled" />
            </el-form-item>
          </el-tab-pane>
          
          <el-tab-pane label="模型配置" name="model">
            <el-form-item label="模型类型" prop="modelType">
              <el-select v-model="configForm.modelType" placeholder="请选择模型类型" style="width: 100%">
                <el-option label="GPT-4" value="gpt4" />
                <el-option label="GPT-3.5" value="gpt35" />
                <el-option label="Claude" value="claude" />
                <el-option label="自定义模型" value="custom" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="温度" prop="temperature">
              <el-slider v-model="configForm.temperature" :min="0" :max="1" :step="0.1" show-stops />
            </el-form-item>
            
            <el-form-item label="最大输出长度" prop="maxTokens">
              <el-input-number v-model="configForm.maxTokens" :min="100" :max="10000" :step="100" />
            </el-form-item>
            
            <el-form-item label="API密钥" prop="apiKey" v-if="configForm.modelType !== 'custom'">
              <el-input v-model="configForm.apiKey" placeholder="请输入API密钥" show-password />
            </el-form-item>
            
            <el-form-item label="自定义端点" prop="endpoint" v-if="configForm.modelType === 'custom'">
              <el-input v-model="configForm.endpoint" placeholder="请输入自定义端点URL" />
            </el-form-item>
          </el-tab-pane>
          
          <el-tab-pane label="知识库配置" name="knowledge">
            <el-form-item label="启用知识库" prop="enableKnowledgeBase">
              <el-switch v-model="configForm.enableKnowledgeBase" />
            </el-form-item>
            
            <template v-if="configForm.enableKnowledgeBase">
              <el-form-item label="知识库类型" prop="knowledgeBaseType">
                <el-select v-model="configForm.knowledgeBaseType" placeholder="请选择知识库类型" style="width: 100%">
                  <el-option label="文档库" value="document" />
                  <el-option label="向量数据库" value="vector" />
                  <el-option label="关系型数据库" value="relational" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="知识库来源" prop="knowledgeBaseSources">
                <el-select
                  v-model="configForm.knowledgeBaseSources"
                  multiple
                  collapse-tags
                  collapse-tags-tooltip
                  placeholder="请选择知识库来源"
                  style="width: 100%"
                >
                  <el-option label="产品文档" value="product_docs" />
                  <el-option label="API文档" value="api_docs" />
                  <el-option label="常见问题" value="faq" />
                  <el-option label="用户手册" value="user_manual" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="更新频率" prop="updateFrequency">
                <el-select v-model="configForm.updateFrequency" placeholder="请选择更新频率" style="width: 100%">
                  <el-option label="实时" value="realtime" />
                  <el-option label="每小时" value="hourly" />
                  <el-option label="每天" value="daily" />
                  <el-option label="每周" value="weekly" />
                  <el-option label="手动" value="manual" />
                </el-select>
              </el-form-item>
            </template>
          </el-tab-pane>
          
          <el-tab-pane label="高级设置" name="advanced">
            <el-form-item label="并发请求数" prop="concurrentRequests">
              <el-input-number v-model="configForm.concurrentRequests" :min="1" :max="100" />
            </el-form-item>
            
            <el-form-item label="重试次数" prop="retryCount">
              <el-input-number v-model="configForm.retryCount" :min="0" :max="5" />
            </el-form-item>
            
            <el-form-item label="超时时间" prop="timeout">
              <el-input-number v-model="configForm.timeout" :min="1" :max="60" />
              <span class="form-item-hint">秒</span>
            </el-form-item>
            
            <el-form-item label="日志级别" prop="logLevel">
              <el-select v-model="configForm.logLevel" placeholder="请选择日志级别" style="width: 100%">
                <el-option label="调试" value="debug" />
                <el-option label="信息" value="info" />
                <el-option label="警告" value="warning" />
                <el-option label="错误" value="error" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="自定义提示词" prop="customPrompt">
              <el-input v-model="configForm.customPrompt" type="textarea" rows="5" placeholder="请输入自定义提示词" />
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// 表单引用
const configFormRef = ref<FormInstance>()

// 当前激活的标签页
const activeTab = ref('basic')

// 表单数据
const configForm = reactive({
  name: '客服助手',
  type: 'conversation',
  description: '处理客户咨询的智能客服',
  maxResponseTime: 10,
  enabled: true,
  
  // 模型配置
  modelType: 'gpt4',
  temperature: 0.7,
  maxTokens: 2000,
  apiKey: '',
  endpoint: '',
  
  // 知识库配置
  enableKnowledgeBase: true,
  knowledgeBaseType: 'document',
  knowledgeBaseSources: ['product_docs', 'faq'],
  updateFrequency: 'daily',
  
  // 高级设置
  concurrentRequests: 5,
  retryCount: 3,
  timeout: 30,
  logLevel: 'info',
  customPrompt: '你是一个专业的客服助手，负责回答用户关于我们产品的问题。请保持礼貌和专业，如果不确定答案，请告知用户你会转接给人工客服。'
})

// 表单验证规则
const rules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入代理名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择代理类型', trigger: 'change' }
  ],
  description: [
    { max: 200, message: '描述不能超过200个字符', trigger: 'blur' }
  ],
  modelType: [
    { required: true, message: '请选择模型类型', trigger: 'change' }
  ],
  apiKey: [
    { required: true, message: '请输入API密钥', trigger: 'blur' }
  ],
  endpoint: [
    { required: true, message: '请输入自定义端点URL', trigger: 'blur' }
  ]
})

// 保存配置
const handleSaveConfig = async () => {
  if (!configFormRef.value) return
  
  await configFormRef.value.validate((valid, fields) => {
    if (valid) {
      ElMessageBox.confirm('确定要保存配置吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }).then(() => {
        ElMessage.success('配置保存成功')
      }).catch(() => {
        ElMessage.info('已取消保存')
      })
    } else {
      console.log('表单验证失败', fields)
    }
  })
}

onMounted(() => {
  // 加载配置数据
})
</script>

<style scoped>
.agent-config-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-item-hint {
  margin-left: 10px;
  color: #909399;
}
</style>