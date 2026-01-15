<template>
  <div class="base-pagination">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="pageSizes"
      :layout="layout"
      :total="total"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      page: 1,
      limit: 10
    })
  },
  total: {
    type: Number,
    default: 0
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const currentPage = computed({
  get: () => props.modelValue.page,
  set: (val) => {
    emit('update:modelValue', { ...props.modelValue, page: val })
  }
})

const pageSize = computed({
  get: () => props.modelValue.limit,
  set: (val) => {
    emit('update:modelValue', { ...props.modelValue, limit: val })
  }
})

const handleSizeChange = (val) => {
  emit('change', { page: currentPage.value, limit: val })
}

const handleCurrentChange = (val) => {
  emit('change', { page: val, limit: pageSize.value })
}
</script>

<style scoped>
.base-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  padding: 10px 0;
}
</style>
