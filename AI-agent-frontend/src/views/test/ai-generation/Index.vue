<script setup>
import { h, onMounted, ref, computed } from 'vue'
import {
  NButton,
  NCard,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NInputNumber,
  NSpace,
  NSpin,
  NDataTable,
  NTag,
  NAlert,
  NCheckboxGroup,
  NCheckbox,
  NProgress,
} from 'naive-ui'

import CommonPage from '@/components/page/CommonPage.vue'
import { formatDate, renderIcon } from '@/utils'
import api from '@/api'
import TheIcon from '@/components/icon/TheIcon.vue'

defineOptions({ name: 'AI生成测试用例' })

const loading = ref(false)
const generating = ref(false)
const formRef = ref(null)
const generatedCases = ref([])
const generationHistory = ref([])

// 生成配置表单
const formData = ref({
  api_endpoint_id: null,
  model_id: null,
  generation_type: 'comprehensive',
  test_count: 10,
  priority_distribution: {
    high: 30,
    medium: 50,
    low: 20,
  },
  include_types: ['functional', 'boundary', 'exception'],
  description: '',
})

// API端点选项
const apiEndpointOptions = ref([])
// AI模型选项
const modelOptions = ref([])

// 生成类型选项
const generationTypeOptions = [
  { label: '综合测试', value: 'comprehensive', description: '包含功能、边界、异常等多种测试场景' },
  { label: '功能测试', value: 'functional', description: '专注于业务功能验证' },
  { label: '边界测试', value: 'boundary', description: '专注于边界条件和极值测试' },
  { label: '异常测试', value: 'exception', description: '专注于异常情况处理' },
  { label: '性能测试', value: 'performance', description: '专注于性能指标测试' },
  { label: '安全测试', value: 'security', description: '专注于安全漏洞检测' },
]

// 测试类型选项
const testTypeOptions = [
  { label: '功能测试', value: 'functional' },
  { label: '边界测试', value: 'boundary' },
  { label: '异常测试', value: 'exception' },
  { label: '性能测试', value: 'performance' },
  { label: '安全测试', value: 'security' },
]

// 生成的测试用例表格列
const caseColumns = [
  {
    title: '用例名称',
    key: 'name',
    width: 200,
    ellipsis: { tooltip: true },
  },
  {
    title: '测试类型',
    key: 'test_type',
    width: 100,
    align: 'center',
    render(row) {
      const typeMap = {
        functional: '功能',
        boundary: '边界',
        exception: '异常',
        performance: '性能',
        security: '安全',
      }
      return h(NTag, { type: 'info', size: 'small' }, {
        default: () => typeMap[row.test_type] || row.test_type
      })
    },
  },
  {
    title: '优先级',
    key: 'priority',
    width: 80,
    align: 'center',
    render(row) {
      const priorityTagType = {
        high: 'error',
        medium: 'warning',
        low: 'default',
      }
      const priorityMap = {
        high: '高',
        medium: '中',
        low: '低',
      }
      return h(NTag, { type: priorityTagType[row.priority], size: 'small' }, {
        default: () => priorityMap[row.priority]
      })
    },
  },
  {
    title: '描述',
    key: 'description',
    minWidth: 300,
    ellipsis: { tooltip: true },
  },
  {
    title: '置信度',
    key: 'confidence',
    width: 120,
    align: 'center',
    render(row) {
      const confidence = row.confidence || 0
      return h(NProgress, {
        type: 'line',
        percentage: Math.round(confidence * 100),
        status: confidence >= 0.8 ? 'success' : confidence >= 0.5 ? 'warning' : 'error',
        showIndicator: true,
      })
    },
  },
]

