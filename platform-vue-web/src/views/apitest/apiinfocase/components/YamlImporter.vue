<template>
  <el-dialog
    v-model="dialogVisible"
    title="导入 YAML 用例"
    width="900px"
    @close="handleClose"
  >
    <div class="yaml-importer">
      <!-- 顶部切换 -->
      <el-radio-group v-model="inputMode" class="mode-switch">
        <el-radio-button value="text">粘贴 YAML</el-radio-button>
        <el-radio-button value="file">上传文件</el-radio-button>
      </el-radio-group>

      <!-- 文本输入模式 -->
      <div v-if="inputMode === 'text'" class="text-mode">
        <el-input
          v-model="yamlContent"
          type="textarea"
          :rows="16"
          placeholder="粘贴 YAML 内容，格式示例：
desc: 登录接口测试
steps:
  - 发送登录请求:
      关键字: send_request
      method: POST
      url: '{{URL}}'
      data:
        username: '{{username}}'
        password: '{{password}}'
  - 提取token:
      关键字: ex_jsonData
      EXVALUE: $.data.token
      VARNAME: token
ddts:
  - desc: 用户A登录
    username: admin
    password: '123456'"
          class="yaml-textarea"
        />
      </div>

      <!-- 文件上传模式 -->
      <div v-else class="file-mode">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".yaml,.yml"
          :on-change="handleFileChange"
          drag
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">拖拽 YAML 文件到此处，或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">仅支持 .yaml 或 .yml 文件</div>
          </template>
        </el-upload>
      </div>

      <!-- 解析按钮 -->
      <div class="parse-actions">
        <el-button type="primary" @click="handleParse" :loading="parsing">
          解析 YAML
        </el-button>
        <el-button v-if="parsedSteps.length > 0" @click="clearParsed">清空预览</el-button>
      </div>

      <!-- 解析错误 -->
      <el-alert
        v-if="parseError"
        :title="parseError"
        type="error"
        show-icon
        class="parse-error"
      />

      <!-- 解析结果预览 -->
      <div v-if="parsedSteps.length > 0" class="preview-section">
        <el-divider>解析结果预览 ({{ parsedSteps.length }} 个步骤)</el-divider>
        
        <el-table :data="parsedSteps" border stripe max-height="300">
          <el-table-column prop="run_order" label="序号" width="70" align="center" />
          <el-table-column prop="step_desc" label="步骤描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="keyword_name" label="关键字" width="180">
            <template #default="{ row }">
              <el-tag size="small" :type="row.keyword_id ? 'success' : 'warning'">
                {{ row.keyword_name }}
              </el-tag>
              <el-icon v-if="!row.keyword_id" class="warning-icon"><Warning /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80" align="center">
            <template #default="{ $index }">
              <el-button type="danger" link @click="removeStep($index)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- 数据驱动预览 -->
        <div v-if="parsedDdts.length > 0" class="ddts-preview">
          <el-divider>数据驱动 ({{ parsedDdts.length }} 组数据)</el-divider>
          <el-table :data="parsedDdts" border stripe max-height="200">
            <el-table-column prop="desc" label="数据描述" min-width="150" />
            <el-table-column label="变量" min-width="300">
              <template #default="{ row }">
                <el-tag v-for="(value, key) in row" :key="key" v-show="key !== 'desc'" size="small" class="var-tag">
                  {{ key }}={{ value }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleImport" :disabled="parsedSteps.length === 0">
        导入 {{ parsedSteps.length }} 个步骤
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload, Warning } from '@element-plus/icons-vue'
import yaml from 'js-yaml'
import { queryAll as queryKeywords } from '~/views/apitest/keyword/apiKeyWord.js'
import { queryAll as queryOperationType } from '~/views/apitest/keyword/operationType.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  startOrder: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:modelValue', 'import'])

const dialogVisible = ref(false)
const inputMode = ref('text')
const yamlContent = ref('')
const parsing = ref(false)
const parseError = ref('')
const parsedSteps = ref([])
const parsedDdts = ref([])
const parsedContext = ref({})  // 全局配置
const uploadRef = ref(null)

// 关键字映射缓存
const keywordMap = ref({})
const operationTypeMap = ref({})

// 加载关键字列表
const loadKeywords = async () => {
  try {
    const [kwRes, opRes] = await Promise.all([queryKeywords(), queryOperationType()])
    
    if (kwRes.data.code === 200) {
      const keywords = kwRes.data.data || []
      keywords.forEach(kw => {
        keywordMap.value[kw.name] = kw
      })
    }
    
    if (opRes.data.code === 200) {
      const opTypes = opRes.data.data || []
      opTypes.forEach(op => {
        operationTypeMap.value[op.operation_type_name] = op
      })
    }
  } catch (error) {
    console.error('加载关键字列表失败:', error)
  }
}

