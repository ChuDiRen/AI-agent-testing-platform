<template>
  <div class="step-editor">
    <div class="editor-header">
      <h3>测试步骤配置</h3>
      <el-button type="primary" size="small" @click="addStep">
        <el-icon><Plus /></el-icon>
        添加步骤
      </el-button>
    </div>

    <div v-if="steps.length === 0" class="empty-state">
      <el-empty description="暂无测试步骤,点击上方按钮添加" />
    </div>

    <draggable
      v-model="steps"
      item-key="id"
      handle=".drag-handle"
      @end="handleDragEnd"
      class="step-list"
    >
      <template #item="{ element, index }">
        <el-card class="step-card" shadow="hover">
          <div class="step-header">
            <div class="step-title">
              <el-icon class="drag-handle"><Menu /></el-icon>
              <span class="step-number">步骤 {{ index + 1 }}</span>
              <el-tag size="small">{{ element.keyword || '未选择关键字' }}</el-tag>
            </div>
            <div class="step-actions">
              <el-button
                type="danger"
                size="small"
                text
                @click="removeStep(index)"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>

          <div class="step-content">
            <el-form :model="element" label-width="100px" size="small">
              <el-form-item label="选择关键字">
                <keyword-selector
                  v-model="element.keyword"
                  @select="(info) => handleKeywordSelect(index, info)"
                />
              </el-form-item>

              <el-form-item label="步骤名称">
                <el-input v-model="element.name" placeholder="可选,步骤描述" />
              </el-form-item>

              <!-- 动态参数表单 -->
              <div v-if="element.parameters && element.parameters.length > 0">
                <el-divider content-position="left">参数配置</el-divider>
                <el-form-item
                  v-for="param in element.parameters"
                  :key="param.name"
                  :label="param.name"
                  :required="param.required"
                >
                  <el-input
                    v-if="param.type === 'string' || param.type === 'str'"
                    v-model="element.params[param.name]"
                    :placeholder="param.description || `请输入${param.name}`"
                  />
                  <el-input-number
                    v-else-if="param.type === 'int' || param.type === 'number'"
                    v-model="element.params[param.name]"
                    :placeholder="param.description || `请输入${param.name}`"
                    style="width: 100%"
                  />
                  <el-switch
                    v-else-if="param.type === 'bool' || param.type === 'boolean'"
                    v-model="element.params[param.name]"
                  />
                  <el-input
                    v-else-if="param.type === 'dict' || param.type === 'object'"
                    v-model="element.params[param.name]"
                    type="textarea"
                    :rows="3"
                    placeholder="请输入JSON格式"
                  />
                  <el-input
                    v-else
                    v-model="element.params[param.name]"
                    :placeholder="param.description || `请输入${param.name}`"
                  />
                </el-form-item>
              </div>
            </el-form>
          </div>
        </el-card>
      </template>
    </draggable>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete, Menu } from '@element-plus/icons-vue'
import draggable from 'vuedraggable'
import KeywordSelector from './KeywordSelector.vue'

interface Step {
  id: string
  name?: string
  keyword?: string
  parameters?: any[]
  params: Record<string, any>
}

const props = defineProps<{
  modelValue: Step[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: Step[]): void
}>()

const steps = ref<Step[]>(props.modelValue || [])

watch(
  () => props.modelValue,
  (newVal) => {
    steps.value = newVal || []
  }
)

watch(
  steps,
  (newVal) => {
    emit('update:modelValue', newVal)
  },
  { deep: true }
)

const addStep = () => {
  steps.value.push({
    id: `step_${Date.now()}_${Math.random()}`,
    name: '',
    keyword: '',
    parameters: [],
    params: {}
  })
}

const removeStep = (index: number) => {
  steps.value.splice(index, 1)
}

const handleKeywordSelect = (index: number, keywordInfo: any) => {
  if (!keywordInfo) return
  
  const step = steps.value[index]
  step.parameters = keywordInfo.parameters || []
  
  // 初始化参数默认值
  step.params = {}
  if (keywordInfo.parameters) {
    keywordInfo.parameters.forEach((param: any) => {
      if (param.default !== undefined) {
        step.params[param.name] = param.default
      }
    })
  }
}

const handleDragEnd = () => {
  emit('update:modelValue', steps.value)
}
</script>

<style scoped lang="scss">
.step-editor {
  .editor-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
  }

  .empty-state {
    padding: 40px 0;
  }

  .step-list {
    display: flex;
    flex-direction: column;
    gap: 16px;

    .step-card {
      cursor: move;

      .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #eee;

        .step-title {
          display: flex;
          align-items: center;
          gap: 12px;

          .drag-handle {
            cursor: grab;
            color: #999;
            font-size: 18px;

            &:active {
              cursor: grabbing;
            }
          }

          .step-number {
            font-weight: 600;
            font-size: 16px;
          }
        }
      }

      .step-content {
        :deep(.el-form-item) {
          margin-bottom: 16px;
        }
      }
    }
  }
}
</style>

