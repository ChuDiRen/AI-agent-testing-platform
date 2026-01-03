<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ isEdit ? '编辑测试任务' : '新增测试任务' }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <el-form ref="formRef" :model="formData" :rules="rules" label-width="120px" style="max-width: 800px">
        <el-form-item label="任务名称" prop="task_name">
          <el-input v-model="formData.task_name" placeholder="请输入任务名称" />
        </el-form-item>

        <el-form-item label="任务描述" prop="task_desc">
          <el-input v-model="formData.task_desc" type="textarea" :rows="3" placeholder="请输入任务描述" />
        </el-form-item>

        <el-form-item label="所属项目" prop="project_id">
          <el-select v-model="formData.project_id" placeholder="请选择项目" clearable filterable style="width: 100%">
            <el-option v-for="project in projectList" :key="project.id" :label="project.project_name" :value="project.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="任务类型" prop="task_type">
          <el-radio-group v-model="formData.task_type">
            <el-radio value="manual">手动任务</el-radio>
            <el-radio value="scheduled">定时任务</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Cron表达式" prop="cron_expression" v-if="formData.task_type === 'scheduled'">
          <el-input v-model="formData.cron_expression" placeholder="例如: 0 0 8 * * ? (每天8点执行)" style="width: 300px" />
          <el-tooltip content="Cron表达式格式: 秒 分 时 日 月 周" placement="top">
            <el-icon style="margin-left: 8px; cursor: pointer;"><QuestionFilled /></el-icon>
          </el-tooltip>
        </el-form-item>

        <el-divider content-position="left">测试内容配置</el-divider>

        <el-form-item label="配置方式">
          <el-radio-group v-model="configMode" @change="handleConfigModeChange">
            <el-radio value="plan">关联测试计划</el-radio>
            <el-radio value="cases">选择用例</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="测试计划" prop="plan_id" v-if="configMode === 'plan'">
          <el-select v-model="formData.plan_id" placeholder="请选择测试计划" clearable filterable style="width: 100%">
            <el-option v-for="plan in planList" :key="plan.id" :label="plan.plan_name" :value="plan.id">
              <span>{{ plan.plan_name }}</span>
              <span style="color: #999; margin-left: 10px;">{{ plan.case_count || 0 }}个用例</span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="选择用例" prop="case_ids" v-if="configMode === 'cases'">
          <el-select 
            v-model="formData.case_ids" 
            multiple 
            filterable 
            placeholder="请选择用例" 
            style="width: 100%"
          >
            <el-option v-for="item in caseList" :key="item.id" :label="item.case_name" :value="item.id">
              <span>{{ item.case_name }}</span>
              <span style="color: #999; margin-left: 10px;">ID: {{ item.id }}</span>
            </el-option>
          </el-select>
          <div class="selected-count" v-if="formData.case_ids && formData.case_ids.length > 0">
            已选择 {{ formData.case_ids.length }} 个用例
          </div>
        </el-form-item>

        <el-divider content-position="left">通知配置（可选）</el-divider>

        <el-form-item label="执行完成通知">
          <el-switch v-model="enableNotify" />
        </el-form-item>

        <template v-if="enableNotify">
          <el-form-item label="通知方式">
            <el-checkbox-group v-model="notifyMethods">
              <el-checkbox value="webhook">Webhook</el-checkbox>
              <el-checkbox value="email">邮件</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="Webhook地址" v-if="notifyMethods.includes('webhook')">
            <el-input v-model="webhookUrl" placeholder="请输入Webhook地址" />
          </el-form-item>

          <el-form-item label="通知邮箱" v-if="notifyMethods.includes('email')">
            <el-input v-model="notifyEmail" placeholder="请输入通知邮箱，多个用逗号分隔" />
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? '保存修改' : '创建任务' }}
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'
import { queryById, insertData, updateData } from './testTask.js'
import { queryAll as queryProjects } from '~/views/apitest/project/apiProject.js'
import { queryByPage as queryPlans } from '~/views/apitest/testplan/testPlan.js'
import { queryByPage as queryCases } from '~/views/apitest/apiinfocase/apiInfoCase.js'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const submitting = ref(false)

// 判断是否编辑模式
const isEdit = computed(() => !!route.query.id)