// 文件变更处理
const handleFileChange = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    yamlContent.value = e.target.result
  }
  reader.readAsText(file.raw)
}

// 解析 YAML
const handleParse = () => {
  parseError.value = ''
  parsedSteps.value = []
  parsedDdts.value = []
  
  if (!yamlContent.value.trim()) {
    parseError.value = '请输入或上传 YAML 内容'
    return
  }
  
  parsing.value = true
  
  try {
    const data = yaml.load(yamlContent.value)
    
    if (!data || typeof data !== 'object') {
      throw new Error('YAML 格式错误：无法解析')
    }
    
    // 解析步骤（可选）
    const steps = []
    if (data.steps && Array.isArray(data.steps)) {
      let order = props.startOrder
      
      data.steps.forEach((stepObj) => {
        const stepName = Object.keys(stepObj)[0]
        const stepConfig = { ...stepObj[stepName] }
        const keywordName = stepConfig['关键字']
        delete stepConfig['关键字']
        
        // 查找关键字ID
        const keyword = keywordMap.value[keywordName]
        
        steps.push({
          run_order: order++,
          step_desc: stepName,
          keyword_name: keywordName,
          keyword_id: keyword?.id || null,
          operation_type_id: keyword?.operation_type_id || null,
          step_data: stepConfig
        })
      })
    }
    
    parsedSteps.value = steps
    
    // 解析数据驱动
    if (data.ddts && Array.isArray(data.ddts)) {
      parsedDdts.value = data.ddts
    }
    
    // 解析全局配置（排除 desc, steps, ddts 之外的所有字段）
    const contextKeys = Object.keys(data).filter(k => !['desc', 'steps', 'ddts'].includes(k))
    if (contextKeys.length > 0) {
      const context = {}
      contextKeys.forEach(key => {
        context[key] = data[key]
      })
      parsedContext.value = context
    }
    
    const contextCount = Object.keys(parsedContext.value).length
    const msgParts = []
    if (steps.length > 0) msgParts.push(`${steps.length} 个步骤`)
    if (contextCount > 0) msgParts.push(`${contextCount} 个全局配置`)
    if (parsedDdts.value.length > 0) msgParts.push(`${parsedDdts.value.length} 组数据驱动`)
    
    if (msgParts.length === 0) {
      throw new Error('YAML 中没有可导入的内容')
    }
    ElMessage.success(`成功解析 ${msgParts.join('，')}`)
    
  } catch (error) {
    parseError.value = `解析失败: ${error.message}`
  } finally {
    parsing.value = false
  }
}

// 移除步骤
const removeStep = (index) => {
  parsedSteps.value.splice(index, 1)
  // 重新编号
  parsedSteps.value.forEach((step, i) => {
    step.run_order = props.startOrder + i
  })
}

// 清空预览
const clearParsed = () => {
  parsedSteps.value = []
  parsedDdts.value = []
  parsedContext.value = {}
}

// 导入
const handleImport = () => {
  // 检查是否有未匹配的关键字（仅当有步骤时）
  if (parsedSteps.value.length > 0) {
    const unmatchedSteps = parsedSteps.value.filter(s => !s.keyword_id)
    if (unmatchedSteps.length > 0) {
      ElMessage.warning(`有 ${unmatchedSteps.length} 个步骤的关键字未匹配，请先在关键字管理中添加对应关键字`)
      return
    }
  }
  
  emit('import', {
    steps: parsedSteps.value,
    ddts: parsedDdts.value,
    context: parsedContext.value
  })
  
  const msgParts = []
  if (parsedSteps.value.length > 0) msgParts.push(`${parsedSteps.value.length} 个步骤`)
  if (Object.keys(parsedContext.value).length > 0) msgParts.push(`${Object.keys(parsedContext.value).length} 个全局配置`)
  if (parsedDdts.value.length > 0) msgParts.push(`${parsedDdts.value.length} 组数据驱动`)
  ElMessage.success(`成功导入 ${msgParts.join('，')}`)
  handleClose()
}

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  emit('update:modelValue', false)
  yamlContent.value = ''
  parsedSteps.value = []
  parsedDdts.value = []
  parseError.value = ''
}

// 监听 modelValue
watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
  if (val) {
    loadKeywords()
  }
})
</script>

<style scoped>
.yaml-importer {
  padding: 0 10px;
}

.mode-switch {
  margin-bottom: 16px;
}

.yaml-textarea :deep(.el-textarea__inner) {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.file-mode {
  margin-bottom: 16px;
}

.parse-actions {
  margin: 16px 0;
  display: flex;
  gap: 12px;
}

.parse-error {
  margin-bottom: 16px;
}

.preview-section {
  margin-top: 16px;
}

.var-tag {
  margin: 2px 4px 2px 0;
}

.warning-icon {
  color: #e6a23c;
  margin-left: 4px;
}

.ddts-preview {
  margin-top: 16px;
}
</style>
