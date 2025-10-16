<template>
  <div class="request-body">
    <!-- Body类型选择 -->
    <el-radio-group v-model="bodyType" class="body-type-group">
      <el-radio-button label="form-data">form-data</el-radio-button>
      <el-radio-button label="x-www-form-urlencoded">x-www-form-urlencoded</el-radio-button>
      <el-radio-button label="raw">raw (JSON)</el-radio-button>
      <el-radio-button label="file">文件上传</el-radio-button>
    </el-radio-group>

    <!-- form-data -->
    <div v-if="bodyType === 'form-data'" class="body-content">
      <div class="form-list">
        <div v-for="(item, index) in formDataList" :key="index" class="form-row">
          <el-checkbox v-model="item.enabled" />
          <el-input v-model="item.key" placeholder="字段名" class="form-key" />
          <el-input v-model="item.value" placeholder="字段值" class="form-value" />
          <el-button type="danger" icon="Delete" circle @click="removeFormData(index)" />
        </div>
      </div>
      <el-button type="primary" icon="Plus" @click="addFormData">添加字段</el-button>
    </div>

    <!-- x-www-form-urlencoded -->
    <div v-if="bodyType === 'x-www-form-urlencoded'" class="body-content">
      <div class="form-list">
        <div v-for="(item, index) in wwwFormDataList" :key="index" class="form-row">
          <el-checkbox v-model="item.enabled" />
          <el-input v-model="item.key" placeholder="字段名" class="form-key" />
          <el-input v-model="item.value" placeholder="字段值" class="form-value" />
          <el-button type="danger" icon="Delete" circle @click="removeWwwFormData(index)" />
        </div>
      </div>
      <el-button type="primary" icon="Plus" @click="addWwwFormData">添加字段</el-button>
    </div>

    <!-- raw (JSON) -->
    <div v-if="bodyType === 'raw'" class="body-content">
      <el-input
        v-model="jsonDataStr"
        type="textarea"
        :rows="15"
        placeholder="请输入JSON格式的数据"
        @blur="formatJson"
      />
    </div>

    <!-- 文件上传 -->
    <div v-if="bodyType === 'file'" class="body-content">
      <div class="file-list">
        <div v-for="(item, index) in fileList" :key="index" class="file-row">
          <el-checkbox v-model="item.enabled" />
          <el-input v-model="item.key" placeholder="字段名" class="file-key" />
          <el-input v-model="item.value" placeholder="文件路径" class="file-value" />
          <el-button type="danger" icon="Delete" circle @click="removeFile(index)" />
        </div>
      </div>
      <el-button type="primary" icon="Plus" @click="addFile">添加文件</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  formData: {
    type: String,
    default: '{}'
  },
  wwwFormData: {
    type: String,
    default: '{}'
  },
  jsonData: {
    type: String,
    default: '{}'
  },
  files: {
    type: String,
    default: '{}'
  }
})

const emit = defineEmits(['update:formData', 'update:wwwFormData', 'update:jsonData', 'update:files'])

// Body类型
const bodyType = ref('raw')

// form-data列表
const formDataList = ref([])

// www-form-urlencoded列表
const wwwFormDataList = ref([])

// JSON数据
const jsonDataStr = ref('{}')

// 文件列表
const fileList = ref([])

// 初始化form-data
const initFormData = () => {
  try {
    const obj = JSON.parse(props.formData || '{}')
    formDataList.value = Object.keys(obj).map(key => ({
      enabled: true,
      key,
      value: obj[key]
    }))
  } catch {
    formDataList.value = []
  }
}

// 初始化www-form-urlencoded
const initWwwFormData = () => {
  try {
    const obj = JSON.parse(props.wwwFormData || '{}')
    wwwFormDataList.value = Object.keys(obj).map(key => ({
      enabled: true,
      key,
      value: obj[key]
    }))
  } catch {
    wwwFormDataList.value = []
  }
}

// 初始化JSON数据
const initJsonData = () => {
  jsonDataStr.value = props.jsonData || '{}'
}

// 初始化文件列表
const initFiles = () => {
  try {
    const obj = JSON.parse(props.files || '{}')
    fileList.value = Object.keys(obj).map(key => ({
      enabled: true,
      key,
      value: obj[key]
    }))
  } catch {
    fileList.value = []
  }
}

// 添加form-data
const addFormData = () => {
  formDataList.value.push({
    enabled: true,
    key: '',
    value: ''
  })
}

// 删除form-data
const removeFormData = (index) => {
  formDataList.value.splice(index, 1)
  updateFormData()
}

// 更新form-data
const updateFormData = () => {
  const obj = {}
  formDataList.value.forEach(item => {
    if (item.enabled && item.key) {
      obj[item.key] = item.value
    }
  })
  emit('update:formData', JSON.stringify(obj))
}

// 添加www-form-urlencoded
const addWwwFormData = () => {
  wwwFormDataList.value.push({
    enabled: true,
    key: '',
    value: ''
  })
}

// 删除www-form-urlencoded
const removeWwwFormData = (index) => {
  wwwFormDataList.value.splice(index, 1)
  updateWwwFormData()
}

// 更新www-form-urlencoded
const updateWwwFormData = () => {
  const obj = {}
  wwwFormDataList.value.forEach(item => {
    if (item.enabled && item.key) {
      obj[item.key] = item.value
    }
  })
  emit('update:wwwFormData', JSON.stringify(obj))
}

// 格式化JSON
const formatJson = () => {
  try {
    const obj = JSON.parse(jsonDataStr.value)
    jsonDataStr.value = JSON.stringify(obj, null, 2)
    emit('update:jsonData', jsonDataStr.value)
  } catch (e) {
    ElMessage.warning('JSON格式不正确')
  }
}

// 添加文件
const addFile = () => {
  fileList.value.push({
    enabled: true,
    key: '',
    value: ''
  })
}

// 删除文件
const removeFile = (index) => {
  fileList.value.splice(index, 1)
  updateFiles()
}

// 更新文件
const updateFiles = () => {
  const obj = {}
  fileList.value.forEach(item => {
    if (item.enabled && item.key) {
      obj[item.key] = item.value
    }
  })
  emit('update:files', JSON.stringify(obj))
}

// 监听变化
watch(formDataList, updateFormData, { deep: true })
watch(wwwFormDataList, updateWwwFormData, { deep: true })
watch(jsonDataStr, (val) => emit('update:jsonData', val))
watch(fileList, updateFiles, { deep: true })

// 监听props变化
watch(() => props.formData, initFormData, { immediate: true })
watch(() => props.wwwFormData, initWwwFormData, { immediate: true })
watch(() => props.jsonData, initJsonData, { immediate: true })
watch(() => props.files, initFiles, { immediate: true })
</script>

<style scoped lang="scss">
.request-body {
  .body-type-group {
    margin-bottom: 20px;
  }

  .body-content {
    .form-list,
    .file-list {
      margin-bottom: 15px;
    }

    .form-row,
    .file-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;

      .form-key,
      .file-key {
        width: 200px;
      }

      .form-value,
      .file-value {
        flex: 1;
      }
    }
  }
}
</style>

