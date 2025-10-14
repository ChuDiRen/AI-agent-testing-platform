<template>
  <div class="api-group-form-container">
    <el-card>
      <template #header>
        <div class="header">
          <span>{{ formTitle }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="formData.project_id" placeholder="请选择项目" style="width: 100%">
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.project_name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="分组名称" prop="group_name">
          <el-input v-model="formData.group_name" placeholder="请输入分组名称" />
        </el-form-item>

        <el-form-item label="父级分组" prop="parent_id">
          <el-select v-model="formData.parent_id" placeholder="请选择父级分组（可选）" clearable style="width: 100%">
            <el-option label="无" :value="0" />
            <el-option
              v-for="group in groupList"
              :key="group.id"
              :label="group.group_name"
              :value="group.id"
              :disabled="group.id === formData.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="formData.sort" :min="0" :max="9999" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入描述"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryGroupByPage, getGroupById, createGroup, updateGroup } from './apiGroup.js'
import { queryByPage as queryProjectByPage } from '../project/ApiProject.js'  // 使用正确的导出名称

const route = useRoute()
const router = useRouter()

const formRef = ref(null)
const projectList = ref([])
const groupList = ref([])

const formData = ref({
  id: null,
  project_id: '',
  group_name: '',
  parent_id: null,
  sort: 0,
  description: ''
})

const formRules = {
  project_id: [{ required: true, message: '请选择所属项目', trigger: 'change' }],
  group_name: [{ required: true, message: '请输入分组名称', trigger: 'blur' }]
}

const formTitle = computed(() => {
  return formData.value.id ? '编辑接口分组' : '新增接口分组'
})

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryProjectByPage({ page: 1, pageSize: 1000 })
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败', error)
  }
}

// 加载分组列表
const loadGroups = async () => {
  try {
    const res = await queryGroupByPage({ page: 1, pageSize: 1000 })
    if (res.data.code === 200) {
      groupList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载分组列表失败', error)
  }
}

// 加载数据
const loadData = async () => {
  const id = route.query.id
  if (id) {
    try {
      const res = await getGroupById(id)
      if (res.data.code === 200 && res.data.data) {
        formData.value = res.data.data
      }
    } catch (error) {
      ElMessage.error('加载数据失败')
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let res
        if (formData.value.id) {
          res = await updateGroup(formData.value.id, formData.value)
        } else {
          res = await createGroup(formData.value)
        }

        if (res.data.code === 200) {
          ElMessage.success(formData.value.id ? '修改成功' : '新增成功')
          goBack()
        } else {
          ElMessage.error(res.data.msg || '操作失败')
        }
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(() => {
  loadProjects()
  loadGroups()
  loadData()
})
</script>

<style scoped lang="scss">
.api-group-form-container {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
</style>

