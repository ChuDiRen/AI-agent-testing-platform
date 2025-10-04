<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="knowledge-base-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📚 知识库管理</span>
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            创建知识库
          </el-button>
        </div>
      </template>
      
      <!-- 知识库列表 -->
      <el-row :gutter="20">
        <el-col
          v-for="kb in knowledgeBases"
          :key="kb.kb_id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card class="kb-card" shadow="hover" @click="selectKnowledgeBase(kb)">
            <div class="kb-icon">📖</div>
            <div class="kb-name">{{ kb.name }}</div>
            <div class="kb-description">{{ kb.description || '暂无描述' }}</div>
            <div class="kb-stats">
              <el-tag size="small">{{ kb.document_count }} 文档</el-tag>
              <el-tag size="small" type="info">{{ kb.chunk_count }} 分块</el-tag>
            </div>
            <div class="kb-actions">
              <el-button link size="small" @click.stop="editKnowledgeBase(kb)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button link size="small" type="danger" @click.stop="deleteKnowledgeBase(kb)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="knowledgeBases.length === 0" description="暂无知识库,点击创建" />
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑知识库' : '创建知识库'"
      width="600px"
    >
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述"
          />
        </el-form-item>
        <el-form-item label="分块大小" prop="chunk_size">
          <el-input-number
            v-model="formData.chunk_size"
            :min="100"
            :max="2000"
            :step="100"
          />
          <span class="form-tip">字符数,建议500</span>
        </el-form-item>
        <el-form-item label="分块重叠" prop="chunk_overlap">
          <el-input-number
            v-model="formData.chunk_overlap"
            :min="0"
            :max="500"
            :step="10"
          />
          <span class="form-tip">字符数,建议50</span>
        </el-form-item>
        <el-form-item label="公开" prop="is_public">
          <el-switch v-model="formData.is_public" />
          <span class="form-tip">公开后其他用户可见</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getKnowledgeBasesAPI,
  createKnowledgeBaseAPI,
  updateKnowledgeBaseAPI,
  deleteKnowledgeBaseAPI,
  type KnowledgeBase
} from '@/api/knowledge'

const router = useRouter()

// 状态
const knowledgeBases = ref<KnowledgeBase[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref<FormInstance>()

// 表单数据
const formData = ref({
  kb_id: 0,
  name: '',
  description: '',
  chunk_size: 500,
  chunk_overlap: 50,
  is_public: false
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入知识库名称', trigger: 'blur' },
    { min: 1, max: 200, message: '长度在 1 到 200 个字符', trigger: 'blur' }
  ]
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const response = await getKnowledgeBasesAPI()
    if (response.data) {
      knowledgeBases.value = response.data
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  }
}

// 显示创建对话框
const showCreateDialog = () => {
  isEdit.value = false
  formData.value = {
    kb_id: 0,
    name: '',
    description: '',
    chunk_size: 500,
    chunk_overlap: 50,
    is_public: false
  }
  dialogVisible.value = true
}

// 编辑知识库
const editKnowledgeBase = (kb: KnowledgeBase) => {
  isEdit.value = true
  formData.value = {
    kb_id: kb.kb_id,
    name: kb.name,
    description: kb.description || '',
    chunk_size: kb.chunk_size,
    chunk_overlap: kb.chunk_overlap,
    is_public: kb.is_public
  }
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEdit.value) {
        await updateKnowledgeBaseAPI(formData.value.kb_id, formData.value)
        ElMessage.success('更新成功')
      } else {
        await createKnowledgeBaseAPI(formData.value)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadKnowledgeBases()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

// 删除知识库
const deleteKnowledgeBase = async (kb: KnowledgeBase) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库"${kb.name}"吗?此操作将删除所有文档和数据!`,
      '警告',
      {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }
    )
    
    await deleteKnowledgeBaseAPI(kb.kb_id)
    ElMessage.success('删除成功')
    loadKnowledgeBases()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 选择知识库
const selectKnowledgeBase = (kb: KnowledgeBase) => {
  router.push({
    name: 'KnowledgeDetail',
    params: { kbId: kb.kb_id }
  })
}

// 初始化
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped lang="scss">
.knowledge-base-container {
  padding: 20px;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
  
  .kb-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-5px);
    }
    
    .kb-icon {
      font-size: 48px;
      text-align: center;
      margin-bottom: 10px;
    }
    
    .kb-name {
      font-size: 18px;
      font-weight: 600;
      text-align: center;
      margin-bottom: 8px;
    }
    
    .kb-description {
      font-size: 14px;
      color: #909399;
      text-align: center;
      margin-bottom: 12px;
      min-height: 40px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    
    .kb-stats {
      display: flex;
      justify-content: center;
      gap: 8px;
      margin-bottom: 12px;
    }
    
    .kb-actions {
      display: flex;
      justify-content: center;
      gap: 8px;
      padding-top: 12px;
      border-top: 1px solid #ebeef5;
    }
  }
  
  .form-tip {
    margin-left: 10px;
    font-size: 12px;
    color: #909399;
  }
}
</style>

