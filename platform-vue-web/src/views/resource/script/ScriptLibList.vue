<template>
  <div class="page-container">
    <BaseSearch :model="searchForm" @search="loadData" @reset="resetSearch">
      <el-form-item label="脚本名称">
        <el-input v-model="searchForm.name" placeholder="请输入脚本名称" clearable />
      </el-form-item>
      <el-form-item label="脚本类型">
        <el-select v-model="searchForm.type" placeholder="全部" clearable>
          <el-option label="Python" value="python" />
          <el-option label="JavaScript" value="javascript" />
          <el-option label="Shell" value="shell" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="脚本库管理"
      :data="tableData"
      :total="total"
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
      @selection-change="handleSelectionChange"
      type="selection"
    >
      <template #header>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>新建脚本
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>导入脚本
        </el-button>
        <el-button 
          type="danger" 
          :disabled="selectedRows.length === 0"
          @click="handleBatchDelete"
        >
          <el-icon><Delete /></el-icon>
          批量删除 ({{ selectedRows.length }})
        </el-button>
      </template>

      <el-table-column prop="name" label="脚本名称" width="200">
        <template #default="scope">
          <div class="flex items-center gap-2">
            <el-icon :class="getScriptIconClass(scope.row.type)">
              <Document />
            </el-icon>
            <span class="text-blue-600 cursor-pointer hover:underline" @click="handleEdit(scope.row)">
              {{ scope.row.name }}
            </span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="100">
        <template #default="scope">
          <el-tag size="small" :type="getScriptTypeTag(scope.row.type)">
            {{ scope.row.type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="功能说明" show-overflow-tooltip />
      <el-table-column prop="author" label="作者" width="100" />
      <el-table-column prop="version" label="版本" width="80" />
      <el-table-column prop="update_time" label="最后修改" width="180" />
      <el-table-column fixed="right" label="操作" width="200">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="primary" @click="handleRun(scope.row)">运行</el-button>
          <el-button link type="primary" @click="handleExport(scope.row)">导出</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 脚本编辑弹窗 -->
    <el-dialog 
      v-model="editorVisible" 
      :title="currentScript.id ? '编辑脚本' : '新建脚本'" 
      width="900px"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="currentScript" label-width="100px" class="mb-4">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="脚本名称" required>
              <el-input v-model="currentScript.name" placeholder="例如: utils.py" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="脚本类型" required>
              <el-select v-model="currentScript.type" class="w-full">
                <el-option label="Python" value="python" />
                <el-option label="JavaScript" value="javascript" />
                <el-option label="Shell" value="shell" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="功能说明">
          <el-input v-model="currentScript.description" placeholder="请输入脚本功能说明" />
        </el-form-item>
      </el-form>
      
      <div class="editor-container">
        <CodeEditor 
          v-model="currentScript.content" 
          :mode="getEditorMode(currentScript.type)" 
          height="400px"
          theme="monokai"
        />
      </div>

      <template #footer>
        <el-button @click="editorVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 运行结果弹窗 -->
    <el-dialog v-model="runResultVisible" title="运行结果" width="700px">
      <div class="run-result">
        <div class="flex items-center gap-2 mb-4">
          <el-tag :type="runResult.success ? 'success' : 'danger'">
            {{ runResult.success ? '运行成功' : '运行失败' }}
          </el-tag>
          <span class="text-gray-500 text-sm">耗时: {{ runResult.duration }}ms</span>
        </div>
        <pre class="result-output">{{ runResult.output }}</pre>
      </div>
    </el-dialog>

    <!-- 导入弹窗 -->
    <el-dialog v-model="importVisible" title="导入脚本" width="500px">
      <el-upload
        drag
        :auto-upload="false"
        :on-change="handleImportFile"
        accept=".py,.js,.sh"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽脚本文件到此处 或 <em>点击选择</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 .py, .js, .sh 格式文件
          </div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Delete, Document, UploadFilled } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import CodeEditor from '~/components/CodeEditor.vue'
import { getScriptList, deleteScript, batchDeleteScript, saveScript, runScript } from '../resource'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const selectedRows = ref([])
const editorVisible = ref(false)
const runResultVisible = ref(false)
const importVisible = ref(false)

const searchForm = reactive({
  name: '',
  type: ''
})

const pagination = reactive({
  page: 1,
  limit: 10
})

const currentScript = reactive({
  id: null,
  name: '',
  type: 'python',
  description: '',
  content: ''
})

const runResult = reactive({
  success: true,
  duration: 0,
  output: ''
})

// 默认脚本模板
const scriptTemplates = {
  python: `# -*- coding: utf-8 -*-
"""
脚本说明: 
作者: 
创建时间: 
"""

def main():
    """主函数"""
    print("Hello, World!")
    return True

if __name__ == "__main__":
    main()
`,
  javascript: `/**
 * 脚本说明: 
 * 作者: 
 * 创建时间: 
 */

function main() {
  console.log("Hello, World!");
  return true;
}

module.exports = { main };
`,
  shell: `#!/bin/bash
# 脚本说明: 
# 作者: 
# 创建时间: 

echo "Hello, World!"
exit 0
`
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getScriptList({ ...searchForm, ...pagination })
    if (res?.data?.code === 200) {
      tableData.value = res.data.data.list
      total.value = res.data.data.total
    } else {
      mockData()
    }
  } catch (e) {
    mockData()
  } finally {
    loading.value = false
  }
}

