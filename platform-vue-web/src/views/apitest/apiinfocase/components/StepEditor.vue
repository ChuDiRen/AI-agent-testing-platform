<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑步骤' : '添加步骤'"
    width="900px"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="stepForm" :rules="rules" label-width="100px">
      <!-- 快捷模板区域 - 按引擎分组 -->
      <div v-if="!isEdit" class="quick-templates">
        <div class="template-section" v-for="engine in quickTemplateEngines" :key="engine.code">
          <span class="engine-label">{{ engine.icon }} {{ engine.name }}:</span>
          <el-button 
            v-for="tpl in engine.templates" 
            :key="tpl.key"
            size="small" 
            @click="applyTemplate(tpl.key)"
          >
            {{ tpl.label }}
          </el-button>
        </div>
      </div>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="运行序号" prop="run_order">
            <el-input-number v-model="stepForm.run_order" :min="1" :step="1" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="16">
          <el-form-item label="步骤描述" prop="step_desc">
            <el-input v-model="stepForm.step_desc" placeholder="请输入步骤描述" />
          </el-form-item>
        </el-col>
      </el-row>

      <!-- 关键字选择 - 按引擎分组 -->
      <el-form-item label="选择关键字" prop="keyword_id">
        <div class="keyword-selector">
          <!-- 搜索框 -->
          <el-input
            v-model="keywordSearch"
            placeholder="搜索关键字..."
            prefix-icon="Search"
            clearable
            style="margin-bottom: 12px"
          />
          
          <!-- 按引擎分组的关键字列表 -->
          <div class="engine-groups" v-loading="loadingKeywords">
            <el-collapse v-model="activeEngines" v-if="filteredEngineKeywords.length > 0">
              <el-collapse-item 
                v-for="engine in filteredEngineKeywords" 
                :key="engine.plugin_code"
                :name="engine.plugin_code"
              >
                <template #title>
                  <span class="engine-title">
                    <span class="engine-icon">{{ getEngineIcon(engine.plugin_code) }}</span>
                    {{ engine.plugin_name }}
                    <el-tag size="small" type="info" style="margin-left: 8px">{{ engine.keywords.length }}</el-tag>
                  </span>
                </template>
                <div class="keyword-grid">
                  <div
                    v-for="kw in engine.keywords"
                    :key="kw.id"
                    :class="['keyword-item', { active: stepForm.keyword_id === kw.id }]"
                    @click="selectKeyword(kw, engine.plugin_code)"
                  >
                    <div class="kw-name">{{ kw.name }}</div>
                    <div class="kw-category">{{ kw.category }}</div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
            <el-empty v-else description="暂无关键字，请先同步执行引擎关键字" :image-size="60" />
          </div>
          
          <!-- 已选择的关键字 -->
          <div v-if="selectedKeyword" class="selected-keyword">
            <el-tag type="success" size="large" closable @close="clearKeyword">
              {{ getEngineIcon(selectedKeyword.plugin_code) }} {{ selectedKeyword.name }}
            </el-tag>
          </div>
        </div>
      </el-form-item>

      <!-- 动态字段区域 -->
      <div v-if="dynamicFields.length > 0" class="dynamic-fields">
        <el-divider>关键字参数配置</el-divider>
        <el-form-item
          v-for="field in dynamicFields"
          :key="field.name"
          :label="field.placeholder || field.description || field.name"
        >
          <!-- 特殊字段：接口信息下拉 -->
          <el-select
            v-if="field.name.startsWith('_接口信息')"
            v-model="stepForm.step_data[field.name]"
            placeholder="请选择接口"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="api in apiInfoList"
              :key="api.id"
              :label="`${api.api_name} (${api.request_method} ${api.request_url})`"
              :value="api.id"
            />
          </el-select>

          <!-- 特殊字段：数据库下拉 -->
          <el-select
            v-else-if="field.name && field.name.startsWith('_数据库')"
            v-model="stepForm.step_data[field.name]"
            placeholder="请选择数据库"
            filterable
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="db in dbList"
              :key="db.id"
              :label="`${db.db_name} (${db.db_type})`"
              :value="db.id"
            />
          </el-select>

          <!-- JSON/对象类型：使用文本域 -->
          <el-input
            v-else-if="isJsonField(field.name)"
            v-model="stepForm.step_data[field.name]"
            type="textarea"
            :rows="4"
            :placeholder="field.placeholder || field.description || `请输入${field.name} (JSON格式)`"
          />

          <!-- 普通文本输入框 -->
          <el-input
            v-else
            v-model="stepForm.step_data[field.name]"
            :placeholder="field.placeholder || field.description || `请输入${field.name}`"
          />
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { queryKeywordsGroupedByEngine, getKeywordFields } from '~/views/apitest/apiinfocase/apiInfoCase.js'
import { queryAll as queryApiInfo } from '~/views/apitest/apiinfo/apiinfo.js'
import { queryAll as queryDbBase } from '~/views/apitest/project/dbBase.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  stepData: {
    type: Object,
    default: null
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  nextOrder: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:modelValue', 'confirm'])