// 历史记录表格列
const historyColumns = [
  {
    title: '生成时间',
    key: 'created_at',
    width: 180,
    render(row) {
      return formatDate(row.created_at)
    },
  },
  {
    title: 'API端点',
    key: 'api_endpoint',
    width: 200,
    ellipsis: { tooltip: true },
  },
  {
    title: '生成类型',
    key: 'generation_type',
    width: 100,
    render(row) {
      const typeOption = generationTypeOptions.find(opt => opt.value === row.generation_type)
      return typeOption?.label || row.generation_type
    },
  },
  {
    title: '生成数量',
    key: 'generated_count',
    width: 100,
    align: 'center',
  },
  {
    title: '成功率',
    key: 'success_rate',
    width: 100,
    align: 'center',
    render(row) {
      return `${Math.round((row.success_count / row.generated_count) * 100)}%`
    },
  },
  {
    title: '状态',
    key: 'status',
    width: 100,
    align: 'center',
    render(row) {
      const statusMap = {
        pending: { label: '待生成', type: 'default' },
        generating: { label: '生成中', type: 'info' },
        completed: { label: '已完成', type: 'success' },
        failed: { label: '失败', type: 'error' },
      }
      const status = statusMap[row.status] || statusMap.pending
      return h(NTag, { type: status.type, size: 'small' }, {
        default: () => status.label
      })
    },
  },
]

// 表单验证规则
const rules = {
  api_endpoint_id: [
    { required: true, type: 'number', message: '请选择API端点', trigger: 'change' },
  ],
  model_id: [
    { required: true, type: 'number', message: '请选择AI模型', trigger: 'change' },
  ],
  generation_type: [
    { required: true, message: '请选择生成类型', trigger: 'change' },
  ],
  test_count: [
    { required: true, type: 'number', message: '请输入生成数量', trigger: 'blur' },
    { type: 'number', min: 1, max: 100, message: '生成数量应在1-100之间', trigger: 'blur' },
  ],
}

// 计算优先级分布总和
const prioritySum = computed(() => {
  const { high, medium, low } = formData.value.priority_distribution
  return high + medium + low
})

// 加载API端点和模型选项
async function loadOptions() {
  try {
    const [apiRes, modelRes] = await Promise.all([
      api.getApiEndpointList({ page: 1, page_size: 100 }),
      api.getAIModelList({ page: 1, page_size: 100, status: 'active' }),
    ])

    if (apiRes.data?.items) {
      apiEndpointOptions.value = apiRes.data.items.map(item => ({
        label: `${item.method} ${item.path}`,
        value: item.id,
      }))
    }

    if (modelRes.data?.items) {
      modelOptions.value = modelRes.data.items.map(item => ({
        label: `${item.name} (${item.provider})`,
        value: item.id,
      }))
    }
  } catch (error) {
    console.error('加载选项失败:', error)
    $message.error('加载选项失败')
  }
}

// 生成测试用例
async function handleGenerate() {
  try {
    await formRef.value?.validate()

    if (prioritySum.value !== 100) {
      $message.warning('优先级分布总和必须为100%')
      return
    }

    generating.value = true
    const response = await api.generateTestCases(formData.value)

    if (response.data) {
      generatedCases.value = response.data.test_cases || []
      $message.success(`成功生成 ${generatedCases.value.length} 个测试用例`)
      await loadGenerationHistory()
    }
  } catch (error) {
    console.error('生成测试用例失败:', error)
    $message.error(error.response?.data?.message || '生成失败')
  } finally {
    generating.value = false
  }
}

// 保存生成的测试用例
async function handleSaveCases() {
  if (generatedCases.value.length === 0) {
    $message.warning('没有可保存的测试用例')
    return
  }

  try {
    loading.value = true
    await api.batchCreateTestCases({ test_cases: generatedCases.value })
    $message.success('测试用例保存成功')
    generatedCases.value = []
  } catch (error) {
    console.error('保存测试用例失败:', error)
    $message.error('保存失败')
  } finally {
    loading.value = false
  }
}

// 加载生成历史
async function loadGenerationHistory() {
  try {
    const response = await api.getGenerationHistory({ page: 1, page_size: 10 })
    if (response.data?.items) {
      generationHistory.value = response.data.items
    }
  } catch (error) {
    console.error('加载生成历史失败:', error)
  }
}

onMounted(() => {
  loadOptions()
  loadGenerationHistory()
})
</script>

