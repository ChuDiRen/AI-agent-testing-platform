<template>
  <div class="api-test-plan-form">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>{{ formTitle }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>

      <!-- 基本信息表单 -->
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="计划名称" prop="plan_name">
          <el-input v-model="formData.plan_name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="执行引擎" prop="plugin_code">
          <el-select v-model="formData.plugin_code" placeholder="请选择执行引擎" style="width: 300px">
            <el-option
              v-for="item in pluginList"
              :key="item.plugin_code"
              :label="item.plugin_name"
              :value="item.plugin_code"
            >
              <span>{{ item.plugin_name }}</span>
              <span style="color: #999; margin-left: 10px; font-size: 12px">{{ item.plugin_code }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="计划描述">
          <el-input v-model="formData.plan_desc" type="textarea" :rows="3" placeholder="请输入计划描述" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存计划</el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用例关联（仅编辑模式） -->
    <el-card v-if="formData.id" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>关联用例</span>
          <div>
            <el-button type="danger" size="small" :disabled="selectedCases.length === 0" @click="handleBatchRemove">批量移除{{ selectedCases.length > 0 ? ` (${selectedCases.length})` : '' }}</el-button>
            <el-button type="success" size="small" @click="handleAddCase">添加用例</el-button>
          </div>
        </div>
      </template>

      <el-table :data="caseList" border @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="run_order" label="执行顺序" width="100" />
        <el-table-column prop="case_name" label="用例名称" min-width="150" />
        <el-table-column prop="case_desc" label="用例描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="数据驱动" width="120">
          <template #default="{ row }">
            <el-tag v-if="hasDdtData(row.ddt_data)">已配置</el-tag>
            <el-tag v-else type="info">未配置</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="handleEditDdt(row)">配置数据</el-button>
            <el-button size="small" type="danger" @click="handleRemoveCase(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 数据驱动配置对话框 -->
    <el-dialog v-model="ddtDialogVisible" title="配置数据驱动" width="70%">
      <JsonEditor
        v-model="currentDdtData"
        title="数据驱动配置（JSON格式数组）"
        :show-toolbar="false"
        :show-preview="false"
        placeholder='[{"desc": "数据组1", "username": "test1"}]'
      />
      <template #footer>
        <el-button @click="ddtDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDdt">保存</el-button>
      </template>
    </el-dialog>

    <!-- 机器人通知配置（仅编辑模式） -->
    <el-card v-if="formData.id" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>
            <el-icon><Bell /></el-icon>
            消息通知配置
          </span>
          <el-button type="primary" size="small" @click="robotDialogVisible = true">
            <el-icon><Plus /></el-icon>
            添加机器人
          </el-button>
        </div>
      </template>

      <el-empty v-if="robotList.length === 0" description="暂未配置通知机器人" :image-size="60" />
      
      <el-table v-else :data="robotList" border>
        <el-table-column prop="robot_name" label="机器人名称" min-width="150" />
        <el-table-column prop="robot_type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRobotTypeTag(row.robot_type)" size="small">
              {{ getRobotTypeName(row.robot_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="启用通知" width="100" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.is_enabled" @change="handleUpdateRobot(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="notify_on_success" label="成功通知" width="100" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.notify_on_success" @change="handleUpdateRobot(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="notify_on_failure" label="失败通知" width="100" align="center">
          <template #default="{ row }">
            <el-switch v-model="row.notify_on_failure" @change="handleUpdateRobot(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-button link type="danger" @click="handleRemoveRobot(row)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加机器人对话框 -->
    <el-dialog v-model="robotDialogVisible" title="添加通知机器人" width="500px">
      <el-form :model="robotForm" label-width="100px">
        <el-form-item label="选择机器人" required>
          <el-select v-model="robotForm.robot_id" placeholder="请选择机器人" style="width: 100%">
            <el-option
              v-for="robot in availableRobots"
              :key="robot.id"
              :label="robot.robot_name"
              :value="robot.id"
            >
              <span>{{ robot.robot_name }}</span>
              <el-tag :type="getRobotTypeTag(robot.robot_type)" size="small" style="margin-left: 8px">
                {{ getRobotTypeName(robot.robot_type) }}
              </el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="成功时通知">
          <el-switch v-model="robotForm.notify_on_success" />
        </el-form-item>
        <el-form-item label="失败时通知">
          <el-switch v-model="robotForm.notify_on_failure" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="robotDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddRobot" :disabled="!robotForm.robot_id">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Bell } from '@element-plus/icons-vue'
import { insertData, updateData, queryById, removeCase, updateDdtData, getDdtTemplate, getPlanRobots, addPlanRobot, updatePlanRobot, removePlanRobot } from './testPlan'
import JsonEditor from '~/components/JsonEditor.vue'
import { queryAllExecutors } from '~/views/plugin/plugin.js'
import { queryAll as queryAllRobots } from '~/views/msgmanage/robot/robotConfig.js'

const router = useRouter()
const route = useRoute()

const formRef = ref(null)
const formData = ref({
  id: null,
  plan_name: '',
  plan_desc: '',
  project_id: null,
  plugin_code: 'api_engine'
})

// 插件列表
const pluginList = ref([])

const rules = {
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }]
}

const caseList = ref([])
const selectedCases = ref([])
const ddtDialogVisible = ref(false)
const currentDdtData = ref('')
const currentEditingCase = ref(null)

// 机器人相关
const robotList = ref([])
const allRobots = ref([])
const robotDialogVisible = ref(false)
const robotForm = ref({
  robot_id: null,
  notify_on_success: true,
  notify_on_failure: true
})

const formTitle = computed(() => formData.value.id ? '编辑测试计划' : '新增测试计划')

// 可选的机器人（排除已关联的）
const availableRobots = computed(() => {
  const linkedIds = robotList.value.map(r => r.robot_id)
  return allRobots.value.filter(r => !linkedIds.includes(r.id))
})

// 判断是否有有效的数据驱动配置
const hasDdtData = (ddtData) => {
  if (!ddtData) return false
  if (typeof ddtData === 'string') {
    const trimmed = ddtData.trim()
    if (!trimmed || trimmed === '[]' || trimmed === 'null' || trimmed === '""') return false
    try {
      const parsed = JSON.parse(trimmed)
      return Array.isArray(parsed) && parsed.length > 0
    } catch {
      return false
    }
  }
  if (Array.isArray(ddtData)) return ddtData.length > 0
  return false
}

// 选择变化
const handleSelectionChange = (selection) => {
  selectedCases.value = selection
}

// 加载插件列表
const loadPluginList = async () => {
  try {
    const res = await queryAllExecutors()
    if (res.data.code === 200) {
      pluginList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载插件列表失败:', error)
  }
}

// 加载详情
const loadDetail = async (id) => {
  try {
    const res = await queryById(id)
    if (res.data.code === 200 && res.data.data) {
      const data = res.data.data
      formData.value = {
        id: data.id,
        plan_name: data.plan_name,
        plan_desc: data.plan_desc,
        project_id: data.project_id,
        plugin_code: data.plugin_code || 'api_engine'
      }
      caseList.value = data.cases || []
    }
  } catch (error) {
    ElMessage.error('加载数据失败: ' + error.message)
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const apiFunc = formData.value.id ? updateData : insertData
    const res = await apiFunc(formData.value)
    
    if (res.data.code === 200) {
      ElMessage.success(formData.value.id ? '更新成功' : '新增成功')
      goBack()
    } else {
      ElMessage.error(res.data.msg || '操作失败')
    }
  } catch (error) {
    if (error !== false) { // 表单验证失败会返回false
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

// 添加用例（简化版，实际应该打开用例选择器）
const handleAddCase = () => {
  ElMessage.info('请在用例列表中选择用例添加到计划')
  // TODO: 实现用例选择器对话框
}

// 移除用例
const handleRemoveCase = async (row) => {
  try {
    const res = await removeCase(row.id)
    if (res.data.code === 200) {
      ElMessage.success('移除成功')
      loadDetail(formData.value.id)
    } else {
      ElMessage.error(res.data.msg || '移除失败')
    }
  } catch (error) {
    ElMessage.error('移除失败: ' + error.message)
  }
}

// 批量移除用例
const handleBatchRemove = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请先选择要移除的用例')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要移除选中的 ${selectedCases.value.length} 个用例吗？`,
      '批量移除',
      { type: 'warning' }
    )
    
    // 逐个移除
    let successCount = 0
    let failCount = 0
    for (const row of selectedCases.value) {
      try {
        const res = await removeCase(row.id)
        if (res.data.code === 200) {
          successCount++
        } else {
          failCount++
        }
      } catch {
        failCount++
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功移除 ${successCount} 个用例${failCount > 0 ? `，${failCount} 个失败` : ''}`)
      selectedCases.value = []
      loadDetail(formData.value.id)
    } else {
      ElMessage.error('移除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败: ' + error.message)
    }
  }
}

// 编辑数据驱动
const handleEditDdt = async (row) => {
  currentEditingCase.value = row
  
  // 准备数据
  let ddtContent = ''
  if (row.ddt_data && row.ddt_data !== '[]' && row.ddt_data !== 'null') {
    // 已有数据，直接显示
    if (typeof row.ddt_data === 'string') {
      try {
        // 格式化JSON显示
        const parsed = JSON.parse(row.ddt_data)
        ddtContent = JSON.stringify(parsed, null, 2)
      } catch {
        ddtContent = row.ddt_data
      }
    } else {
      ddtContent = JSON.stringify(row.ddt_data, null, 2)
    }
  } else {
    // 没有数据，从后端获取模板
    try {
      const res = await getDdtTemplate(row.case_info_id)
      if (res.data.code === 200 && res.data.data) {
        const template = res.data.data.template || []
        ddtContent = JSON.stringify(template, null, 2)
      } else {
        // 后端获取失败，使用默认模板
        const template = [
          {
            "desc": `${row.case_name || '测试'}_数据1`,
            "变量名1": "值1",
            "变量名2": "值2"
          }
        ]
        ddtContent = JSON.stringify(template, null, 2)
      }
    } catch (error) {
      console.error('获取模板失败:', error)
      // 使用默认模板
      const template = [
        {
          "desc": `${row.case_name || '测试'}_数据1`,
          "变量名1": "值1",
          "变量名2": "值2"
        }
      ]
      ddtContent = JSON.stringify(template, null, 2)
    }
  }
  
  // 先设置数据，再打开对话框
  currentDdtData.value = ddtContent
  ddtDialogVisible.value = true
  
  // 等待 DOM 更新后再次设置数据，确保编辑器能接收到
  await nextTick()
  currentDdtData.value = ddtContent
}

// 保存数据驱动配置
const handleSaveDdt = async () => {
  try {
    // JsonEditor 返回的可能是对象或字符串
    let ddtData = currentDdtData.value
    if (typeof ddtData === 'string') {
      ddtData = JSON.parse(ddtData)
    }
    
    const res = await updateDdtData({
      plan_case_id: currentEditingCase.value.id,
      ddt_data: ddtData
    })
    
    if (res.data.code === 200) {
      ElMessage.success('保存成功')
      ddtDialogVisible.value = false
      loadDetail(formData.value.id)
    } else {
      ElMessage.error(res.data.msg || '保存失败')
    }
  } catch (error) {
    ElMessage.error('JSON格式错误或保存失败: ' + error.message)
  }
}

const goBack = () => {
  router.back()
}

// ==================== 机器人相关方法 ====================

// 加载所有可用机器人
const loadAllRobots = async () => {
  try {
    const res = await queryAllRobots()
    if (res.data.code === 200) {
      allRobots.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载机器人列表失败:', error)
  }
}

// 加载计划关联的机器人
const loadPlanRobots = async (planId) => {
  try {
    const res = await getPlanRobots(planId)
    if (res.data.code === 200) {
      robotList.value = res.data.data || []
    }
  } catch (error) {
    console.error('加载计划机器人失败:', error)
  }
}

// 添加机器人
const handleAddRobot = async () => {
  if (!robotForm.value.robot_id) {
    ElMessage.warning('请选择机器人')
    return
  }
  
  try {
    const res = await addPlanRobot({
      plan_id: formData.value.id,
      robot_id: robotForm.value.robot_id,
      is_enabled: true,
      notify_on_success: robotForm.value.notify_on_success,
      notify_on_failure: robotForm.value.notify_on_failure
    })
    
    if (res.data.code === 200) {
      ElMessage.success('添加成功')
      robotDialogVisible.value = false
      robotForm.value = { robot_id: null, notify_on_success: true, notify_on_failure: true }
      loadPlanRobots(formData.value.id)
    } else {
      ElMessage.error(res.data.msg || '添加失败')
    }
  } catch (error) {
    ElMessage.error('添加失败: ' + error.message)
  }
}

// 更新机器人配置
const handleUpdateRobot = async (row) => {
  try {
    const res = await updatePlanRobot({
      id: row.id,
      is_enabled: row.is_enabled,
      notify_on_success: row.notify_on_success,
      notify_on_failure: row.notify_on_failure
    })
    
    if (res.data.code === 200) {
      ElMessage.success('更新成功')
    } else {
      ElMessage.error(res.data.msg || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败: ' + error.message)
  }
}

// 移除机器人
const handleRemoveRobot = async (row) => {
  try {
    await ElMessageBox.confirm(`确定移除机器人"${row.robot_name}"吗？`, '提示', { type: 'warning' })
    
    const res = await removePlanRobot(row.id)
    if (res.data.code === 200) {
      ElMessage.success('移除成功')
      loadPlanRobots(formData.value.id)
    } else {
      ElMessage.error(res.data.msg || '移除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('移除失败: ' + error.message)
    }
  }
}

// 辅助方法
const getRobotTypeName = (type) => {
  const map = { wechat: '企业微信', dingtalk: '钉钉', feishu: '飞书' }
  return map[type] || type
}

const getRobotTypeTag = (type) => {
  const map = { wechat: 'success', dingtalk: 'primary', feishu: 'warning' }
  return map[type] || ''
}

onMounted(() => {
  loadPluginList()
  loadAllRobots()
  if (route.query.id) {
    loadDetail(route.query.id)
    loadPlanRobots(route.query.id)
  }
})
</script>

<style scoped>
.api-test-plan-form {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