// 表单数据
const formData = reactive({
  id: null,
  task_name: '',
  task_desc: '',
  project_id: null,
  task_type: 'manual',
  cron_expression: '',
  plan_id: null,
  case_ids: [],
  notify_config: null,
  extra_config: null
})

// 配置模式
const configMode = ref('plan')

// 通知配置
const enableNotify = ref(false)
const notifyMethods = ref([])
const webhookUrl = ref('')
const notifyEmail = ref('')

// 下拉列表数据
const projectList = ref([])
const planList = ref([])
const caseList = ref([])

// 表单验证规则
const rules = {
  task_name: [
    { required: true, message: '请输入任务名称', trigger: 'blur' },
    { min: 1, max: 255, message: '长度在 1 到 255 个字符', trigger: 'blur' }
  ],
  task_type: [
    { required: true, message: '请选择任务类型', trigger: 'change' }
  ],
  cron_expression: [
    { required: true, message: '请输入Cron表达式', trigger: 'blur' }
  ]
}

// 加载项目列表
const loadProjects = async () => {
  try {
    const res = await queryProjects()
    if (res.data.code === 200) {
      projectList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

// 加载测试计划列表
const loadPlans = async () => {
  try {
    const res = await queryPlans({ page: 1, pageSize: 100 })
    if (res.data.code === 200) {
      planList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载测试计划列表失败:', error)
  }
}

// 加载用例列表
const loadCases = async () => {
  try {
    const res = await queryCases({ page: 1, pageSize: 100 })
    if (res.data.code === 200) {
      caseList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载用例列表失败:', error)
  }
}

// 加载任务详情
const loadTaskDetail = async () => {
  if (!route.query.id) return
  
  try {
    const res = await queryById(route.query.id)
    if (res.data.code === 200 && res.data.data) {
      const data = res.data.data
      formData.id = data.id
      formData.task_name = data.task_name
      formData.task_desc = data.task_desc
      formData.project_id = data.project_id
      formData.task_type = data.task_type
      formData.cron_expression = data.cron_expression
      formData.plan_id = data.plan_id
      formData.case_ids = data.case_ids || []
      
      // 设置配置模式
      if (data.plan_id) {
        configMode.value = 'plan'
      } else if (data.case_ids && data.case_ids.length > 0) {
        configMode.value = 'cases'
      }
      
      // 解析通知配置
      if (data.notify_config) {
        enableNotify.value = true
        notifyMethods.value = data.notify_config.methods || []
        webhookUrl.value = data.notify_config.webhook_url || ''
        notifyEmail.value = data.notify_config.email || ''
      }
    }
  } catch (error) {
    console.error('加载任务详情失败:', error)
    ElMessage.error('加载任务详情失败')
  }
}

// 配置模式切换
const handleConfigModeChange = () => {
  if (configMode.value === 'plan') {
    formData.case_ids = []
  } else {
    formData.plan_id = null
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
  } catch (error) {
    return
  }

  // 验证测试内容配置
  if (configMode.value === 'plan' && !formData.plan_id) {
    ElMessage.warning('请选择测试计划')
    return
  }
  if (configMode.value === 'cases' && (!formData.case_ids || formData.case_ids.length === 0)) {
    ElMessage.warning('请选择至少一个用例')
    return
  }

  // 构建通知配置
  let notifyConfig = null
  if (enableNotify.value && notifyMethods.value.length > 0) {
    notifyConfig = {
      methods: notifyMethods.value,
      webhook_url: webhookUrl.value,
      email: notifyEmail.value
    }
  }

  submitting.value = true
  try {
    const submitData = {
      ...formData,
      notify_config: notifyConfig
    }

    // 根据配置模式清理数据
    if (configMode.value === 'plan') {
      submitData.case_ids = null
    } else {
      submitData.plan_id = null
    }

    let res
    if (isEdit.value) {
      res = await updateData(submitData)
    } else {
      res = await insertData(submitData)
    }

    if (res.data.code === 200) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      goBack()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 返回列表
const goBack = () => {
  router.push('/TestTaskList')
}

onMounted(() => {
  loadProjects()
  loadPlans()
  loadCases()
  if (isEdit.value) {
    loadTaskDetail()
  }
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-count {
  margin-top: 8px;
  color: #409eff;
  font-size: 13px;
}
</style>