// 对话框显示状态
const dialogVisible = ref(false)
const formRef = ref(null)

// 表单数据
const stepForm = reactive({
  run_order: 1,
  step_desc: '',
  operation_type_id: null,
  keyword_id: null,
  step_data: {}
})

// 表单验证规则
const rules = {
  run_order: [{ required: true, message: '请输入运行序号', trigger: 'blur' }],
  step_desc: [{ required: true, message: '请输入步骤描述', trigger: 'blur' }],
  keyword_id: [{ required: true, message: '请选择关键字', trigger: 'change' }]
}

// 关键字相关
const engineKeywords = ref([])
const loadingKeywords = ref(false)
const keywordSearch = ref('')
const activeEngines = ref([])
const selectedKeyword = ref(null)
const dynamicFields = ref([])
const apiInfoList = ref([])
const dbList = ref([])

// 快捷模板 - 按引擎分组
const quickTemplateEngines = [
  {
    code: 'api_engine',
    name: 'API引擎',
    icon: '📡',
    templates: [
      { key: 'send_request', label: 'HTTP请求' },
      { key: 'ex_jsonData', label: '提取JSON' },
      { key: 'assert_text', label: '断言' }
    ]
  },
  {
    code: 'web_engine',
    name: 'Web引擎',
    icon: '🌐',
    templates: [
      { key: 'open_browser', label: '打开浏览器' },
      { key: 'navigate_to', label: '导航' },
      { key: 'click_element', label: '点击' },
      { key: 'input_text', label: '输入' },
      { key: 'bu_run_task', label: 'AI任务' }
    ]
  }
]

// 快捷模板定义
const QUICK_TEMPLATES = {
  // API 引擎模板
  send_request: {
    step_desc: 'HTTP请求',
    keyword_name: 'send_request',
    plugin_code: 'api_engine',
    fields: [
      { name: 'method', placeholder: '请求方法', default: 'GET' },
      { name: 'url', placeholder: '请求URL' },
      { name: 'params', placeholder: 'URL参数 (JSON)' },
      { name: 'headers', placeholder: '请求头 (JSON)' },
      { name: 'data', placeholder: '请求体 (JSON)' }
    ]
  },
  ex_jsonData: {
    step_desc: '提取响应数据',
    keyword_name: 'ex_jsonData',
    plugin_code: 'api_engine',
    fields: [
      { name: 'EXVALUE', placeholder: 'JSONPath表达式', default: '$.data' },
      { name: 'VARNAME', placeholder: '变量名' },
      { name: 'INDEX', placeholder: '索引', default: '0' }
    ]
  },
  assert_text: {
    step_desc: '断言验证',
    keyword_name: 'assert_text_comparators',
    plugin_code: 'api_engine',
    fields: [
      { name: 'VALUE', placeholder: '实际值' },
      { name: 'EXPECTED', placeholder: '期望值' },
      { name: 'OP_STR', placeholder: '比较运算符', default: '==' }
    ]
  },
  // Web 引擎模板
  open_browser: {
    step_desc: '打开浏览器',
    keyword_name: 'open_browser',
    plugin_code: 'web_engine',
    fields: [
      { name: 'browser', placeholder: '浏览器类型', default: 'chrome' },
      { name: 'headless', placeholder: '无头模式', default: 'false' }
    ]
  },
  navigate_to: {
    step_desc: '导航到URL',
    keyword_name: 'navigate_to',
    plugin_code: 'web_engine',
    fields: [
      { name: 'url', placeholder: '目标URL' }
    ]
  },
  click_element: {
    step_desc: '点击元素',
    keyword_name: 'click_element',
    plugin_code: 'web_engine',
    fields: [
      { name: 'locator_type', placeholder: '定位方式', default: 'id' },
      { name: 'element', placeholder: '元素标识' }
    ]
  },
  input_text: {
    step_desc: '输入文本',
    keyword_name: 'input_text',
    plugin_code: 'web_engine',
    fields: [
      { name: 'locator_type', placeholder: '定位方式', default: 'id' },
      { name: 'element', placeholder: '元素标识' },
      { name: 'text', placeholder: '输入内容' }
    ]
  },
  bu_run_task: {
    step_desc: 'AI执行任务',
    keyword_name: 'bu_run_task',
    plugin_code: 'web_engine',
    fields: [
      { name: 'task', placeholder: '任务描述（自然语言）' }
    ]
  }
}