<template>
  <CommonPage show-footer title="AI生成测试用例">
    <NSpin :show="loading">
      <NSpace vertical :size="16">
        <!-- 生成配置 -->
        <NCard title="生成配置" :bordered="false">
          <NForm
            ref="formRef"
            :model="formData"
            :rules="rules"
            label-placement="left"
            label-width="120"
          >
            <NFormItem label="API端点" path="api_endpoint_id">
              <NSelect
                v-model:value="formData.api_endpoint_id"
                :options="apiEndpointOptions"
                placeholder="请选择要测试的API端点"
                filterable
              />
            </NFormItem>

            <NFormItem label="AI模型" path="model_id">
              <NSelect
                v-model:value="formData.model_id"
                :options="modelOptions"
                placeholder="请选择AI模型"
                filterable
              />
            </NFormItem>

            <NFormItem label="生成类型" path="generation_type">
              <NSelect
                v-model:value="formData.generation_type"
                :options="generationTypeOptions"
                placeholder="请选择生成类型"
              >
                <template #option="{ option }">
                  <div>
                    <div>{{ option.label }}</div>
                    <div class="text-xs text-gray-500">{{ option.description }}</div>
                  </div>
                </template>
              </NSelect>
            </NFormItem>

            <NFormItem label="生成数量" path="test_count">
              <NInputNumber
                v-model:value="formData.test_count"
                :min="1"
                :max="100"
                placeholder="请输入生成数量"
                style="width: 100%"
              />
            </NFormItem>

            <NFormItem label="包含类型" path="include_types">
              <NCheckboxGroup v-model:value="formData.include_types">
                <NSpace>
                  <NCheckbox v-for="type in testTypeOptions" :key="type.value" :value="type.value">
                    {{ type.label }}
                  </NCheckbox>
                </NSpace>
              </NCheckboxGroup>
            </NFormItem>

            <NFormItem label="优先级分布">
              <NSpace vertical style="width: 100%">
                <div class="flex items-center gap-4">
                  <span class="w-20">高优先级:</span>
                  <NInputNumber
                    v-model:value="formData.priority_distribution.high"
                    :min="0"
                    :max="100"
                    style="flex: 1"
                  />
                  <span>%</span>
                </div>
                <div class="flex items-center gap-4">
                  <span class="w-20">中优先级:</span>
                  <NInputNumber
                    v-model:value="formData.priority_distribution.medium"
                    :min="0"
                    :max="100"
                    style="flex: 1"
                  />
                  <span>%</span>
                </div>
                <div class="flex items-center gap-4">
                  <span class="w-20">低优先级:</span>
                  <NInputNumber
                    v-model:value="formData.priority_distribution.low"
                    :min="0"
                    :max="100"
                    style="flex: 1"
                  />
                  <span>%</span>
                </div>
                <NAlert v-if="prioritySum !== 100" type="warning" size="small">
                  优先级分布总和应为100% (当前: {{ prioritySum }}%)
                </NAlert>
              </NSpace>
            </NFormItem>

            <NFormItem label="备注说明" path="description">
              <NInput
                v-model:value="formData.description"
                type="textarea"
                :rows="3"
                placeholder="请输入生成说明或特殊要求"
              />
            </NFormItem>

            <NFormItem :show-label="false">
              <NSpace>
                <NButton
                  type="primary"
                  :loading="generating"
                  :disabled="generating"
                  @click="handleGenerate"
                >
                  <template #icon>
                    <TheIcon icon="mdi:auto-fix" :size="18" />
                  </template>
                  {{ generating ? '生成中...' : '开始生成' }}
                </NButton>
                <NButton
                  v-if="generatedCases.length > 0"
                  type="success"
                  @click="handleSaveCases"
                >
                  <template #icon>
                    <TheIcon icon="mdi:content-save" :size="18" />
                  </template>
                  保存测试用例
                </NButton>
              </NSpace>
            </NFormItem>
          </NForm>
        </NCard>

        <!-- 生成结果 -->
        <NCard v-if="generatedCases.length > 0" title="生成结果" :bordered="false">
          <template #header-extra>
            <NTag type="success">
              共生成 {{ generatedCases.length }} 个测试用例
            </NTag>
          </template>
          <NDataTable
            :columns="caseColumns"
            :data="generatedCases"
            :pagination="{ pageSize: 10 }"
            :bordered="false"
          />
        </NCard>

        <!-- 生成历史 -->
        <NCard title="生成历史" :bordered="false">
          <NDataTable
            :columns="historyColumns"
            :data="generationHistory"
            :pagination="{ pageSize: 10 }"
            :bordered="false"
          />
        </NCard>
      </NSpace>
    </NSpin>
  </CommonPage>
</template>

<style scoped></style>

