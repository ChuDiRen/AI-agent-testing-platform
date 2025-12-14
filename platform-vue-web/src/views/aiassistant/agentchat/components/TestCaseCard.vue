<template>
  <div class="test-case-card" :class="{ expanded: isExpanded }">
    <div class="card-header" @click="toggleExpand">
      <div class="header-left">
        <el-tag :type="priorityType" size="small">{{ testCase.priority || 'P2' }}</el-tag>
        <span class="case-name">{{ testCase.case_name || testCase.case_id }}</span>
      </div>
      <div class="header-right">
        <el-tag v-if="testCase.module" type="info" size="small">{{ testCase.module }}</el-tag>
        <el-icon :class="{ rotated: isExpanded }"><ArrowDown /></el-icon>
      </div>
    </div>
    
    <el-collapse-transition>
      <div class="card-body" v-show="isExpanded">
        <!-- 前置条件 -->
        <div class="section" v-if="testCase.preconditions?.length">
          <div class="section-title">前置条件</div>
          <ul class="preconditions">
            <li v-for="(cond, idx) in testCase.preconditions" :key="idx">{{ cond }}</li>
          </ul>
        </div>
        
        <!-- 测试步骤 -->
        <div class="section" v-if="testCase.test_steps?.length">
          <div class="section-title">测试步骤</div>
          <div class="steps-table">
            <div class="step-row header">
              <span class="step-no">步骤</span>
              <span class="step-action">操作</span>
              <span class="step-expected">预期结果</span>
            </div>
            <div class="step-row" v-for="step in testCase.test_steps" :key="step.step_no">
              <span class="step-no">{{ step.step_no }}</span>
              <span class="step-action">{{ step.action }}</span>
              <span class="step-expected">{{ step.expected }}</span>
            </div>
          </div>
        </div>
        
        <!-- 预期结果 -->
        <div class="section" v-if="testCase.expected_result">
          <div class="section-title">预期结果</div>
          <div class="expected-result">{{ testCase.expected_result }}</div>
        </div>
        
        <!-- 测试数据 -->
        <div class="section" v-if="testCase.test_data && Object.keys(testCase.test_data).length">
          <div class="section-title">测试数据</div>
          <pre class="test-data">{{ JSON.stringify(testCase.test_data, null, 2) }}</pre>
        </div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <el-button size="small" @click="handleEdit">
            <el-icon><Edit /></el-icon> 编辑
          </el-button>
          <el-button size="small" @click="handleCopy">
            <el-icon><CopyDocument /></el-icon> 复制
          </el-button>
          <el-button size="small" type="primary" @click="handleSave">
            <el-icon><Check /></el-icon> 保存
          </el-button>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowDown, Edit, CopyDocument, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  testCase: { type: Object, required: true }
})

const emit = defineEmits(['edit', 'save', 'copy'])

const isExpanded = ref(false)

const priorityType = computed(() => {
  const map = { P0: 'danger', P1: 'warning', P2: 'info', P3: 'success' }
  return map[props.testCase.priority] || 'info'
})

const toggleExpand = () => { isExpanded.value = !isExpanded.value }
const handleEdit = () => { emit('edit', props.testCase) }
const handleSave = () => { emit('save', props.testCase) }
const handleCopy = () => {
  navigator.clipboard.writeText(JSON.stringify(props.testCase, null, 2))
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.test-case-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin: 8px 0;
  overflow: hidden;
  transition: all 0.3s ease;
}
.test-case-card:hover { box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1); }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: #fafafa;
}
.header-left { display: flex; align-items: center; gap: 8px; }
.header-right { display: flex; align-items: center; gap: 8px; }
.case-name { font-weight: 500; color: #303133; }
.rotated { transform: rotate(180deg); }
.card-body { padding: 16px; }
.section { margin-bottom: 16px; }
.section-title { font-weight: 500; color: #606266; margin-bottom: 8px; font-size: 13px; }
.preconditions { margin: 0; padding-left: 20px; color: #606266; font-size: 13px; }
.steps-table { border: 1px solid #ebeef5; border-radius: 4px; overflow: hidden; }
.step-row { display: flex; border-bottom: 1px solid #ebeef5; font-size: 13px; }
.step-row:last-child { border-bottom: none; }
.step-row.header { background: #f5f7fa; font-weight: 500; }
.step-no { width: 50px; padding: 8px; text-align: center; border-right: 1px solid #ebeef5; }
.step-action { flex: 1; padding: 8px; border-right: 1px solid #ebeef5; }
.step-expected { flex: 1; padding: 8px; }
.expected-result { color: #606266; font-size: 13px; line-height: 1.6; }
.test-data { background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 12px; overflow-x: auto; }
.card-actions { display: flex; gap: 8px; justify-content: flex-end; padding-top: 12px; border-top: 1px solid #ebeef5; }
</style>
