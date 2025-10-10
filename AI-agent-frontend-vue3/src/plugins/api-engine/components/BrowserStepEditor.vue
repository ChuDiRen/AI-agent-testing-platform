<template>
  <div class="browser-step-editor">
    <div class="step-list">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="step-item"
        :class="{ 'step-active': activeStepIndex === index }"
        @click="setActiveStep(index)"
      >
        <div class="step-header">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-info">
            <div class="step-name">{{ step.step_name || `步骤 ${index + 1}` }}</div>
            <div class="step-type">{{ getStepTypeLabel(step.step_type) }}</div>
          </div>
          <div class="step-actions">
            <el-button size="small" text @click.stop="moveStepUp(index)" :disabled="index === 0">
              <el-icon><ArrowUp /></el-icon>
            </el-button>
            <el-button size="small" text @click.stop="moveStepDown(index)" :disabled="index === steps.length - 1">
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <el-button size="small" text type="danger" @click.stop="removeStep(index)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>

      <!-- 添加步骤按钮 -->
      <div class="add-step-btn" @click="addStep">
        <el-icon><Plus /></el-icon>
        <span>添加步骤</span>
      </div>
    </div>

    <!-- 步骤编辑器 -->
    <div v-if="activeStep" class="step-editor-panel">
      <div class="panel-header">
        <h3>编辑步骤 {{ activeStepIndex + 1 }}</h3>
      </div>

      <el-form :model="activeStep" label-width="120px">
        <el-form-item label="步骤名称" required>
          <el-input v-model="activeStep.step_name" placeholder="请输入步骤名称" />
        </el-form-item>

        <el-form-item label="步骤类型" required>
          <el-select v-model="activeStep.step_type" placeholder="选择步骤类型" @change="handleStepTypeChange">
            <el-option-group label="导航操作">
              <el-option label="打开页面" value="navigate" />
            </el-option-group>
            <el-option-group label="交互操作">
              <el-option label="点击元素" value="click" />
              <el-option label="输入文本" value="input" />
              <el-option label="选择选项" value="select_option" />
              <el-option label="悬停" value="hover" />
              <el-option label="拖拽" value="drag" />
            </el-option-group>
            <el-option-group label="等待操作">
              <el-option label="等待元素" value="wait" />
              <el-option label="等待时间" value="sleep" />
            </el-option-group>
            <el-option-group label="验证操作">
              <el-option label="验证元素" value="validate" />
              <el-option label="验证文本" value="assert_text" />
              <el-option label="验证标题" value="assert_title" />
            </el-option-group>
            <el-option-group label="其他操作">
              <el-option label="截图" value="screenshot" />
              <el-option label="执行脚本" value="execute_script" />
              <el-option label="切换框架" value="switch_frame" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <!-- 动作配置 -->
        <div class="config-section">
          <h4>动作配置</h4>

          <!-- 导航URL -->
          <el-form-item v-if="activeStep.step_type === 'navigate'" label="页面URL" required>
            <el-input v-model="activeStep.action_config.url" placeholder="请输入URL，如：https://example.com" />
          </el-form-item>

          <!-- 元素定位器 -->
          <template v-if="needLocator">
            <el-form-item label="定位器类型" required>
              <el-select v-model="activeStep.action_config.locator.type" placeholder="选择定位器类型">
                <el-option label="CSS选择器" value="css" />
                <el-option label="XPath" value="xpath" />
                <el-option label="ID" value="id" />
                <el-option label="Name" value="name" />
                <el-option label="Class" value="class" />
                <el-option label="标签名" value="tag" />
                <el-option label="链接文本" value="link_text" />
              </el-select>
            </el-form-item>
            <el-form-item label="定位器值" required>
              <el-input v-model="activeStep.action_config.locator.value" placeholder="请输入定位器值" />
              <div class="locator-examples">
                <el-button size="small" text @click="showLocatorExamples = !showLocatorExamples">
                  查看示例
                </el-button>
                <div v-if="showLocatorExamples" class="examples-content">
                  <div v-for="example in getLocatorExamples(activeStep.action_config.locator.type)" :key="example" class="example-item">
                    {{ example }}
                  </div>
                </div>
              </div>
            </el-form-item>
          </template>

          <!-- 输入文本 -->
          <el-form-item v-if="activeStep.step_type === 'input'" label="输入文本" required>
            <el-input v-model="activeStep.action_config.text" placeholder="请输入文本" />
            <el-checkbox v-model="activeStep.action_config.clear_first">输入前清空</el-checkbox>
          </el-form-item>

          <!-- 选择选项 -->
          <el-form-item v-if="activeStep.step_type === 'select_option'" label="选择值" required>
            <el-select v-model="activeStep.action_config.values" multiple placeholder="选择选项">
              <!-- 这里需要动态获取页面元素选项 -->
            </el-select>
          </el-form-item>

          <!-- 等待配置 -->
          <template v-if="activeStep.step_type === 'wait'">
            <el-form-item label="等待类型" required>
              <el-select v-model="activeStep.action_config.wait_type">
                <el-option label="元素可见" value="element_visible" />
                <el-option label="元素存在" value="element_exists" />
                <el-option label="元素隐藏" value="element_hidden" />
                <el-option label="元素可点击" value="element_clickable" />
              </el-select>
            </el-form-item>
            <el-form-item label="超时时间(秒)">
              <el-input-number v-model="activeStep.action_config.timeout" :min="1" :max="300" />
            </el-form-item>
          </template>

          <!-- 睡眠时间 -->
          <el-form-item v-if="activeStep.step_type === 'sleep'" label="等待时间(秒)" required>
            <el-input-number v-model="activeStep.action_config.time" :min="1" :max="300" />
          </el-form-item>

          <!-- 验证配置 -->
          <template v-if="isValidationStep">
            <el-form-item label="验证类型" required>
              <el-select v-model="activeStep.action_config.validation_type">
                <el-option label="元素存在" value="element_exists" />
                <el-option label="元素可见" value="element_visible" />
                <el-option label="文本包含" value="text_contains" />
                <el-option label="文本等于" value="text_equals" />
                <el-option label="属性值" value="attribute_value" />
                <el-option label="页面标题" value="page_title" />
              </el-select>
            </el-form-item>
            <el-form-item v-if="needExpectedValue" label="期望值" required>
              <el-input v-model="activeStep.action_config.expected_value" placeholder="请输入期望值" />
            </el-form-item>
          </template>

          <!-- JavaScript脚本 -->
          <el-form-item v-if="activeStep.step_type === 'execute_script'" label="JavaScript代码" required>
            <el-input
              v-model="activeStep.action_config.script"
              type="textarea"
              :rows="4"
              placeholder="请输入JavaScript代码"
            />
          </el-form-item>

          <!-- 截图配置 -->
          <template v-if="activeStep.step_type === 'screenshot'">
            <el-form-item label="文件名">
              <el-input v-model="activeStep.action_config.filename" placeholder="截图文件名" />
            </el-form-item>
            <el-form-item label="截图模式">
              <el-radio-group v-model="activeStep.action_config.full_page">
                <el-radio :label="false">当前视窗</el-radio>
                <el-radio :label="true">整个页面</el-radio>
              </el-radio-group>
            </el-form-item>
          </template>
        </div>

        <!-- 验证配置 -->
        <div class="config-section">
          <h4>
            验证配置
            <el-switch v-model="enableValidation" />
          </h4>

          <template v-if="enableValidation">
            <el-form-item label="验证类型">
              <el-select v-model="activeStep.validation_config.type">
                <el-option label="元素存在" value="element_exists" />
                <el-option label="元素可见" value="element_visible" />
                <el-option label="文本包含" value="text_contains" />
                <el-option label="文本等于" value="text_equals" />
              </el-select>
            </el-form-item>
            <el-form-item label="期望值">
              <el-input v-model="activeStep.validation_config.expected_value" placeholder="请输入期望值" />
            </el-form-item>
          </template>
        </div>

        <!-- 步骤描述 -->
        <el-form-item label="步骤描述">
          <el-input
            v-model="activeStep.description"
            type="textarea"
            :rows="2"
            placeholder="请输入步骤描述"
          />
        </el-form-item>
      </el-form>
    </div>

    <!-- 步骤模板选择 -->
    <el-dialog v-model="showTemplateDialog" title="选择步骤模板" width="600px">
      <div class="template-list">
        <div
          v-for="template in stepTemplates"
          :key="template.name"
          class="template-item"
          @click="applyTemplate(template)"
        >
          <div class="template-name">{{ template.name }}</div>
          <div class="template-desc">{{ template.description }}</div>
          <div class="template-tags">
            <el-tag v-for="tag in template.tags" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, ArrowUp, ArrowDown, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

