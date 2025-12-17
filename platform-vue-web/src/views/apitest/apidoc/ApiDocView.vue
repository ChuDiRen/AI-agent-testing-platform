<template>
  <div class="api-doc-container">
    <!-- 顶部工具栏 -->
    <div class="doc-toolbar">
      <div class="toolbar-left">
        <el-select v-model="selectedProjectId" placeholder="选择项目" @change="handleProjectChange" style="width: 240px;">
          <el-option
            v-for="project in projectList"
            :key="project.id"
            :label="project.project_name"
            :value="project.id"
          />
        </el-select>
        <el-button type="primary" :icon="Refresh" @click="generateDocument" :loading="loading">
          生成文档
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-dropdown @command="handleExport">
          <el-button type="success" :icon="Download">
            导出文档 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="markdown">Markdown 格式</el-dropdown-item>
              <el-dropdown-item command="json">JSON 格式</el-dropdown-item>
              <el-dropdown-item command="openapi">OpenAPI 3.0</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button :icon="View" @click="openPreview">在线预览</el-button>
      </div>
    </div>

    <!-- 文档内容区域 -->
    <div class="doc-content" v-loading="loading">
      <template v-if="docData">
        <!-- 项目信息 -->
        <div class="project-header">
          <h1>{{ docData.project?.name }} API文档</h1>
          <p class="project-desc">{{ docData.project?.description }}</p>
          <div class="project-meta">
            <span><el-icon><Document /></el-icon> 接口总数: {{ docData.api_count }}</span>
            <span><el-icon><Clock /></el-icon> 生成时间: {{ formatTime(docData.generate_time) }}</span>
          </div>
        </div>

        <!-- 目录导航 -->
        <div class="doc-sidebar">
          <h3>目录</h3>
          <el-tree
            :data="treeData"
            :props="{ label: 'name', children: 'children' }"
            @node-click="handleNodeClick"
            default-expand-all
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-tag v-if="data.method" :type="getMethodType(data.method)" size="small">
                  {{ data.method }}
                </el-tag>
                <span>{{ data.name }}</span>
              </span>
            </template>
          </el-tree>
        </div>

        <!-- 接口列表 -->
        <div class="doc-main">
          <div v-for="category in docData.categories" :key="category.id" class="category-section">
            <h2 :id="'cat-' + category.id">{{ category.name }}</h2>
            
            <div v-for="api in category.apis" :key="api.id" :id="'api-' + api.id" class="api-card">
              <div class="api-header">
                <el-tag :type="getMethodType(api.method)" size="large">{{ api.method }}</el-tag>
                <span class="api-name">{{ api.name }}</span>
                <code class="api-url">{{ api.url }}</code>
              </div>
              
              <div class="api-body">
                <!-- Query参数 -->
                <div v-if="api.params && api.params.length" class="api-section">
                  <h4>Query 参数</h4>
                  <el-table :data="api.params" border size="small">
                    <el-table-column prop="key" label="参数名" width="150" />
                    <el-table-column prop="type" label="类型" width="100">
                      <template #default="{ row }">{{ row.type || 'string' }}</template>
                    </el-table-column>
                    <el-table-column label="必填" width="80">
                      <template #default="{ row }">
                        <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                          {{ row.required ? '是' : '否' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="description" label="说明" />
                  </el-table>
                </div>

                <!-- 请求头 -->
                <div v-if="api.headers && api.headers.length" class="api-section">
                  <h4>请求头</h4>
                  <el-table :data="api.headers" border size="small">
                    <el-table-column prop="key" label="Header" width="200" />
                    <el-table-column prop="value" label="值" />
                  </el-table>
                </div>

                <!-- 请求体 -->
                <div v-if="api.body" class="api-section">
                  <h4>请求体 ({{ api.body_type || 'json' }})</h4>
                  <div class="code-block">
                    <pre><code>{{ formatBody(api.body) }}</code></pre>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <el-empty v-else description="请选择项目并生成文档" />
    </div>

    <!-- 预览弹窗 -->
    <el-dialog v-model="previewVisible" title="API文档预览" width="90%" top="5vh" fullscreen>
      <iframe v-if="previewUrl" :src="previewUrl" class="preview-iframe" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Download, View, Document, Clock, ArrowDown } from '@element-plus/icons-vue'
import { generateDoc, exportDoc } from './apiDoc'
import { queryAllProject } from '~/views/apitest/project/apiProject'

const loading = ref(false)
const selectedProjectId = ref(null)
const projectList = ref([])
const docData = ref(null)
const previewVisible = ref(false)
const previewUrl = ref('')

// 构建树形数据
const treeData = computed(() => {
  if (!docData.value?.categories) return []
  return docData.value.categories.map(cat => ({
    id: cat.id,
    name: cat.name,
    children: cat.apis.map(api => ({
      id: api.id,
      name: api.name,
      method: api.method
    }))
  }))
})

// 加载项目列表
async function loadProjects() {
  const res = await queryAllProject()
  if (res.code === 200) {
    projectList.value = res.data || []
  }
}

// 项目切换
function handleProjectChange() {
  docData.value = null
}

// 生成文档
async function generateDocument() {
  if (!selectedProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  loading.value = true
  const res = await generateDoc(selectedProjectId.value, 'json')
  loading.value = false
  if (res.code === 200) {
    docData.value = res.data
    ElMessage.success('文档生成成功')
  } else {
    ElMessage.error(res.msg || '生成失败')
  }
}

// 导出文档
async function handleExport(format) {
  if (!selectedProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  const res = await exportDoc(selectedProjectId.value, format)
  if (res.code === 200) {
    if (format === 'markdown') {
      downloadFile(res.data.content, res.data.filename, 'text/markdown')
    } else {
      downloadFile(JSON.stringify(res.data, null, 2), `api_doc.${format === 'openapi' ? 'json' : format}`, 'application/json')
    }
    ElMessage.success('导出成功')
  } else {
    ElMessage.error(res.msg || '导出失败')
  }
}

// 下载文件
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

// 打开预览
function openPreview() {
  if (!selectedProjectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  previewUrl.value = `/api/ApiDoc/preview?project_id=${selectedProjectId.value}`
  previewVisible.value = true
}

// 节点点击
function handleNodeClick(data) {
  const el = document.getElementById(data.method ? `api-${data.id}` : `cat-${data.id}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 获取请求方法对应的类型
function getMethodType(method) {
  const types = {
    GET: 'success',
    POST: 'warning',
    PUT: 'primary',
    DELETE: 'danger',
    PATCH: 'info'
  }
  return types[method] || 'info'
}

// 格式化时间
function formatTime(time) {
  if (!time) return ''
  return time.substring(0, 19).replace('T', ' ')
}

// 格式化请求体
function formatBody(body) {
  if (typeof body === 'string') {
    try {
      return JSON.stringify(JSON.parse(body), null, 2)
    } catch {
      return body
    }
  }
  return JSON.stringify(body, null, 2)
}

onMounted(() => {
  loadProjects()
})
</script>

<style scoped>
.api-doc-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.doc-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
}

.toolbar-left, .toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.doc-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  padding: 20px;
  gap: 20px;
}

.project-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.project-header h1 {
  margin: 0 0 10px 0;
  font-size: 1.8em;
}

.project-desc {
  opacity: 0.9;
  margin-bottom: 15px;
}

.project-meta {
  display: flex;
  gap: 30px;
  font-size: 0.9em;
  opacity: 0.85;
}

.project-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.doc-sidebar {
  width: 280px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
  flex-shrink: 0;
}

.doc-sidebar h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 1.1em;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
}

.doc-main {
  flex: 1;
  overflow-y: auto;
}

.category-section {
  margin-bottom: 30px;
}

.category-section h2 {
  color: #303133;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

.api-card {
  background: white;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.api-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 20px;
  background: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.api-name {
  font-weight: 600;
  font-size: 1.05em;
  color: #303133;
}

.api-url {
  color: #909399;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.9em;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
}

.api-body {
  padding: 20px;
}

.api-section {
  margin-bottom: 20px;
}

.api-section:last-child {
  margin-bottom: 0;
}

.api-section h4 {
  color: #606266;
  margin: 0 0 12px 0;
  font-size: 0.95em;
}

.code-block {
  background: #2d2d2d;
  border-radius: 6px;
  overflow: auto;
}

.code-block pre {
  margin: 0;
  padding: 15px;
}

.code-block code {
  color: #f8f8f2;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.85em;
  white-space: pre-wrap;
}

.preview-iframe {
  width: 100%;
  height: calc(100vh - 150px);
  border: none;
}

:deep(.el-empty) {
  height: 100%;
}
</style>
