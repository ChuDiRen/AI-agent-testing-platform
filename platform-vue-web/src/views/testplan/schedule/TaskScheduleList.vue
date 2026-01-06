<template>
  <div class="page-container">
    <BaseSearch :model="searchForm" @search="loadData" @reset="resetSearch">
      <el-form-item label="任务名称">
        <el-input v-model="searchForm.name" placeholder="请输入任务名称" clearable />
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="searchForm.status" placeholder="全部" clearable>
          <el-option label="运行中" value="active" />
          <el-option label="已停止" value="stopped" />
        </el-select>
      </el-form-item>
    </BaseSearch>

    <BaseTable
      title="定时任务管理"
      :data="tableData"
      :total="total"
      :loading="loading"
      :pagination="pagination"
      @update:pagination="pagination = $event"
      @refresh="loadData"
    >
      <template #header>
        <el-button type="primary" @click="handleCreate">
          <el-icon><Plus /></el-icon>新增任务
        </el-button>
      </template>

      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="任务名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="cron" label="Cron 表达式" width="150">
        <template #default="scope">
          <el-tooltip :content="getCronDescription(scope.row.cron)" placement="top">
            <code class="cron-code">{{ scope.row.cron }}</code>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="plan_name" label="关联测试计划" show-overflow-tooltip />
      <el-table-column prop="next_run" label="下次执行时间" width="180" />
      <el-table-column prop="last_run" label="上次执行时间" width="180" />
      <el-table-column prop="last_result" label="上次结果" width="100">
        <template #default="scope">
          <el-tag v-if="scope.row.last_result" size="small" :type="scope.row.last_result === 'success' ? 'success' : 'danger'">
            {{ scope.row.last_result === 'success' ? '成功' : '失败' }}
          </el-tag>
          <span v-else class="text-gray-400">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120">
        <template #default="scope">
          <el-switch
            v-model="scope.row.status"
            active-value="active"
            inactive-value="stopped"
            @change="(val) => handleStatusChange(scope.row, val)"
          />
          <span class="ml-2 text-xs" :class="scope.row.status === 'active' ? 'text-green-500' : 'text-gray-500'">
            {{ scope.row.status === 'active' ? '运行中' : '已停止' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column fixed="right" label="操作" width="200">
        <template #default="scope">
          <el-button link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
          <el-button link type="success" @click="handleRunNow(scope.row)">立即执行</el-button>
          <el-button link type="info" @click="handleViewLog(scope.row)">日志</el-button>
          <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </BaseTable>

    <!-- 新增/编辑弹窗 -->
    <el-dialog 
      v-model="formVisible" 
      :title="form.id ? '编辑定时任务' : '新增定时任务'" 
      width="600px"
      destroy-on-close
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="120px" class="p-4">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="测试计划" prop="plan_id">
          <el-select v-model="form.plan_id" placeholder="请选择计划" class="w-full">
            <el-option 
              v-for="plan in planList" 
              :key="plan.id" 
              :label="plan.name" 
              :value="plan.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="执行环境">
          <el-select v-model="form.env" class="w-full">
            <el-option label="开发环境" value="dev" />
            <el-option label="测试环境" value="test" />
            <el-option label="预发布环境" value="staging" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
        <el-form-item label="Cron 表达式" prop="cron">
          <el-input v-model="form.cron" placeholder="0 0 * * * ?">
            <template #append>
              <el-button @click="showCronHelper">
                <el-icon><QuestionFilled /></el-icon>
              </el-button>
            </template>
          </el-input>
          <p class="text-xs text-gray-400 mt-1">
            {{ getCronDescription(form.cron) || '请输入有效的 Cron 表达式' }}
          </p>
        </el-form-item>
        <el-form-item label="快捷设置">
          <el-radio-group v-model="cronPreset" @change="handleCronPreset">
            <el-radio-button label="hourly">每小时</el-radio-button>
            <el-radio-button label="daily">每天</el-radio-button>
            <el-radio-button label="weekly">每周</el-radio-button>
            <el-radio-button label="monthly">每月</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="通知方式">
          <el-checkbox-group v-model="form.notify">
            <el-checkbox label="email">邮件</el-checkbox>
            <el-checkbox label="wechat">企业微信</el-checkbox>
            <el-checkbox label="dingtalk">钉钉</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="失败重试">
          <el-switch v-model="form.retry_on_fail" />
          <span class="ml-2 text-gray-500 text-sm">失败后自动重试一次</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Cron 帮助弹窗 -->
    <el-dialog v-model="cronHelpVisible" title="Cron 表达式说明" width="600px">
      <div class="cron-help">
        <p class="mb-4">Cron 表达式由 6 个字段组成，格式为：</p>
        <code class="block bg-gray-100 p-3 rounded mb-4">秒 分 时 日 月 周</code>
        
        <el-table :data="cronFields" border size="small">
          <el-table-column prop="field" label="字段" width="80" />
          <el-table-column prop="range" label="取值范围" width="120" />
          <el-table-column prop="special" label="特殊字符" />
        </el-table>

        <div class="mt-4">
          <p class="font-bold mb-2">常用示例：</p>
          <ul class="list-disc list-inside space-y-1 text-sm">
            <li><code>0 0 * * * ?</code> - 每小时整点执行</li>
            <li><code>0 0 8 * * ?</code> - 每天早上8点执行</li>
            <li><code>0 0 8 * * 1-5</code> - 工作日早上8点执行</li>
            <li><code>0 0 0 1 * ?</code> - 每月1号凌晨执行</li>
            <li><code>0 */30 * * * ?</code> - 每30分钟执行一次</li>
          </ul>
        </div>
      </div>
    </el-dialog>

    <!-- 执行日志弹窗 -->
    <el-dialog v-model="logVisible" title="执行日志" width="800px">
      <el-table :data="logData" border stripe max-height="400">
        <el-table-column prop="time" label="执行时间" width="180" />
        <el-table-column prop="result" label="结果" width="100">
          <template #default="scope">
            <el-tag size="small" :type="scope.row.result === 'success' ? 'success' : 'danger'">
              {{ scope.row.result === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column prop="pass_rate" label="通过率" width="100" />
        <el-table-column prop="message" label="详情" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, QuestionFilled } from '@element-plus/icons-vue'
import BaseSearch from '~/components/BaseSearch/index.vue'
import BaseTable from '~/components/BaseTable/index.vue'
import { getScheduleList, deleteSchedule, toggleScheduleStatus, saveSchedule, runScheduleNow, getScheduleLog } from './schedule'

const loading = ref(false)
const tableData = ref([])
const total = ref(0)
const formVisible = ref(false)
const cronHelpVisible = ref(false)
const logVisible = ref(false)
const formRef = ref(null)
const cronPreset = ref('')

const searchForm = reactive({
  name: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  limit: 10
})

const form = reactive({
  id: null,
  name: '',
  plan_id: null,
  env: 'test',
  cron: '0 0 8 * * ?',
  notify: ['wechat'],
  retry_on_fail: false,
  status: 'active'
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  plan_id: [{ required: true, message: '请选择测试计划', trigger: 'change' }],
  cron: [{ required: true, message: '请输入 Cron 表达式', trigger: 'blur' }]
}

const planList = ref([
  { id: 1, name: 'API 核心流程回归' },
  { id: 2, name: 'Web 冒烟测试计划' },
  { id: 3, name: '混合场景端到端测试' },
  { id: 4, name: '支付模块专项测试' }
])

const logData = ref([])

const cronFields = [
  { field: '秒', range: '0-59', special: ', - * /' },
  { field: '分', range: '0-59', special: ', - * /' },
  { field: '时', range: '0-23', special: ', - * /' },
  { field: '日', range: '1-31', special: ', - * / ? L W' },
  { field: '月', range: '1-12', special: ', - * /' },
  { field: '周', range: '0-7', special: ', - * / ? L #' }
]

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await getScheduleList({ ...searchForm, ...pagination })
    if (res?.data?.code === 200) {
      tableData.value = res.data.data.list
      total.value = res.data.data.total
    } else {
      mockData()
    }
  } catch (e) {
    mockData()
  } finally {
    loading.value = false
  }
}

const mockData = () => {
  tableData.value = [
    { id: 1, name: '每日冒烟测试', cron: '0 0 8 * * ?', plan_id: 2, plan_name: 'Web 冒烟测试计划', next_run: '2026-01-07 08:00:00', last_run: '2026-01-06 08:00:00', last_result: 'success', status: 'active' },
    { id: 2, name: '核心接口每小时巡检', cron: '0 0 * * * ?', plan_id: 1, plan_name: 'API 核心流程回归', next_run: '2026-01-06 15:00:00', last_run: '2026-01-06 14:00:00', last_result: 'success', status: 'active' },
    { id: 3, name: '周末全量回归', cron: '0 0 2 ? * SAT', plan_id: 3, plan_name: '混合场景端到端测试', next_run: '2026-01-11 02:00:00', last_run: '2026-01-04 02:00:00', last_result: 'failed', status: 'active' },
    { id: 4, name: '月度性能测试', cron: '0 0 3 1 * ?', plan_id: 4, plan_name: '支付模块专项测试', next_run: '2026-02-01 03:00:00', last_run: '2026-01-01 03:00:00', last_result: 'success', status: 'stopped' }
  ]
  total.value = 4
}

const resetSearch = () => {
  Object.assign(searchForm, { name: '', status: '' })
  loadData()
}

// Cron 描述
const getCronDescription = (cron) => {
  if (!cron) return ''
  const parts = cron.split(' ')
  if (parts.length !== 6) return '无效的 Cron 表达式'
  
  const [sec, min, hour, day, month, week] = parts
  
  if (cron === '0 0 * * * ?') return '每小时整点执行'
  if (cron === '0 0 8 * * ?') return '每天早上 8:00 执行'
  if (cron === '0 0 0 * * ?') return '每天凌晨 0:00 执行'
  if (cron === '0 0 2 ? * SAT') return '每周六凌晨 2:00 执行'
  if (cron === '0 0 3 1 * ?') return '每月 1 号凌晨 3:00 执行'
  if (min.startsWith('*/')) return `每 ${min.slice(2)} 分钟执行一次`
  if (hour.startsWith('*/')) return `每 ${hour.slice(2)} 小时执行一次`
  
  return `${hour}:${min} 执行`
}

// Cron 快捷设置
const handleCronPreset = (preset) => {
  const presets = {
    hourly: '0 0 * * * ?',
    daily: '0 0 8 * * ?',
    weekly: '0 0 8 ? * MON',
    monthly: '0 0 8 1 * ?'
  }
  form.cron = presets[preset] || form.cron
}

// 新建任务
const handleCreate = () => {
  Object.assign(form, {
    id: null,
    name: '',
    plan_id: null,
    env: 'test',
    cron: '0 0 8 * * ?',
    notify: ['wechat'],
    retry_on_fail: false,
    status: 'active'
  })
  cronPreset.value = ''
  formVisible.value = true
}

// 编辑任务
const handleEdit = (row) => {
  Object.assign(form, row)
  cronPreset.value = ''
  formVisible.value = true
}

// 保存任务
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  try {
    await saveSchedule(form)
    ElMessage.success('保存成功')
    formVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.success('保存成功 (Mock)')
    formVisible.value = false
    loadData()
  }
}

// 状态切换
const handleStatusChange = async (row, val) => {
  try {
    await toggleScheduleStatus(row.id, val)
    ElMessage.success(`任务已${val === 'active' ? '启动' : '停止'}`)
  } catch (e) {
    ElMessage.success(`任务已${val === 'active' ? '启动' : '停止'} (Mock)`)
  }
}

// 立即执行
const handleRunNow = async (row) => {
  try {
    await runScheduleNow(row.id)
    ElMessage.success('任务已提交执行')
  } catch (e) {
    ElMessage.success('任务已提交执行 (Mock)')
  }
}

// 查看日志
const handleViewLog = async (row) => {
  try {
    const res = await getScheduleLog(row.id)
    if (res?.data?.code === 200) {
      logData.value = res.data.data
    } else {
      mockLogData()
    }
  } catch (e) {
    mockLogData()
  }
  logVisible.value = true
}

const mockLogData = () => {
  logData.value = [
    { time: '2026-01-06 08:00:00', result: 'success', duration: '3m 25s', pass_rate: '100%', message: '全部用例执行通过' },
    { time: '2026-01-05 08:00:00', result: 'success', duration: '3m 18s', pass_rate: '100%', message: '全部用例执行通过' },
    { time: '2026-01-04 08:00:00', result: 'failed', duration: '4m 02s', pass_rate: '85%', message: '3 个用例执行失败' },
    { time: '2026-01-03 08:00:00', result: 'success', duration: '3m 30s', pass_rate: '100%', message: '全部用例执行通过' }
  ]
}

// 删除任务
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除定时任务 "${row.name}" 吗？`, '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await deleteSchedule(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (e) {
      ElMessage.success('删除成功 (Mock)')
      tableData.value = tableData.value.filter(item => item.id !== row.id)
      total.value--
    }
  })
}

// 显示 Cron 帮助
const showCronHelper = () => {
  cronHelpVisible.value = true
}

onMounted(() => loadData())
</script>

<style scoped>
@import '~/styles/common-list.css';

.cron-code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
  font-size: 12px;
}

.cron-help code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Consolas', monospace;
}
</style>