// 数据
const steps = ref([])
const activeStepIndex = ref(0)
const showLocatorExamples = ref(false)
const showTemplateDialog = ref(false)
const stepTemplates = ref([])
const enableValidation = ref(false)

// 计算属性
const activeStep = computed(() => {
  return steps.value[activeStepIndex.value] || null
})

const needLocator = computed(() => {
  return ['click', 'input', 'select_option', 'hover', 'drag', 'wait', 'validate'].includes(activeStep.value?.step_type)
})

const needExpectedValue = computed(() => {
  return ['text_contains', 'text_equals', 'attribute_value', 'page_title'].includes(activeStep.value?.action_config?.validation_type)
})

const isValidationStep = computed(() => {
  return ['validate', 'assert_text', 'assert_title'].includes(activeStep.value?.step_type)
})

// 监听数据变化
watch(() => props.modelValue, (newVal) => {
  steps.value = JSON.parse(JSON.stringify(newVal))
}, { immediate: true, deep: true })

watch(steps, (newVal) => {
  emit('update:modelValue', JSON.parse(JSON.stringify(newVal)))
}, { deep: true })

// 初始化步骤配置
const initStepConfig = (stepType) => {
  const baseConfig = {
    step_name: '',
    step_type: stepType,
    action_config: {},
    wait_config: null,
    validation_config: null,
    screenshot_config: null,
    condition_config: null,
    is_enabled: true,
    description: ''
  }

  // 根据步骤类型设置默认配置
  switch (stepType) {
    case 'navigate':
      baseConfig.action_config = { url: '' }
      break
    case 'click':
      baseConfig.action_config = {
        locator: { type: 'css', value: '' },
        timeout: 10
      }
      break
    case 'input':
      baseConfig.action_config = {
        locator: { type: 'css', value: '' },
        text: '',
        clear_first: true
      }
      break
    case 'wait':
      baseConfig.action_config = {
        wait_type: 'element_visible',
        locator: { type: 'css', value: '' },
        timeout: 10
      }
      break
    case 'screenshot':
      baseConfig.action_config = {
        filename: '',
        full_page: false
      }
      break
    case 'execute_script':
      baseConfig.action_config = {
        script: ''
      }
      break
  }

  return baseConfig
}

