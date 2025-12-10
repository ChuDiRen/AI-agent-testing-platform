<template>
  <el-dialog
    v-model="dialogVisible"
    title="导入全局配置"
    width="700px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- 输入方式切换 -->
    <div class="input-mode-switch">
      <el-radio-group v-model="inputMode" size="default">
        <el-radio-button label="text">粘贴 YAML</el-radio-button>
        <el-radio-button label="file">上传文件</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 文本输入 -->
    <div v-if="inputMode === 'text'" class="yaml-input">
      <el-input
        v-model="yamlContent"
        type="textarea"
        :rows="12"
        placeholder="粘贴 YAML 内容，格式示例：
URL: http://example.com
API_KEY: your-api-key
_database:
  host: localhost
  port: 3306
  user: root
  password: 123456"
      />
    </div>

    <!-- 文件上传 -->
    <div v-else class="file-upload">
      <el-upload
        ref="uploadRef"
        drag
        :auto-upload="false"
        :show-file-list="false"
        accept=".yaml,.yml"
        @change="handleFileChange"
      >
        <el-icon class="el-icon--upload"><Upload /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 .yaml / .yml 文件</div>
        </template>
      </el-upload>
      <div v-if="yamlContent" class="file-preview">
        <el-input
          v-model="yamlContent"
          type="textarea"
          :rows="8"
          readonly
        />
      </div>
    </div>

    <!-- 解析按钮 -->
    <div class="parse-actions">
      <el-button type="primary" @click="handleParse" :loading="parsing">解析 YAML</el-button>
    </div>

    <!-- 解析错误 -->
    <el-alert v-if="parseError" :title="parseError" type="error" show-icon :closable="false" class="parse-error" />

    <!-- 解析预览 -->
    <div v-if="Object.keys(parsedConfig).length > 0" class="parsed-preview">
      <div class="preview-header">
        <span class="preview-title">解析结果 ({{ Object.keys(parsedConfig).length }} 个配置)</span>
        <el-button type="danger" link size="small" @click="clearParsed">清空</el-button>
      </div>
      <el-table :data="configList" border stripe max-height="200" size="small">
        <el-table-column prop="key" label="变量名" width="180" />
        <el-table-column prop="value" label="变量值" show-overflow-tooltip />
        <el-table-column label="操作" width="60" align="center">
          <template #default="{ $index }">
            <el-button type="danger" link size="small" @click="removeConfig($index)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button 
        type="primary" 
        @click="handleImport" 
        :disabled="Object.keys(parsedConfig).length === 0"
      >
        导入 {{ Object.keys(parsedConfig).length }} 个配置
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import yaml from 'js-yaml'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'import'])

const dialogVisible = ref(false)
const inputMode = ref('text')
const yamlContent = ref('')
const parsing = ref(false)
const parseError = ref('')
const parsedConfig = ref({})
const uploadRef = ref(null)

// 转换为表格数据
const configList = computed(() => {
  return Object.entries(parsedConfig.value).map(([key, value]) => ({
    key,
    value: typeof value === 'object' ? JSON.stringify(value) : String(value)
  }))
})

// 监听 modelValue
watch(() => props.modelValue, (val) => {
  dialogVisible.value = val
})

watch(dialogVisible, (val) => {
  emit('update:modelValue', val)
})

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
  parsedConfig.value = {}
  
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
    
    // 排除 desc, steps, ddts，其他都作为全局配置
    const excludeKeys = ['desc', 'steps', 'ddts']
    const config = {}
    
    Object.entries(data).forEach(([key, value]) => {
      if (!excludeKeys.includes(key)) {
        config[key] = value
      }
    })
    
    if (Object.keys(config).length === 0) {
      throw new Error('没有找到可导入的配置')
    }
    
    parsedConfig.value = config
    ElMessage.success(`成功解析 ${Object.keys(config).length} 个配置`)
    
  } catch (error) {
    parseError.value = `解析失败: ${error.message}`
  } finally {
    parsing.value = false
  }
}

// 移除配置
const removeConfig = (index) => {
  const key = configList.value[index].key
  delete parsedConfig.value[key]
}

// 清空预览
const clearParsed = () => {
  parsedConfig.value = {}
}

// 导入
const handleImport = () => {
  emit('import', parsedConfig.value)
  ElMessage.success(`成功导入 ${Object.keys(parsedConfig.value).length} 个配置`)
  handleClose()
}

// 关闭弹窗
const handleClose = () => {
  dialogVisible.value = false
  emit('update:modelValue', false)
  yamlContent.value = ''
  parsedConfig.value = {}
  parseError.value = ''
}
</script>

<style scoped>
.input-mode-switch {
  margin-bottom: 16px;
}

.yaml-input,
.file-upload {
  margin-bottom: 16px;
}

.file-preview {
  margin-top: 12px;
}

.parse-actions {
  margin-bottom: 16px;
}

.parse-error {
  margin-bottom: 16px;
}

.parsed-preview {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preview-title {
  font-weight: 500;
  color: #303133;
}
</style>
