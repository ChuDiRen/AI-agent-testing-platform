<template>
  <div class="page-container">
    <!-- 搜索区域 -->
    <BaseSearch :model="searchForm" :loading="loading" @search="handleSearch" @reset="handleReset">
      <el-form-item label="插件名称">
        <el-input v-model="searchForm.plugin_name" placeholder="输入插件名称" clearable />
      </el-form-item>
      <el-form-item label="插件类型">
        <el-select v-model="searchForm.plugin_type" placeholder="全部" clearable>
          <el-option label="全部" value="" />
          <el-option label="执行器" value="executor" />
          <el-option label="工具" value="tool" />
          <el-option label="扩展" value="extension" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.is_enabled" placeholder="全部" clearable>
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
        <el-button type="primary" @click="uploadVisible = true">
          <el-icon style="margin-right: 4px"><Upload /></el-icon>
          安装插件
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
      <el-table-column prop="command" label="执行命令" min-width="180" show-overflow-tooltip />
      <el-table-column prop="storage_path" label="存储路径" min-width="220" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      <el-table-column prop="is_enabled" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.is_enabled"
            :active-value="1"
            :inactive-value="0"
            @change="handleToggle(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">详情</el-button>
          <el-button link type="primary" @click="handleHealthCheck(row)">检测</el-button>
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
        <el-descriptions-item label="存储路径" :span="2">
          <code>{{ currentPlugin.storage_path || '-' }}</code>
        </el-descriptions-item>
        <el-descriptions-item label="作者">{{ currentPlugin.author || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentPlugin.is_enabled === 1 ? 'success' : 'danger'">
            {{ currentPlugin.is_enabled === 1 ? '已启用' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentPlugin.description || '-' }}</el-descriptions-item>
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
      </el-descriptions>
    </el-dialog>

    <!-- 上传插件对话框 -->
    <el-dialog v-model="uploadVisible" title="安装插件" width="600px">
      <div class="upload-container">
        <div class="upload-section">
          <div class="section-title">方式一：上传 ZIP 包</div>
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :http-request="handleUpload"
            :show-file-list="false"
            accept=".zip"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽 ZIP 文件到此处或 <em>点击上传</em>
            </div>
          </el-upload>
        </div>

        <div class="divider">
          <span>OR</span>
        </div>

        <div class="upload-section">
          <div class="section-title">方式二：上传插件目录</div>
          <div class="folder-upload-box" @click="triggerFolderSelect">
            <el-icon class="folder-icon"><Folder /></el-icon>
            <div class="upload-text">点击选择插件文件夹</div>
            <div class="upload-tip">自动压缩并上传</div>
          </div>
          <input 
            type="file" 
            ref="folderInput" 
            webkitdirectory 
            style="display:none" 
            @change="handleFolderChange"
          >
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Upload, UploadFilled, Folder } from '@element-plus/icons-vue'
import JSZip from 'jszip'
import { queryByPage, togglePlugin, unregisterPlugin, healthCheck, uploadPlugin } from './plugin.js'
import BaseSearch from '@/components/BaseSearch/index.vue'
import BaseTable from '@/components/BaseTable/index.vue'

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
const uploadVisible = ref(false)
const currentPlugin = ref(null)
const folderInput = ref(null)

// 通用上传逻辑
const uploadFile = async (file) => {
  const loadingInstance = ElLoading.service({ text: '正在上传并安装插件...' })
  try {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await uploadPlugin(formData)
    loadingInstance.close()
    
    if (res.data.code === 200) {
      ElMessage.success(res.data.msg || '插件安装成功')
      uploadVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.data.msg || '安装失败')
    }
  } catch (error) {
    loadingInstance.close()
    ElMessage.error('上传失败: ' + error.message)
  }
}

// 处理 ZIP 上传 (el-upload)
const handleUpload = (options) => {
  uploadFile(options.file)
}

// 触发文件夹选择
const triggerFolderSelect = () => {
  folderInput.value?.click()
}

// 处理文件夹选择
const handleFolderChange = async (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  const loadingInstance = ElLoading.service({ text: '正在压缩文件夹...' })
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
    uploadFile(zipFile)
    
  } catch (error) {
    loadingInstance.close()
    ElMessage.error('压缩文件夹失败: ' + error.message)
  } finally {
    event.target.value = ''
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
</style>
