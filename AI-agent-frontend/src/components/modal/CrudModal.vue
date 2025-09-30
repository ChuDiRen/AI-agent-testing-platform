<template>
  <NModal
    v-model:show="modalVisible"
    :mask-closable="false"
    preset="dialog"
    :title="modalTitle"
    :style="{ width: width + 'px' }"
    @after-leave="handleAfterLeave"
  >
    <NForm
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-placement="labelPlacement"
      :label-width="labelWidth"
      :require-mark-placement="requireMarkPlacement"
    >
      <slot :form-data="formData" />
    </NForm>
    
    <template #action>
      <NSpace>
        <NButton @click="handleCancel">取消</NButton>
        <NButton
          type="primary"
          :loading="submitLoading"
          @click="handleConfirm"
        >
          确定
        </NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  type: {
    type: String,
    default: 'add', // add | edit
  },
  title: {
    type: String,
    default: '',
  },
  width: {
    type: Number,
    default: 600,
  },
  labelPlacement: {
    type: String,
    default: 'left',
  },
  labelWidth: {
    type: [String, Number],
    default: 100,
  },
  requireMarkPlacement: {
    type: String,
    default: 'right-hanging',
  },
  data: {
    type: Object,
    default: () => ({}),
  },
  rules: {
    type: Object,
    default: () => ({}),
  },
  onSave: {
    type: Function,
    required: true,
  },
})

const emit = defineEmits(['update:visible', 'success'])

const formRef = ref()
const submitLoading = ref(false)
const formData = ref({})

// 弹窗显示状态
const modalVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

// 弹窗标题
const modalTitle = computed(() => {
  if (props.title) return props.title
  return props.type === 'add' ? '新增' : '编辑'
})

// 监听数据变化
watch(
  () => props.data,
  (newData) => {
    formData.value = { ...newData }
  },
  { immediate: true, deep: true }
)

// 监听弹窗显示
watch(
  () => props.visible,
  (visible) => {
    if (visible) {
      nextTick(() => {
        formRef.value?.restoreValidation()
      })
    }
  }
)

// 确认提交
const handleConfirm = async () => {
  try {
    await formRef.value?.validate()
    submitLoading.value = true
    
    await props.onSave(formData.value, props.type)
    
    modalVisible.value = false
    emit('success')
    window.$message?.success(props.type === 'add' ? '新增成功' : '更新成功')
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 取消
const handleCancel = () => {
  modalVisible.value = false
}

// 弹窗关闭后
const handleAfterLeave = () => {
  formRef.value?.restoreValidation()
  submitLoading.value = false
}

defineExpose({
  formRef,
  formData,
})
</script>
