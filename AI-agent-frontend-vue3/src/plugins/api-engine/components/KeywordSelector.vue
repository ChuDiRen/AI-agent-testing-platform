<template>
  <div class="keyword-selector">
    <el-select
      v-model="selectedKeyword"
      filterable
      placeholder="选择关键字"
      @change="handleSelect"
      style="width: 100%"
    >
      <el-option-group label="内置关键字">
        <el-option
          v-for="keyword in builtinKeywords"
          :key="keyword.name"
          :label="keyword.name"
          :value="keyword.name"
        >
          <div class="keyword-option">
            <span class="keyword-name">{{ keyword.name }}</span>
            <span class="keyword-desc">{{ keyword.description }}</span>
          </div>
        </el-option>
      </el-option-group>
      <el-option-group label="自定义关键字" v-if="customKeywords.length > 0">
        <el-option
          v-for="keyword in customKeywords"
          :key="keyword.keyword_id"
          :label="keyword.name"
          :value="keyword.name"
        >
          <div class="keyword-option">
            <span class="keyword-name">{{ keyword.name }}</span>
            <span class="keyword-desc">{{ keyword.description }}</span>
          </div>
        </el-option>
      </el-option-group>
    </el-select>

    <!-- 关键字参数说明 -->
    <el-collapse v-if="currentKeywordInfo" class="keyword-info" v-model="activeCollapse">
      <el-collapse-item name="params" title="参数说明">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item
            v-for="param in currentKeywordInfo.parameters"
            :key="param.name"
            :label="param.name"
          >
            <el-tag :type="param.required ? 'danger' : 'info'" size="small">
              {{ param.required ? '必填' : '可选' }}
            </el-tag>
            <el-tag size="small" style="margin-left: 8px">{{ param.type }}</el-tag>
            <span style="margin-left: 8px">{{ param.description || '-' }}</span>
            <span v-if="param.default" style="margin-left: 8px; color: #999;">
              默认: {{ param.default }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useApiEngineStore } from '../store'

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'select', keywordInfo: any): void
}>()

const store = useApiEngineStore()

const selectedKeyword = ref(props.modelValue || '')
const activeCollapse = ref(['params'])

const builtinKeywords = computed(() => store.builtinKeywords || [])
const customKeywords = computed(() => store.keywords || [])

const currentKeywordInfo = computed(() => {
  if (!selectedKeyword.value) return null
  
  // 先找内置关键字
  const builtin = builtinKeywords.value.find(k => k.name === selectedKeyword.value)
  if (builtin) return builtin

  // 再找自定义关键字
  const custom = customKeywords.value.find(k => k.name === selectedKeyword.value)
  return custom || null
})

const handleSelect = (value: string) => {
  emit('update:modelValue', value)
  emit('select', currentKeywordInfo.value)
}

onMounted(async () => {
  if (builtinKeywords.value.length === 0) {
    await store.fetchBuiltinKeywords()
  }
  if (customKeywords.value.length === 0) {
    await store.fetchKeywords()
  }
})
</script>

<style scoped lang="scss">
.keyword-selector {
  .keyword-option {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .keyword-name {
      font-weight: 600;
    }

    .keyword-desc {
      font-size: 12px;
      color: #999;
      margin-left: 8px;
    }
  }

  .keyword-info {
    margin-top: 12px;
  }
}
</style>

