<template>
  <div class="suite-detail-container">
    <el-page-header @back="goBack">
      <template #content>
        <span class="suite-title">{{ store.currentSuite?.name || '套件详情' }}</span>
      </template>
      <template #extra>
        <el-button type="primary" @click="showCreateCaseDialog = true">
          <el-icon><Plus /></el-icon>
          创建用例
        </el-button>
        <el-button @click="showImportDialog = true">
          <el-icon><Upload /></el-icon>
          导入YAML
        </el-button>
      </template>
    </el-page-header>

    <el-card class="suite-info-card" v-if="store.currentSuite">
      <h3>套件信息</h3>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="套件名称">{{ store.currentSuite.name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(store.currentSuite.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ store.currentSuite.description || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="case-list-card">
      <template #header>
        <div class="card-header">
          <h3>测试用例列表</h3>
          <div class="actions">
            <el-input
              v-model="searchName"
              placeholder="搜索用例名称"
              clearable
              style="width: 200px"
              @clear="loadCases"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="loadCases">搜索</el-button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="store.casesLoading"
        :data="cases"
        border
        style="width: 100%"
      >
        <el-table-column prop="case_id" label="ID" width="80" />
        <el-table-column prop="name" label="用例名称" min-width="200" />
        <el-table-column prop="config_mode" label="配置模式" width="100">
          <template #default="{ row }">
            <el-tag :type="row.config_mode === 'form' ? 'success' : 'info'">
              {{ row.config_mode === 'form' ? '表单' : 'YAML' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDate(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="handleExecuteCase(row.case_id)">
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button size="small" @click="handleEditCase(row.case_id)">编辑</el-button>
            <el-button size="small" @click="handleCloneCase(row.case_id)">克隆</el-button>
            <el-popconfirm
              title="确定要删除这个用例吗?"
              @confirm="handleDeleteCase(row.case_id)"
            >
              <template #reference>
                <el-button size="small" type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建用例对话框 -->
    <el-dialog v-model="showCreateCaseDialog" title="创建用例" width="600px">
      <el-form ref="caseFormRef" :model="caseFormData" :rules="caseRules" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="caseFormData.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="配置模式" prop="config_mode">
          <el-radio-group v-model="caseFormData.config_mode">
            <el-radio label="form">表单模式</el-radio>
            <el-radio label="yaml">YAML模式</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="caseFormData.priority">
            <el-option label="P0" value="P0" />
            <el-option label="P1" value="P1" />
            <el-option label="P2" value="P2" />
            <el-option label="P3" value="P3" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="caseFormData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入用例描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateCaseDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleCreateCase">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 导入YAML对话框 -->
    <el-dialog v-model="showImportDialog" title="导入YAML用例" width="700px">
      <el-form label-width="100px">
        <el-form-item label="用例名称">
          <el-input v-model="importData.name" placeholder="可选,不填则从YAML中提取" />
        </el-form-item>
        <el-form-item label="YAML内容">
          <el-input
            v-model="importData.yaml_content"
            type="textarea"
            :rows="15"
            placeholder="请粘贴YAML内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" :loading="importing" @click="handleImportYaml">
          导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Upload, Search, VideoPlay } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import type { Case } from '../api'

const route = useRoute()
const router = useRouter()
const store = useApiEngineStore()

const suiteId = computed(() => Number(route.params.id))
const searchName = ref('')
const showCreateCaseDialog = ref(false)
const showImportDialog = ref(false)
const submitting = ref(false)
const importing = ref(false)
const caseFormRef = ref()

const cases = computed(() => store.getCasesBySuiteId(suiteId.value))

const caseFormData = reactive<Case>({
  suite_id: suiteId.value,
  name: '',
  description: '',
  config_mode: 'form',
  priority: 'P2',
  status: 'draft'
})

const importData = reactive({
  name: '',
  yaml_content: ''
})

const caseRules = {
  name: [
    { required: true, message: '请输入用例名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  config_mode: [{ required: true, message: '请选择配置模式', trigger: 'change' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

const goBack = () => {
  router.push('/plugin/api-engine/suites')
}

const loadCases = async () => {
  await store.fetchCases({
    suite_id: suiteId.value,
    name: searchName.value || undefined
  })
}

const handleCreateCase = async () => {
  if (!caseFormRef.value) return

  await caseFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        const newCase = await store.createCase(caseFormData)
        ElMessage.success('创建成功')
        showCreateCaseDialog.value = false
        // 跳转到编辑页面
        router.push(`/plugin/api-engine/cases/${newCase.case_id}/edit`)
      } catch (error: any) {
        ElMessage.error(error.message || '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleImportYaml = async () => {
  if (!importData.yaml_content.trim()) {
    ElMessage.warning('请输入YAML内容')
    return
  }

  importing.value = true
  try {
    await store.importYaml({
      suite_id: suiteId.value,
      yaml_content: importData.yaml_content,
      name: importData.name || undefined
    })
    ElMessage.success('导入成功')
    showImportDialog.value = false
    importData.name = ''
    importData.yaml_content = ''
    await loadCases()
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

const handleExecuteCase = (caseId?: number) => {
  if (!caseId) return
  router.push(`/plugin/api-engine/executions/${caseId}`)
}

const handleEditCase = (caseId?: number) => {
  if (!caseId) return
  router.push(`/plugin/api-engine/cases/${caseId}/edit`)
}

const handleCloneCase = async (caseId?: number) => {
  if (!caseId) return
  try {
    await store.cloneCase(caseId)
    ElMessage.success('克隆成功')
    await loadCases()
  } catch (error: any) {
    ElMessage.error(error.message || '克隆失败')
  }
}

const handleDeleteCase = async (caseId?: number) => {
  if (!caseId) return
  try {
    await store.deleteCase(caseId)
    ElMessage.success('删除成功')
    await loadCases()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    draft: 'info',
    active: 'success',
    deprecated: 'warning'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(async () => {
  await store.fetchSuiteById(suiteId.value)
  await loadCases()
})
</script>

<style scoped lang="scss">
.suite-detail-container {
  padding: 20px;

  .suite-title {
    font-size: 20px;
    font-weight: 600;
  }

  .suite-info-card {
    margin: 20px 0;

    h3 {
      margin: 0 0 16px 0;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .case-list-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      .actions {
        display: flex;
        gap: 12px;
        align-items: center;
      }
    }
  }
}
</style>

