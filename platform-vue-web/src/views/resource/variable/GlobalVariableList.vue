<template>
  <div class="page-container">
    <div class="flex gap-4 h-full">
      <!-- 左侧：环境列表 -->
      <el-card shadow="never" class="w-64 flex-shrink-0">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-bold">环境配置</span>
            <el-button type="primary" size="small" @click="handleAddEnv">
              <el-icon><Plus /></el-icon>
            </el-button>
          </div>
        </template>
        <el-menu :default-active="currentEnv" @select="handleEnvSelect">
          <el-menu-item 
            v-for="env in envList" 
            :key="env.key" 
            :index="env.key"
          >
            <div class="flex items-center justify-between w-full">
              <span>{{ env.name }}</span>
              <el-tag size="small" :type="env.type">{{ env.key }}</el-tag>
            </div>
          </el-menu-item>
        </el-menu>
      </el-card>

      <!-- 右侧：变量编辑 -->
      <el-card shadow="never" class="flex-1 flex flex-col overflow-hidden">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="font-bold">
              {{ currentEnvName }} - 变量配置
            </span>
            <div class="space-x-2">
              <el-button size="small" @click="handleAddVariable">
                <el-icon><Plus /></el-icon>添加变量
              </el-button>
              <el-button type="primary" size="small" @click="handleSave">
                <el-icon><Check /></el-icon>保存修改
              </el-button>
              <el-button size="small" @click="handleReset">
                <el-icon><RefreshRight /></el-icon>重置
              </el-button>
              <el-dropdown @command="handleExport">
                <el-button size="small">
                  <el-icon><Download /></el-icon>导出
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="yaml">导出为 YAML</el-dropdown-item>
                    <el-dropdown-item command="json">导出为 JSON</el-dropdown-item>
                    <el-dropdown-item command="env">导出为 .env</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </template>

        <!-- 切换视图 -->
        <div class="mb-4">
          <el-radio-group v-model="viewMode" size="small">
            <el-radio-button label="table">表格模式</el-radio-button>
            <el-radio-button label="yaml">YAML 模式</el-radio-button>
          </el-radio-group>
        </div>

        <!-- 表格模式 -->
        <div v-if="viewMode === 'table'" class="flex-1 overflow-auto">
          <el-table :data="variables" border stripe>
            <el-table-column prop="key" label="变量名" width="200">
              <template #default="scope">
                <el-input 
                  v-model="scope.row.key" 
                  size="small" 
                  placeholder="变量名"
                />
              </template>
            </el-table-column>
            <el-table-column prop="value" label="变量值">
              <template #default="scope">
                <el-input 
                  v-model="scope.row.value" 
                  size="small" 
                  placeholder="变量值"
                  :type="scope.row.secret ? 'password' : 'text'"
                  :show-password="scope.row.secret"
                />
              </template>
            </el-table-column>
            <el-table-column prop="type" label="类型" width="100">
              <template #default="scope">
                <el-select v-model="scope.row.type" size="small">
                  <el-option label="字符串" value="string" />
                  <el-option label="数字" value="number" />
                  <el-option label="布尔" value="boolean" />
                  <el-option label="JSON" value="json" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column prop="secret" label="敏感" width="80" align="center">
              <template #default="scope">
                <el-switch v-model="scope.row.secret" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" width="200">
              <template #default="scope">
                <el-input 
                  v-model="scope.row.description" 
                  size="small" 
                  placeholder="变量说明"
                />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="scope">
                <el-button 
                  link 
                  type="danger" 
                  size="small"
                  @click="handleDeleteVariable(scope.$index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- YAML 模式 -->
        <div v-else class="flex-1 overflow-hidden editor-container">
          <CodeEditor 
            v-model="yamlContent" 
            mode="yaml" 
            height="100%" 
            theme="monokai"
          />
        </div>

        <!-- 使用提示 -->
        <div class="mt-4 p-3 bg-blue-50 rounded text-xs text-blue-600">
          <p><strong>使用说明：</strong></p>
          <ul class="list-disc list-inside mt-1 space-y-1">
            <li>变量可在测试用例中通过 <code class="bg-blue-100 px-1 rounded">${variable_name}</code> 引用</li>
            <li>支持嵌套引用，如 <code class="bg-blue-100 px-1 rounded">${env.db_host}</code></li>
            <li>敏感变量（如密码）会在日志中脱敏显示</li>
          </ul>
        </div>
      </el-card>
    </div>

    <!-- 新增环境弹窗 -->
    <el-dialog v-model="envDialogVisible" title="新增环境" width="400px">
      <el-form :model="newEnv" label-width="80px">
        <el-form-item label="环境名称" required>
          <el-input v-model="newEnv.name" placeholder="例如: 预发布环境" />
        </el-form-item>
        <el-form-item label="环境标识" required>
          <el-input v-model="newEnv.key" placeholder="例如: staging" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="envDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveEnv">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Check, RefreshRight, Download, ArrowDown } from '@element-plus/icons-vue'
import CodeEditor from '~/components/CodeEditor.vue'
import { getVariableList, saveVariables } from '../resource'

const viewMode = ref('table')
const currentEnv = ref('common')
const envDialogVisible = ref(false)

const envList = ref([
  { key: 'common', name: '公共配置', type: 'info' },
  { key: 'dev', name: '开发环境', type: 'success' },
  { key: 'test', name: '测试环境', type: 'warning' },
  { key: 'prod', name: '生产环境', type: 'danger' }
])

