<template>
  <div class="keyword-manage-container">
    <div class="header">
      <h2>关键字管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建自定义关键字
      </el-button>
    </div>

    <el-tabs v-model="activeTab" class="keyword-tabs">
      <!-- 内置关键字 -->
      <el-tab-pane label="内置关键字" name="builtin">
        <div class="search-bar">
          <el-input
            v-model="builtinSearch"
            placeholder="搜索关键字名称"
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <div class="keyword-grid">
          <el-card
            v-for="keyword in filteredBuiltinKeywords"
            :key="keyword.name"
            class="keyword-card"
            shadow="hover"
          >
            <template #header>
              <div class="card-header">
                <span class="keyword-name">{{ keyword.name }}</span>
                <el-tag type="info" size="small">内置</el-tag>
              </div>
            </template>
            <div class="keyword-content">
              <p class="description">{{ keyword.description || '暂无描述' }}</p>
              <el-divider />
              <div class="parameters">
                <h4>参数列表:</h4>
                <el-table
                  :data="keyword.parameters || []"
                  size="small"
                  border
                  v-if="keyword.parameters && keyword.parameters.length > 0"
                >
                  <el-table-column prop="name" label="参数名" width="120" />
                  <el-table-column prop="type" label="类型" width="80" />
                  <el-table-column label="必填" width="60">
                    <template #default="{ row }">
                      <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                        {{ row.required ? '是' : '否' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="description" label="说明" min-width="150" />
                </el-table>
                <el-empty v-else description="无参数" :image-size="60" />
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 自定义关键字 -->
      <el-tab-pane label="自定义关键字" name="custom">
        <div class="search-bar">
          <el-input
            v-model="customSearch"
            placeholder="搜索关键字名称"
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table
          v-loading="store.keywordsLoading"
          :data="filteredCustomKeywords"
          border
          style="width: 100%"
        >
          <el-table-column prop="keyword_id" label="ID" width="80" />
          <el-table-column prop="name" label="关键字名称" width="180" />
          <el-table-column prop="description" label="描述" min-width="200" />
          <el-table-column label="参数数量" width="100">
            <template #default="{ row }">
              {{ row.parameters?.length || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="180">
            <template #default="{ row }">{{ formatDate(row.create_time) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="viewKeyword(row)">查看</el-button>
              <el-button size="small" @click="editKeyword(row)">编辑</el-button>
              <el-button size="small" @click="testKeyword(row)">测试</el-button>
              <el-popconfirm
                title="确定要删除这个关键字吗?"
                @confirm="deleteKeyword(row.keyword_id)"
              >
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建/编辑关键字对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingKeyword ? '编辑关键字' : '创建关键字'"
      width="800px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="关键字名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入关键字名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入关键字描述"
          />
        </el-form-item>
        <el-form-item label="Python代码" prop="code">
          <el-input
            v-model="formData.code"
            type="textarea"
            :rows="15"
            placeholder="def my_keyword(*args, **kwargs):&#10;    # 实现关键字逻辑&#10;    pass"
            class="code-editor"
          />
        </el-form-item>
        <el-form-item label="参数定义">
          <el-button size="small" @click="addParameter">添加参数</el-button>
          <el-table :data="formData.parameters" border style="margin-top: 12px" size="small">
            <el-table-column label="参数名" width="150">
              <template #default="{ row }">
                <el-input v-model="row.name" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="类型" width="120">
              <template #default="{ row }">
                <el-select v-model="row.type" size="small">
                  <el-option label="string" value="string" />
                  <el-option label="int" value="int" />
                  <el-option label="bool" value="bool" />
                  <el-option label="dict" value="dict" />
                  <el-option label="list" value="list" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="必填" width="80">
              <template #default="{ row }">
                <el-switch v-model="row.required" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="说明">
              <template #default="{ row }">
                <el-input v-model="row.description" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ $index }">
                <el-button
                  size="small"
                  type="danger"
                  text
                  @click="removeParameter($index)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看关键字详情对话框 -->
    <el-dialog v-model="showViewDialog" title="关键字详情" width="700px">
      <el-descriptions :column="1" border v-if="viewingKeyword">
        <el-descriptions-item label="名称">{{ viewingKeyword.name }}</el-descriptions-item>
        <el-descriptions-item label="描述">{{ viewingKeyword.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="代码">
          <pre class="code-display">{{ viewingKeyword.code }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="参数">
          <el-table :data="viewingKeyword.parameters" size="small" border>
            <el-table-column prop="name" label="参数名" width="120" />
            <el-table-column prop="type" label="类型" width="80" />
            <el-table-column label="必填" width="60">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                  {{ row.required ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" />
          </el-table>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import type { Keyword, KeywordParameter } from '../api'

const store = useApiEngineStore()

const activeTab = ref('builtin')
const builtinSearch = ref('')
const customSearch = ref('')
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingKeyword = ref<Keyword | null>(null)
const viewingKeyword = ref<Keyword | null>(null)
const submitting = ref(false)
const formRef = ref()

const formData = reactive<Keyword>({
  name: '',
  description: '',
  code: '',
  parameters: []
})

const rules = {
  name: [
    { required: true, message: '请输入关键字名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  code: [{ required: true, message: '请输入Python代码', trigger: 'blur' }]
}

const filteredBuiltinKeywords = computed(() => {
  if (!builtinSearch.value) return store.builtinKeywords
  return store.builtinKeywords.filter(k => 
    k.name.toLowerCase().includes(builtinSearch.value.toLowerCase())
  )
})

const filteredCustomKeywords = computed(() => {
  if (!customSearch.value) return store.keywords
  return store.keywords.filter(k => 
    k.name.toLowerCase().includes(customSearch.value.toLowerCase())
  )
})

const addParameter = () => {
  formData.parameters?.push({
    name: '',
    type: 'string',
    required: false,
    description: ''
  })
}

const removeParameter = (index: number) => {
  formData.parameters?.splice(index, 1)
}

const editKeyword = (keyword: Keyword) => {
  editingKeyword.value = keyword
  Object.assign(formData, {
    name: keyword.name,
    description: keyword.description,
    code: keyword.code,
    parameters: JSON.parse(JSON.stringify(keyword.parameters || []))
  })
  showCreateDialog.value = true
}

const viewKeyword = (keyword: Keyword) => {
  viewingKeyword.value = keyword
  showViewDialog.value = true
}

const testKeyword = async (keyword: Keyword) => {
  ElMessage.info('测试关键字功能待实现')
}

const deleteKeyword = async (id?: number) => {
  if (!id) return
  try {
    await store.deleteKeyword(id)
    ElMessage.success('删除成功')
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        if (editingKeyword.value?.keyword_id) {
          await store.updateKeyword(editingKeyword.value.keyword_id, formData)
          ElMessage.success('更新成功')
        } else {
          await store.createKeyword(formData)
          ElMessage.success('创建成功')
        }
        showCreateDialog.value = false
        resetForm()
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  editingKeyword.value = null
  formData.name = ''
  formData.description = ''
  formData.code = ''
  formData.parameters = []
  formRef.value?.resetFields()
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(async () => {
  await Promise.all([
    store.fetchBuiltinKeywords(),
    store.fetchKeywords()
  ])
})
</script>

<style scoped lang="scss">
.keyword-manage-container {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
    }
  }

  .keyword-tabs {
    .search-bar {
      margin-bottom: 20px;
    }

    .keyword-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 20px;

      .keyword-card {
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .keyword-name {
            font-weight: 600;
            font-size: 16px;
          }
        }

        .keyword-content {
          .description {
            color: #666;
            margin-bottom: 12px;
            min-height: 40px;
          }

          .parameters {
            h4 {
              font-size: 14px;
              margin: 12px 0;
              font-weight: 600;
            }
          }
        }
      }
    }
  }

  .code-editor {
    :deep(textarea) {
      font-family: 'Courier New', monospace;
      font-size: 13px;
      line-height: 1.6;
    }
  }

  .code-display {
    margin: 0;
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    font-size: 13px;
    overflow-x: auto;
    font-family: 'Courier New', monospace;
    line-height: 1.6;
  }
}
</style>