// 获取步骤类型标签
const getStepTypeLabel = (stepType) => {
  const typeMap = {
    navigate: '打开页面',
    click: '点击元素',
    input: '输入文本',
    select_option: '选择选项',
    hover: '悬停',
    drag: '拖拽',
    wait: '等待元素',
    sleep: '等待时间',
    validate: '验证元素',
    assert_text: '验证文本',
    assert_title: '验证标题',
    screenshot: '截图',
    execute_script: '执行脚本',
    switch_frame: '切换框架'
  }
  return typeMap[stepType] || stepType
}

// 获取定位器示例
const getLocatorExamples = (type) => {
  const examples = {
    css: ['#submit-button', '.error-message', 'input[name="username"]'],
    xpath: ['//button[@id="submit"]', '//div[contains(@class, "error")]', '//input[@name="username"]'],
    id: ['username', 'password', 'submit-button'],
    name: ['username', 'email', 'login-form'],
    class: ['btn btn-primary', 'form-control', 'error-message'],
    tag: ['button', 'input', 'div'],
    link_text: ['登录', '注册', '忘记密码']
  }
  return examples[type] || []
}

// 设置活动步骤
const setActiveStep = (index) => {
  activeStepIndex.value = index
  // 初始化验证配置
  if (activeStep.value && !activeStep.value.validation_config) {
    activeStep.value.validation_config = {
      type: 'element_exists',
      expected_value: '',
      enabled: false
    }
  }
  enableValidation.value = activeStep.value?.validation_config?.enabled || false
}