const mockData = () => {
  tableData.value = [
    { id: 1, name: 'utils.py', type: 'python', description: '通用工具函数库', author: 'admin', version: '1.0.0', update_time: '2026-01-05 09:00:00', content: scriptTemplates.python },
    { id: 2, name: 'db_handler.py', type: 'python', description: '自定义数据库操作逻辑', author: 'dev', version: '1.2.0', update_time: '2026-01-04 16:45:00', content: scriptTemplates.python },
    { id: 3, name: 'api_helper.js', type: 'javascript', description: 'API 请求封装', author: 'tester', version: '2.0.0', update_time: '2026-01-03 11:30:00', content: scriptTemplates.javascript },
    { id: 4, name: 'deploy.sh', type: 'shell', description: '自动化部署脚本', author: 'ops', version: '1.0.0', update_time: '2026-01-02 14:20:00', content: scriptTemplates.shell }
  ]
  total.value = 4
}

const resetSearch = () => {
  Object.assign(searchForm, { name: '', type: '' })
  loadData()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const getScriptIconClass = (type) => {
  const colors = {
    python: 'text-blue-500',
    javascript: 'text-yellow-500',
    shell: 'text-green-500'
  }
  return colors[type] || 'text-gray-500'
}

const getScriptTypeTag = (type) => {
  const tags = {
    python: 'primary',
    javascript: 'warning',
    shell: 'success'
  }
  return tags[type] || 'info'
}

const getEditorMode = (type) => {
  const modes = {
    python: 'python',
    javascript: 'javascript',
    shell: 'shell'
  }
  return modes[type] || 'text'
}

// 新建脚本
const handleCreate = () => {
  Object.assign(currentScript, {
    id: null,
    name: '',
    type: 'python',
    description: '',
    content: scriptTemplates.python
  })
  editorVisible.value = true
}

// 编辑脚本
const handleEdit = (row) => {
  Object.assign(currentScript, row)
  editorVisible.value = true
}

// 保存脚本
const handleSave = async () => {
  if (!currentScript.name) {
    ElMessage.warning('请输入脚本名称')
    return
  }
  try {
    await saveScript(currentScript)
    ElMessage.success('保存成功')
    editorVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.success('保存成功 (Mock)')
    editorVisible.value = false
    loadData()
  }
}

// 运行脚本
const handleRun = async (row) => {
  ElMessage.info('正在运行脚本...')
  try {
    const res = await runScript(row.id)
    if (res?.data?.code === 200) {
      Object.assign(runResult, res.data.data)
    } else {
      mockRunResult()
    }
  } catch (e) {
    mockRunResult()
  }
  runResultVisible.value = true
}

const mockRunResult = () => {
  Object.assign(runResult, {
    success: true,
    duration: Math.floor(Math.random() * 1000) + 100,
    output: `Hello, World!
Script executed successfully.
Exit code: 0`
  })
}

// 导出脚本
const handleExport = (row) => {
  const blob = new Blob([row.content || ''], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = row.name
  link.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

// 导入脚本
const handleImport = () => {
  importVisible.value = true
}

const handleImportFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    const name = file.name
    const type = name.endsWith('.py') ? 'python' : name.endsWith('.js') ? 'javascript' : 'shell'
    
    Object.assign(currentScript, {
      id: null,
      name,
      type,
      description: '',
      content
    })
    importVisible.value = false
    editorVisible.value = true
  }
  reader.readAsText(file.raw)
}

// 删除脚本
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除脚本 "${row.name}" 吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteScript(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('删除成功 (Mock)')
      tableData.value = tableData.value.filter(item => item.id !== row.id)
      total.value--
    }
  })
}

// 批量删除
const handleBatchDelete = () => {
  const ids = selectedRows.value.map(row => row.id)
  ElMessageBox.confirm(`确定要删除选中的 ${ids.length} 个脚本吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await batchDeleteScript(ids)
      ElMessage.success('批量删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('批量删除成功 (Mock)')
      tableData.value = tableData.value.filter(row => !ids.includes(row.id))
      total.value -= ids.length
    }
  })
}

onMounted(() => loadData())
</script>

<style scoped>
.page-container {
  padding: 0;
}

.editor-container {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.result-output {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
}
</style>