const newEnv = reactive({
  name: '',
  key: ''
})

// 各环境变量数据
const envVariables = reactive({
  common: [
    { key: 'base_url', value: 'https://api.example.com', type: 'string', secret: false, description: 'API 基础地址' },
    { key: 'timeout', value: '30000', type: 'number', secret: false, description: '请求超时时间(ms)' },
    { key: 'api_version', value: 'v1', type: 'string', secret: false, description: 'API 版本' }
  ],
  dev: [
    { key: 'db_host', value: '127.0.0.1', type: 'string', secret: false, description: '数据库地址' },
    { key: 'db_port', value: '3306', type: 'number', secret: false, description: '数据库端口' },
    { key: 'db_password', value: 'dev123456', type: 'string', secret: true, description: '数据库密码' },
    { key: 'debug', value: 'true', type: 'boolean', secret: false, description: '调试模式' }
  ],
  test: [
    { key: 'db_host', value: 'test-db.example.com', type: 'string', secret: false, description: '数据库地址' },
    { key: 'db_port', value: '3306', type: 'number', secret: false, description: '数据库端口' },
    { key: 'db_password', value: 'test123456', type: 'string', secret: true, description: '数据库密码' },
    { key: 'debug', value: 'false', type: 'boolean', secret: false, description: '调试模式' }
  ],
  prod: [
    { key: 'db_host', value: 'db.example.com', type: 'string', secret: false, description: '数据库地址' },
    { key: 'db_port', value: '3306', type: 'number', secret: false, description: '数据库端口' },
    { key: 'db_password', value: '********', type: 'string', secret: true, description: '数据库密码' },
    { key: 'debug', value: 'false', type: 'boolean', secret: false, description: '调试模式' }
  ]
})

const variables = computed(() => envVariables[currentEnv.value] || [])

const currentEnvName = computed(() => {
  const env = envList.value.find(e => e.key === currentEnv.value)
  return env?.name || currentEnv.value
})

// YAML 内容
const yamlContent = ref('')

const updateYamlContent = () => {
  const vars = envVariables[currentEnv.value] || []
  const lines = vars.map(v => {
    const comment = v.description ? `  # ${v.description}` : ''
    const value = v.secret ? '********' : v.value
    return `${v.key}: "${value}"${comment}`
  })
  yamlContent.value = lines.join('\n')
}

// 监听环境切换，更新 YAML 内容
watch(currentEnv, () => {
  updateYamlContent()
}, { immediate: true })

watch(variables, () => {
  if (viewMode.value === 'table') {
    updateYamlContent()
  }
}, { deep: true })

// 环境选择
const handleEnvSelect = (key) => {
  currentEnv.value = key
}

// 添加环境
const handleAddEnv = () => {
  newEnv.name = ''
  newEnv.key = ''
  envDialogVisible.value = true
}

const handleSaveEnv = () => {
  if (!newEnv.name || !newEnv.key) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (envList.value.some(e => e.key === newEnv.key)) {
    ElMessage.warning('环境标识已存在')
    return
  }
  envList.value.push({
    key: newEnv.key,
    name: newEnv.name,
    type: 'info'
  })
  envVariables[newEnv.key] = []
  currentEnv.value = newEnv.key
  envDialogVisible.value = false
  ElMessage.success('环境添加成功')
}

// 添加变量
const handleAddVariable = () => {
  if (!envVariables[currentEnv.value]) {
    envVariables[currentEnv.value] = []
  }
  envVariables[currentEnv.value].push({
    key: '',
    value: '',
    type: 'string',
    secret: false,
    description: ''
  })
}

// 删除变量
const handleDeleteVariable = (index) => {
  envVariables[currentEnv.value].splice(index, 1)
}

// 保存
const handleSave = async () => {
  try {
    await saveVariables({ env: currentEnv.value, variables: envVariables[currentEnv.value] })
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.success('保存成功 (Mock)')
  }
}

// 重置
const handleReset = () => {
  ElMessageBox.confirm('确定要重置当前环境的变量配置吗？', '提示', {
    type: 'warning'
  }).then(() => {
    loadData()
    ElMessage.info('配置已重置')
  })
}

// 导出
const handleExport = (format) => {
  const vars = envVariables[currentEnv.value] || []
  let content = ''
  let filename = `${currentEnv.value}-variables`
  let mimeType = 'text/plain'

  switch (format) {
    case 'yaml':
      content = vars.map(v => `${v.key}: "${v.value}"`).join('\n')
      filename += '.yaml'
      mimeType = 'text/yaml'
      break
    case 'json':
      const obj = {}
      vars.forEach(v => { obj[v.key] = v.value })
      content = JSON.stringify(obj, null, 2)
      filename += '.json'
      mimeType = 'application/json'
      break
    case 'env':
      content = vars.map(v => `${v.key}=${v.value}`).join('\n')
      filename += '.env'
      break
  }

  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

// 加载数据
const loadData = async () => {
  try {
    const res = await getVariableList()
    if (res?.data?.code === 200) {
      Object.assign(envVariables, res.data.data)
    }
  } catch (e) {
    // 使用默认 Mock 数据
  }
  updateYamlContent()
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container {
  padding: 0;
  height: calc(100vh - 140px);
}

.editor-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  height: 400px;
}

:deep(.el-menu) {
  border-right: none;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
}
</style>