// 获取引擎图标
const getEngineIcon = (pluginCode) => {
  const icons = {
    'api_engine': '📡',
    'web_engine': '🌐',
    'perf_engine': '⚡',
    'uncategorized': '📦'
  }
  return icons[pluginCode] || '🔧'
}

// 判断是否为JSON字段
const isJsonField = (fieldName) => {
  const jsonFields = ['HEADERS', 'PARAMS', 'DATA', 'JSON', 'headers', 'params', 'data', 'json', 'form_data']
  return jsonFields.includes(fieldName)
}

// 过滤后的引擎关键字
const filteredEngineKeywords = computed(() => {
  if (!keywordSearch.value) {
    return engineKeywords.value
  }
  
  const search = keywordSearch.value.toLowerCase()
  return engineKeywords.value.map(engine => ({
    ...engine,
    keywords: engine.keywords.filter(kw => 
      kw.name.toLowerCase().includes(search) ||
      (kw.category && kw.category.toLowerCase().includes(search))
    )
  })).filter(engine => engine.keywords.length > 0)
})

// 加载按引擎分组的关键字
const loadEngineKeywords = async () => {
  loadingKeywords.value = true
  try {
    const res = await queryKeywordsGroupedByEngine()
    if (res.data.code === 200 && res.data.data) {
      engineKeywords.value = res.data.data.engines || []
      // 默认展开第一个引擎
      if (engineKeywords.value.length > 0) {
        activeEngines.value = [engineKeywords.value[0].plugin_code]
      }
    }
  } catch (error) {
    console.error('加载关键字失败:', error)
    ElMessage.error('加载关键字失败')
  } finally {
    loadingKeywords.value = false
  }
}

// 选择关键字
const selectKeyword = async (keyword, pluginCode) => {
  stepForm.keyword_id = keyword.id
  stepForm.operation_type_id = keyword.operation_type_id
  selectedKeyword.value = { ...keyword, plugin_code: pluginCode }
  
  // 加载关键字字段
  await loadKeywordFields(keyword.id, keyword.keyword_desc)
}

// 清除选择的关键字
const clearKeyword = () => {
  stepForm.keyword_id = null
  stepForm.operation_type_id = null
  selectedKeyword.value = null
  dynamicFields.value = []
  stepForm.step_data = {}
}

// 加载关键字字段
const loadKeywordFields = async (keywordId, keywordDesc) => {
  dynamicFields.value = []
  
  // 先尝试使用已有的 keyword_desc
  if (keywordDesc && Array.isArray(keywordDesc)) {
    dynamicFields.value = keywordDesc
    initStepData(keywordDesc)
    return
  }
  
  // 从后端获取字段定义
  try {
    const res = await getKeywordFields(keywordId)
    if (res.data.code === 200) {
      const fields = Array.isArray(res.data.data) ? res.data.data : []
      dynamicFields.value = fields
      initStepData(fields)
    }
  } catch (error) {
    console.error('加载关键字字段失败:', error)
  }
}

// 初始化 step_data
const initStepData = (fields, keepExisting = false) => {
  if (!keepExisting) {
    stepForm.step_data = {}
  }
  
  fields.forEach(field => {
    if (field && field.name && stepForm.step_data[field.name] === undefined) {
      stepForm.step_data[field.name] = field.default || ''
    }
  })
  
  // 加载特殊字段数据
  const hasApiField = fields.some(f => f.name && f.name.startsWith('_接口信息'))
  const hasDbField = fields.some(f => f.name && f.name.startsWith('_数据库'))
  
  if (hasApiField) loadApiInfo()
  if (hasDbField) loadDbList()
}

