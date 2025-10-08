<template>
  <div class="suite-list-container">
    <div class="header">
      <h2>测试套件管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建套件
      </el-button>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="searchName"
        placeholder="搜索套件名称"
        clearable
        style="width: 300px"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-button type="primary" @click="handleSearch">搜索</el-button>
    </div>

    <div v-loading="store.suitesLoading" class="suite-grid">
      <el-card
        v-for="suite in store.suites"
        :key="suite.suite_id"
        class="suite-card"
        shadow="hover"
        @click="goToDetail(suite.suite_id)"
      >
        <template #header>
          <div class="card-header">
            <span class="suite-name">{{ suite.name }}</span>
            <div class="actions" @click.stop>
              <el-button
                type="primary"
                size="small"
                text
                @click="handleEdit(suite)"
              >
                编辑
              </el-button>
              <el-popconfirm
                title="确定要删除这个套件吗?"
                @confirm="handleDelete(suite.suite_id)"
              >
                <template #reference>
                  <el-button type="danger" size="small" text>删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </template>

        <div class="suite-info">
          <p class="description">{{ suite.description || '暂无描述' }}</p>
          <div class="meta-info">
            <span><el-icon><User /></el-icon> 创建人: {{ suite.created_by }}</span>
            <span><el-icon><Clock /></el-icon> {{ formatDate(suite.create_time) }}</span>
          </div>
        </div>
      </el-card>

      <el-empty v-if="!store.suitesLoading && store.suites.length === 0" description="暂无套件数据" />
    </div>

    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="store.suitesTotal"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingSuite ? '编辑套件' : '创建套件'"
      width="600px"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="套件名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入套件名称" />
        </el-form-item>
        <el-form-item label="套件描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入套件描述"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search, User, Clock } from '@element-plus/icons-vue'
import { useApiEngineStore } from '../store'
import type { Suite } from '../api'

const router = useRouter()
const store = useApiEngineStore()

const searchName = ref('')
const showCreateDialog = ref(false)
const editingSuite = ref<Suite | null>(null)
const submitting = ref(false)
const formRef = ref()

const pagination = reactive({
  page: 1,
  page_size: 20
})

const formData = reactive<Suite>({
  name: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入套件名称', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在 2 到 200 个字符', trigger: 'blur' }
  ]
}

const handleSearch = () => {
  store.fetchSuites({
    page: pagination.page,
    page_size: pagination.page_size,
    name: searchName.value || undefined
  })
}

const goToDetail = (id?: number) => {
  if (id) {
    router.push(`/plugin/api-engine/suites/${id}`)
  }
}

const handleEdit = (suite: Suite) => {
  editingSuite.value = suite
  formData.name = suite.name
  formData.description = suite.description || ''
  showCreateDialog.value = true
}

const handleDelete = async (id?: number) => {
  if (!id) return
  try {
    await store.deleteSuite(id)
    ElMessage.success('删除成功')
    handleSearch()
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
        if (editingSuite.value?.suite_id) {
          await store.updateSuite(editingSuite.value.suite_id, formData)
          ElMessage.success('更新成功')
        } else {
          await store.createSuite(formData)
          ElMessage.success('创建成功')
        }
        showCreateDialog.value = false
        resetForm()
        handleSearch()
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  editingSuite.value = null
  formData.name = ''
  formData.description = ''
  formRef.value?.resetFields()
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped lang="scss">
.suite-list-container {
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

  .filter-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }

  .suite-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-bottom: 20px;

    .suite-card {
      cursor: pointer;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-4px);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .suite-name {
          font-weight: 600;
          font-size: 16px;
        }

        .actions {
          display: flex;
          gap: 8px;
        }
      }

      .suite-info {
        .description {
          color: #666;
          margin-bottom: 16px;
          min-height: 40px;
          line-height: 1.5;
        }

        .meta-info {
          display: flex;
          justify-content: space-between;
          color: #999;
          font-size: 12px;

          span {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
  }

  .pagination {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
}
</style>

