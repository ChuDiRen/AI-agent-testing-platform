<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="插件名称">
        <el-input v-model="searchForm.plugin_name" placeholder="输入插件名称" clearable />
      </el-form-item>
      <el-form-item label="插件类型">
        <el-select v-model="searchForm.plugin_type" placeholder="全部" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option label="执行器" value="executor" />
          <el-option label="工具" value="tool" />
          <el-option label="扩展" value="extension" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.is_enabled" placeholder="全部" clearable style="width: 100px">
          <el-option label="全部" value="" />
          <el-option label="已启用" :value="1" />
          <el-option label="已禁用" :value="0" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <!-- 表格区域 -->
    <BaseTable
      title="插件市场"
      :data="tableData"
      :loading="loading"
      :total="pagination.total"
      v-model:pagination="paginationModel"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="executorUploadVisible = true">
          <el-icon style="margin-right: 4px"><Upload /></el-icon>
          上传执行器
        </el-button>
      </template>

      <el-table-column type="index" label="序号" width="60" align="center" />
      <el-table-column prop="plugin_name" label="插件名称" min-width="150">
        <template #default="{ row }">
          <el-tag :type="row.plugin_type === 'executor' ? 'success' : 'info'">
            {{ row.plugin_name }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="plugin_code" label="插件代码" width="130" />
      <el-table-column prop="plugin_type" label="类型" width="90" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.plugin_type === 'executor'" type="success" size="small">执行器</el-tag>
          <el-tag v-else-if="row.plugin_type === 'tool'" type="warning" size="small">工具</el-tag>
          <el-tag v-else type="info" size="small">扩展</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="version" label="版本" width="80" align="center" />
      <el-table-column prop="command" label="执行命令" min-width="120" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column prop="install_status" label="安装状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.install_status === 'installed'" type="success" size="small">已安装</el-tag>
          <el-tag v-else-if="row.install_status === 'installing'" type="warning" size="small">安装中</el-tag>
          <el-tag v-else-if="row.install_status === 'install_failed'" type="danger" size="small">安装失败</el-tag>
          <el-tag v-else type="info" size="small">未安装</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_enabled" label="启用" width="70" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_enabled"
            :active-value="1"
            :inactive-value="0"
            @change="handleToggle(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">详情</el-button>
          <el-button link type="primary" @click="handleHealthCheck(row)">检测</el-button>
          <el-button 
            v-if="row.plugin_content && row.install_status !== 'installed'" 
            link 
            type="success" 
            @click="handleInstall(row)"
            :disabled="row.install_status === 'installing'"
          >
            {{ row.install_status === 'installing' ? '安装中...' : '安装' }}
          </el-button>
          <el-button 
            v-if="row.install_status === 'installed'" 
            link 
            type="warning" 
            @click="handleUninstall(row)"
          >卸载</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 插件详情对话框 -->
    <el-dialog v-model="detailVisible" title="插件详情" width="600px">
      <el-descriptions v-if="currentPlugin" :column="2" border>
        <el-descriptions-item label="插件名称">{{ currentPlugin.plugin_name }}</el-descriptions-item>
        <el-descriptions-item label="插件代码">{{ currentPlugin.plugin_code }}</el-descriptions-item>
        <el-descriptions-item label="插件类型">
          <el-tag v-if="currentPlugin.plugin_type === 'executor'" type="success">执行器</el-tag>
          <el-tag v-else-if="currentPlugin.plugin_type === 'tool'" type="warning">工具</el-tag>
          <el-tag v-else type="info">扩展</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="版本">{{ currentPlugin.version }}</el-descriptions-item>
        <el-descriptions-item label="执行命令" :span="2">
          <code>{{ currentPlugin.command || '-' }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ currentPlugin.author || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentPlugin.is_enabled === 1 ? 'success' : 'danger'">
            {{ currentPlugin.is_enabled === 1 ? '已启用' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentPlugin.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="参数配置" :span="2">
          <template v-if="currentPluginParams.length">
            <div v-for="param in currentPluginParams" :key="param.name" class="param-item">
              <el-tag size="small" type="info">{{ param.name }}</el-tag>
              <span class="param-label">{{ param.label || param.name }}</span>
              <span class="param-type">({{ param.type || 'string' }})</span>
              <span v-if="param.default" class="param-default">默认: {{ param.default }}</span>
            </div>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="依赖" :span="2">
          <template v-if="currentPlugin.dependencies && currentPlugin.dependencies.length">
            <el-tag v-for="(dep, index) in parseDependencies(currentPlugin.dependencies)" :key="index" style="margin: 2px;">
              {{ dep }}
            </el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ currentPlugin.create_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="修改时间">{{ currentPlugin.modify_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="安装状态">
          <el-tag v-if="currentPlugin.install_status === 'installed'" type="success">已安装</el-tag>
          <el-tag v-else-if="currentPlugin.install_status === 'installing'" type="warning">安装中</el-tag>
          <el-tag v-else-if="currentPlugin.install_status === 'install_failed'" type="danger">安装失败</el-tag>
          <el-tag v-else type="info">未安装</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="健康状态">
          <el-tag v-if="currentPlugin.health_status === 'healthy'" type="success">健康</el-tag>
          <el-tag v-else-if="currentPlugin.health_status === 'unhealthy'" type="danger">不健康</el-tag>
          <el-tag v-else-if="currentPlugin.health_status === 'degraded'" type="warning">降级</el-tag>
          <el-tag v-else type="info">未知</el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentPlugin.venv_path" label="虚拟环境" :span="2">
          <code>{{ currentPlugin.venv_path }}</code>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentPlugin.install_time" label="安装时间">
          {{ currentPlugin.install_time }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- 安装进度对话框 -->
    <el-dialog v-model="installDialogVisible" title="安装执行器" width="450px" :close-on-click-modal="false" :close-on-press-escape="false" :show-close="!installLoading">
      <div style="padding: 20px 0;">
        <div style="margin-bottom: 15px; color: #606266;">
          <el-icon v-if="installLoading" class="is-loading" style="margin-right: 8px;"><Loading /></el-icon>
          {{ installMessage }}
        </div>
        <el-progress :percentage="installProgress" :status="installStatus === 'completed' ? 'success' : installStatus === 'failed' ? 'exception' : ''" />
      </div>
      <template #footer v-if="!installLoading">
        <el-button type="primary" @click="installDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <!-- 上传执行器对话框 -->
    <el-dialog v-model="executorUploadVisible" title="上传执行器" width="600px">
      <div class="upload-container">
        <el-alert
          title="执行器要求"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 15px"
        >
          <template #default>
            执行器需包含 <code>setup.py</code> 文件，并在 <code>entry_points.console_scripts</code> 中定义命令。
            上传后存入数据库，点击"安装"后可通过命令行使用。
          </template>
        </el-alert>

        <div class="upload-section">
          <div class="section-title">方式一：上传 ZIP 包</div>
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :http-request="handleExecutorUpload"
            :show-file-list="false"
            accept=".zip"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽执行器 ZIP 到此处或 <em>点击上传</em>
            </div>
          </el-upload>
        </div>

        <div class="divider">
          <span>OR</span>
        </div>

        <div class="upload-section">
          <div class="section-title">方式二：选择执行器目录</div>
          <div class="folder-upload-box" @click="triggerExecutorFolderSelect">
            <el-icon class="folder-icon"><Folder /></el-icon>
            <div class="upload-text">点击选择执行器文件夹</div>
            <div class="upload-tip">自动压缩并上传</div>
          </div>
          <input 
            type="file" 
            ref="executorFolderInput" 
            webkitdirectory 
            style="display:none" 
            @change="handleExecutorFolderChange"
          >
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Upload, UploadFilled, Folder, Loading } from '@element-plus/icons-vue'
import JSZip from 'jszip'
import { queryByPage, togglePlugin, unregisterPlugin, healthCheck, uploadExecutor, installExecutor, getInstallStatus, uninstallExecutor } from './plugin.js'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'

// 搜索表单
const searchForm = reactive({
  plugin_name: '',
  plugin_type: '',
  is_enabled: ''
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 分页模型（适配 BaseTable）
const paginationModel = computed({
  get: () => ({ page: pagination.page, limit: pagination.page_size }),
  set: (val) => {
    pagination.page = val.page
    pagination.page_size = val.limit
  }
})

// 对话框控制
const detailVisible = ref(false)
const executorUploadVisible = ref(false)
const currentPlugin = ref(null)
const executorFolderInput = ref(null)

// 当前插件的参数列表
const currentPluginParams = computed(() => {
  if (!currentPlugin.value?.config_schema) return []
  let schema = currentPlugin.value.config_schema
  if (typeof schema === 'string') {
    try {
      schema = JSON.parse(schema)
    } catch {
      return []
    }
  }
  return schema?.params || []
})

// 安装进度
const installDialogVisible = ref(false)
const installProgress = ref(0)
const installMessage = ref('')
const installStatus = ref('')
const installLoading = ref(false)

// 上传执行器文件
const uploadExecutorFile = async (file) => {
  const loadingInstance = ElLoading.service({ text: '正在上传执行器...' })
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await uploadExecutor(formData)
    loadingInstance.close()
    
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '执行器上传成功')
      executorUploadVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.data.msg || '上传失败')
    }
  } catch (error) {
    loadingInstance.close()
    ElMessage.error('上传失败: ' + error.message)
  }
}

// 处理执行器 ZIP 上传
const handleExecutorUpload = (options) => {
  uploadExecutorFile(options.file)
}

// 触发执行器文件夹选择
const triggerExecutorFolderSelect = () => {
  executorFolderInput.value?.click()
}

// 处理执行器文件夹选择
const handleExecutorFolderChange = async (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  const loadingInstance = ElLoading.service({ text: '正在压缩执行器...' })
  try {
    const zip = new JSZip()
    const rootFolderName = files[0].webkitRelativePath.split('/')[0]
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      zip.file(file.webkitRelativePath, file)
    }
    
    const content = await zip.generateAsync({ type: 'blob' })
    const zipFile = new File([content], `${rootFolderName}.zip`, { type: 'application/zip' })
    
    loadingInstance.close()
    uploadExecutorFile(zipFile)
    
  } catch (error) {
    loadingInstance.close()
    ElMessage.error('压缩失败: ' + error.message)
  } finally {
    event.target.value = ''
  }
}

// 安装执行器（异步轮询）
const handleInstall = async (row) => {
  // 初始化进度对话框
  installDialogVisible.value = true
  installProgress.value = 0
  installMessage.value = '正在启动安装...'
  installStatus.value = 'installing'
  installLoading.value = true
  
  try {
    const res = await installExecutor(row.id)
    if (res.data.code !== 200) {
      installMessage.value = res.data.msg || '启动安装失败'
      installStatus.value = 'failed'
      installProgress.value = 100
      installLoading.value = false
      return
    }
    
    // 轮询安装状态
    let pollRetryCount = 0
    const maxPollRetries = 5  // 增加重试次数
    let pollTimer = null
    let lastProgress = 0
    let sameProgressCount = 0
    const maxSameProgressCount = 30  // 进度卡住30次（约30秒）后刷新数据
    
    const stopPolling = () => {
      if (pollTimer) {
        clearTimeout(pollTimer)
        pollTimer = null
      }
      installLoading.value = false
    }
    
    const pollStatus = async () => {
      try {
        const statusRes = await getInstallStatus(row.id)
        if (statusRes.data.code === 200) {
          const status = statusRes.data.data?.status
          const message = statusRes.data.data?.message || ''
          const progress = statusRes.data.data?.progress || 0
          
          installMessage.value = message || '正在安装执行器...'
          installProgress.value = progress
          installStatus.value = status
          
          if (status === 'installing') {
            pollRetryCount = 0 // 只在 installing 时重置
            
            // 检测进度是否卡住
            if (progress === lastProgress) {
              sameProgressCount++
              // 进度卡住超过阈值，尝试刷新数据检查是否已完成
              if (sameProgressCount >= maxSameProgressCount) {
                sameProgressCount = 0
                // 刷新列表数据检查实际状态
                await loadData()
                // 继续轮询
              }
            } else {
              sameProgressCount = 0
              lastProgress = progress
            }
            
            pollTimer = setTimeout(pollStatus, 1000)
          } else if (status === 'completed') {
            stopPolling()
            ElMessage.success(message || '安装成功')
            loadData()
          } else if (status === 'failed') {
            stopPolling()
          } else if (status === 'unknown') {
            // 未找到安装任务，可能已完成或服务重启
            pollRetryCount++
            if (pollRetryCount < maxPollRetries) {
              pollTimer = setTimeout(pollStatus, 1000)
            } else {
              // 多次查询都是 unknown，刷新数据检查实际状态
              installMessage.value = '正在检查安装结果...'
              await loadData()
              stopPolling()
            }
          } else {
            stopPolling()
            installMessage.value = '安装状态未知'
          }
        } else {
          installMessage.value = '查询安装状态失败'
          installStatus.value = 'failed'
          installProgress.value = 100
          stopPolling()
        }
      } catch (error) {
        installMessage.value = '查询安装状态失败: ' + error.message
        installStatus.value = 'failed'
        installProgress.value = 100
        stopPolling()
      }
    }
    
    // 开始轮询
    pollTimer = setTimeout(pollStatus, 500)
    
  } catch (error) {
    installMessage.value = '安装失败: ' + error.message
    installStatus.value = 'failed'
    installProgress.value = 100
    installLoading.value = false
  }
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      pageNum: pagination.page,
      pageSize: pagination.page_size,
      ...(searchForm.plugin_name && { plugin_name: searchForm.plugin_name }),
      ...(searchForm.plugin_type && { plugin_type: searchForm.plugin_type }),
      ...(searchForm.is_enabled !== '' && { is_enabled: searchForm.is_enabled })
    }
    const res = await queryByPage(params)
    if (res.data.code === 200) {
      tableData.value = res.data.data?.rows || []
      pagination.total = res.data.data?.total || 0
    } else {
      ElMessage.error(res.data.msg || '查询失败')
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.plugin_name = ''
  searchForm.plugin_type = ''
  searchForm.is_enabled = ''
  handleSearch()
}

// 启用/禁用插件
const handleToggle = async (row) => {
  try {
    const res = await togglePlugin(row.id)
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '操作成功')
      loadData()
    } else {
      row.is_enabled = row.is_enabled === 1 ? 0 : 1
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    row.is_enabled = row.is_enabled === 1 ? 0 : 1
    ElMessage.error('操作失败')
  }
}

// 查看详情
const handleView = (row) => {
  currentPlugin.value = row
  detailVisible.value = true
}

// 健康检查
const handleHealthCheck = async (row) => {
  const loadingInstance = ElLoading.service({ text: '正在检测插件...' })
  try {
    const res = await healthCheck(row.id)
    loadingInstance.close()
    if (res.data.code === 200) {
      ElMessage.success('插件运行正常')
    } else {
      ElMessage.error(res.data.msg || '插件检测失败')
    }
  } catch (error) {
    loadingInstance.close()
    ElMessage.error('插件检测失败')
  }
}

// 卸载执行器
const handleUninstall = (row) => {
  ElMessageBox.confirm(`确定要卸载执行器 "${row.plugin_name}" 吗？\n这将删除安装目录和虚拟环境，但保留数据库记录。`, '确认卸载', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    const loadingInstance = ElLoading.service({ text: '正在卸载...' })
    try {
      const res = await uninstallExecutor(row.id)
      loadingInstance.close()
      if (res.data.code === 200) {
        ElMessage.success('卸载成功')
        loadData()
      } else {
        ElMessage.error(res.data.msg || '卸载失败')
      }
    } catch (error) {
      loadingInstance.close()
      ElMessage.error('卸载失败: ' + error.message)
    }
  })
}

// 删除插件
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除插件 "${row.plugin_name}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await unregisterPlugin(row.id)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        loadData()
      } else {
        ElMessage.error(res.data.msg || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 格式化能力描述
const formatCapabilities = (caps) => {
  try {
    if (!caps) return '-'
    const data = typeof caps === 'string' ? JSON.parse(caps) : caps
    return JSON.stringify(data, null, 2)
  } catch {
    return String(caps)
  }
}

// 解析依赖
const parseDependencies = (deps) => {
  try {
    if (!deps) return []
    return typeof deps === 'string' ? JSON.parse(deps) : deps
  } catch {
    return []
  }
}

// 初始化
onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '~/styles/common-list.css';

code {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.json-pre {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  margin: 0;
  max-height: 200px;
}

.upload-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-section {
  border: 1px dashed var(--border-color);
  border-radius: 8px;
  padding: 20px;
  background-color: var(--bg-page);
  transition: all 0.3s;
}

.upload-section:hover {
  border-color: var(--color-primary);
}

.section-title {
  font-weight: bold;
  margin-bottom: 15px;
  color: var(--text-primary);
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: var(--text-secondary);
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--border-color);
}

.divider span {
  padding: 0 10px;
  font-size: 12px;
}

.folder-upload-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 180px;
  cursor: pointer;
  border-radius: 6px;
  background-color: #fff;
  border: 1px dashed #d9d9d9;
  transition: border-color .3s;
}

.folder-upload-box:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.folder-icon {
  font-size: 48px;
  margin-bottom: 10px;
  color: #8c939d;
}

.upload-text {
  font-size: 14px;
  color: #606266;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.param-label {
  font-weight: 500;
}

.param-type {
  color: #909399;
  font-size: 12px;
}

.param-default {
  color: #67c23a;
  font-size: 12px;
}
</style>