// 加载接口信息列表
const loadApiInfo = async () => {
  try {
    const res = await queryApiInfo()
    if (res.data.code === 200) {
      apiInfoList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载接口信息失败:', error)
  }
}

// 加载数据库列表
const loadDbList = async () => {
  try {
    const res = await queryDbBase()
    if (res.data.code === 200) {
      dbList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载数据库列表失败:', error)
  }
}

// 应用快捷模板
const applyTemplate = (templateKey) => {
  const template = QUICK_TEMPLATES[templateKey]
  if (!template) return
  
  stepForm.step_desc = template.step_desc
  
  // 在已加载的关键字中查找
  for (const engine of engineKeywords.value) {
    if (engine.plugin_code === template.plugin_code) {
      const matchedKw = engine.keywords.find(kw => kw.name === template.keyword_name)
      if (matchedKw) {
        selectKeyword(matchedKw, engine.plugin_code)
        // 使用模板字段覆盖
        dynamicFields.value = template.fields
        stepForm.step_data = {}
        template.fields.forEach(field => {
          stepForm.step_data[field.name] = field.default || ''
        })
        ElMessage.success(`已应用模板: ${template.step_desc}`)
        return
      }
    }
  }
  
  // 未找到关键字，使用模板字段
  ElMessage.warning(`未找到关键字 ${template.keyword_name}，请先同步关键字`)
  dynamicFields.value = template.fields
  stepForm.step_data = {}
  template.fields.forEach(field => {
    stepForm.step_data[field.name] = field.default || ''
  })
}

// 监听 modelValue 变化
watch(() => props.modelValue, async (val) => {
  dialogVisible.value = val
  if (!val) return
  
  // 加载关键字
  if (engineKeywords.value.length === 0) {
    await loadEngineKeywords()
  }
  
  if (props.stepData) {
    // 编辑模式
    const rawStepData = props.stepData.step_data ? JSON.parse(JSON.stringify(props.stepData.step_data)) : {}
    
    // 将对象类型的参数转换为JSON字符串
    for (const key in rawStepData) {
      if (typeof rawStepData[key] === 'object' && rawStepData[key] !== null) {
        rawStepData[key] = JSON.stringify(rawStepData[key], null, 2)
      }
    }
    
    Object.assign(stepForm, {
      run_order: props.stepData.run_order,
      step_desc: props.stepData.step_desc,
      operation_type_id: props.stepData.operation_type_id,
      keyword_id: props.stepData.keyword_id,
      step_data: rawStepData
    })
    
    // 查找并设置选中的关键字
    if (props.stepData.keyword_id) {
      for (const engine of engineKeywords.value) {
        const kw = engine.keywords.find(k => k.id === props.stepData.keyword_id)
        if (kw) {
          selectedKeyword.value = { ...kw, plugin_code: engine.plugin_code }
          activeEngines.value = [engine.plugin_code]
          // 加载字段但保留现有数据
          if (kw.keyword_desc && Array.isArray(kw.keyword_desc)) {
            dynamicFields.value = kw.keyword_desc
          } else {
            await loadKeywordFields(kw.id, kw.keyword_desc)
          }
          break
        }
      }
    }
  } else {
    // 新增模式
    stepForm.run_order = props.nextOrder
    stepForm.step_desc = ''
    stepForm.operation_type_id = null
    stepForm.keyword_id = null
    stepForm.step_data = {}
    selectedKeyword.value = null
    dynamicFields.value = []
    keywordSearch.value = ''
  }
})

// 关闭对话框
const handleClose = () => {
  emit('update:modelValue', false)
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

// 确认
const handleConfirm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (!valid) return
    
    // 处理数据
    const processedStepData = {}
    for (const key in stepForm.step_data) {
      const val = stepForm.step_data[key]
      
      if (val === null || val === undefined || val === '' || key === 'response') {
        continue
      }
      
      if (typeof val === 'string' && val.trim()) {
        try {
          if (val.trim().startsWith('{') || val.trim().startsWith('[')) {
            processedStepData[key] = JSON.parse(val)
          } else {
            processedStepData[key] = val
          }
        } catch (e) {
          processedStepData[key] = val
        }
      } else if (val !== '') {
        processedStepData[key] = val
      }
    }
    
    const stepData = {
      run_order: stepForm.run_order,
      step_desc: stepForm.step_desc,
      operation_type_id: stepForm.operation_type_id,
      keyword_id: stepForm.keyword_id,
      step_data: processedStepData
    }
    
    emit('confirm', stepData)
    handleClose()
  })
}
</script>

<style scoped>
.quick-templates {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4fc 100%);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.template-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.template-section:last-child {
  margin-bottom: 0;
}

.engine-label {
  font-weight: 500;
  font-size: 13px;
  color: #606266;
  min-width: 90px;
}

.keyword-selector {
  width: 100%;
}

.engine-groups {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
}

.engine-title {
  display: flex;
  align-items: center;
  font-weight: 500;
}

.engine-icon {
  margin-right: 8px;
  font-size: 16px;
}

.keyword-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 8px;
  padding: 8px;
}

.keyword-item {
  padding: 8px 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}

.keyword-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.keyword-item.active {
  border-color: #409eff;
  background: #409eff;
  color: #fff;
}

.keyword-item.active .kw-category {
  color: rgba(255, 255, 255, 0.8);
}

.kw-name {
  font-size: 13px;
  font-weight: 500;
  font-family: 'Consolas', 'Monaco', monospace;
}

.kw-category {
  font-size: 11px;
  color: #909399;
  margin-top: 2px;
}

.selected-keyword {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f0f9eb;
  border-radius: 4px;
}

.dynamic-fields {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.dynamic-fields :deep(.el-input__inner),
.dynamic-fields :deep(.el-textarea__inner) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

:deep(.el-divider) {
  margin: 10px 0 20px 0;
}

:deep(.el-collapse-item__header) {
  background: #fafafa;
  padding-left: 12px;
}

:deep(.el-collapse-item__content) {
  padding-bottom: 0;
}
</style>