// 添加步骤
const addStep = () => {
  showTemplateDialog.value = true
  loadStepTemplates()
}

// 应用模板
const applyTemplate = (template) => {
  const newStep = initStepConfig(template.step_type)
  newStep.step_name = template.name
  newStep.description = template.description
  newStep.action_config = JSON.parse(JSON.stringify(template.action_template))
  if (template.validation_template) {
    newStep.validation_config = JSON.parse(JSON.stringify(template.validation_template))
  }

  steps.value.push(newStep)
  activeStepIndex.value = steps.value.length - 1
  showTemplateDialog.value = false
  ElMessage.success('步骤添加成功')
}

// 移除步骤
const removeStep = (index) => {
  steps.value.splice(index, 1)
  if (activeStepIndex.value >= steps.value.length) {
    activeStepIndex.value = Math.max(0, steps.value.length - 1)
  }
}

// 移动步骤
const moveStepUp = (index) => {
  if (index > 0) {
    [steps.value[index], steps.value[index - 1]] = [steps.value[index - 1], steps.value[index]]
    if (activeStepIndex.value === index) {
      activeStepIndex.value = index - 1
    } else if (activeStepIndex.value === index - 1) {
      activeStepIndex.value = index
    }
  }
}

const moveStepDown = (index) => {
  if (index < steps.value.length - 1) {
    [steps.value[index], steps.value[index + 1]] = [steps.value[index + 1], steps.value[index]]
    if (activeStepIndex.value === index) {
      activeStepIndex.value = index + 1
    } else if (activeStepIndex.value === index + 1) {
      activeStepIndex.value = index
    }
  }
}

// 步骤类型变化
const handleStepTypeChange = (stepType) => {
  // 重新初始化动作配置
  const newConfig = initStepConfig(stepType).action_config
  activeStep.value.action_config = newConfig
}

// 加载步骤模板
const loadStepTemplates = async () => {
  try {
    const response = await axios.get('/api/plugins/api-engine/browser/templates/steps')
    if (response.data.success) {
      stepTemplates.value = response.data.data
    }
  } catch (error) {
    console.error('加载步骤模板失败:', error)
  }
}
</script>

<style scoped>
.browser-step-editor {
  display: flex;
  gap: 20px;
  height: 600px;
}

.step-list {
  width: 300px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow-y: auto;
}

.step-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.step-item:hover {
  background-color: #f5f7fa;
}

.step-item.step-active {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-number {
  width: 24px;
  height: 24px;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.step-info {
  flex: 1;
}

.step-name {
  font-weight: 500;
  color: #303133;
}

.step-type {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.step-actions {
  display: flex;
  gap: 4px;
}

.add-step-btn {
  padding: 12px;
  text-align: center;
  color: #409eff;
  cursor: pointer;
  border-top: 1px solid #e4e7ed;
  transition: background-color 0.3s;
}

.add-step-btn:hover {
  background-color: #f5f7fa;
}

.step-editor-panel {
  flex: 1;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  overflow-y: auto;
}

.panel-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
}

.config-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.config-section h4 {
  margin: 0 0 15px 0;
  color: #606266;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.locator-examples {
  margin-top: 5px;
}

.examples-content {
  margin-top: 8px;
  padding: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.example-item {
  font-family: monospace;
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.template-list {
  max-height: 400px;
  overflow-y: auto;
}

.template-item {
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.template-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
}

.template-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 5px;
}

.template-desc {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.template-tags {
  display: flex;
  gap: 4px;
}
</style>