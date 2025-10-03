<!-- Copyright (c) 2025 左岚. All rights reserved. -->
<template>
  <div class="message-setting-container">
    <el-card>
      <template #header>
        <h3>通知设置</h3>
      </template>

      <el-form :model="settingsForm" label-width="150px">
        <!-- 系统通知设置 -->
        <el-divider content-position="left">系统通知</el-divider>
        <el-form-item label="系统维护通知">
          <el-switch v-model="settingsForm.system.maintenance" />
          <span class="form-item-desc">接收系统维护和更新通知</span>
        </el-form-item>
        <el-form-item label="系统公告">
          <el-switch v-model="settingsForm.system.announcement" />
          <span class="form-item-desc">接收系统公告和重要通知</span>
        </el-form-item>

        <!-- 测试通知设置 -->
        <el-divider content-position="left">测试通知</el-divider>
        <el-form-item label="测试开始通知">
          <el-switch v-model="settingsForm.test.start" />
          <span class="form-item-desc">测试开始时发送通知</span>
        </el-form-item>
        <el-form-item label="测试完成通知">
          <el-switch v-model="settingsForm.test.complete" />
          <span class="form-item-desc">测试完成时发送通知</span>
        </el-form-item>
        <el-form-item label="测试失败通知">
          <el-switch v-model="settingsForm.test.failed" />
          <span class="form-item-desc">测试失败时立即发送通知</span>
        </el-form-item>
        <el-form-item label="报告生成通知">
          <el-switch v-model="settingsForm.test.report" />
          <span class="form-item-desc">测试报告生成完成时发送通知</span>
        </el-form-item>

        <!-- 通知方式 -->
        <el-divider content-position="left">通知方式</el-divider>
        <el-form-item label="站内消息">
          <el-switch v-model="settingsForm.channels.internal" />
          <span class="form-item-desc">在系统内显示消息通知</span>
        </el-form-item>
        <el-form-item label="邮件通知">
          <el-switch v-model="settingsForm.channels.email" />
          <span class="form-item-desc">发送邮件通知到注册邮箱</span>
        </el-form-item>
        <el-form-item label="邮箱地址" v-if="settingsForm.channels.email">
          <el-input v-model="settingsForm.emailAddress" placeholder="请输入邮箱地址" style="width: 300px" />
        </el-form-item>
        <el-form-item label="微信通知">
          <el-switch v-model="settingsForm.channels.wechat" disabled />
          <span class="form-item-desc">发送微信通知（功能开发中）</span>
        </el-form-item>
        <el-form-item label="短信通知">
          <el-switch v-model="settingsForm.channels.sms" disabled />
          <span class="form-item-desc">发送短信通知（功能开发中）</span>
        </el-form-item>

        <!-- 通知时间设置 -->
        <el-divider content-position="left">通知时间</el-divider>
        <el-form-item label="免打扰时间">
          <el-switch v-model="settingsForm.doNotDisturb.enabled" />
          <span class="form-item-desc">在指定时间段内不发送通知</span>
        </el-form-item>
        <el-form-item label="时间范围" v-if="settingsForm.doNotDisturb.enabled">
          <el-time-picker
            v-model="settingsForm.doNotDisturb.startTime"
            placeholder="开始时间"
            format="HH:mm"
            style="width: 150px"
          />
          <span style="margin: 0 10px">至</span>
          <el-time-picker
            v-model="settingsForm.doNotDisturb.endTime"
            placeholder="结束时间"
            format="HH:mm"
            style="width: 150px"
          />
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSave">保存设置</el-button>
          <el-button @click="handleReset">恢复默认</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'

interface SettingsForm {
  system: {
    maintenance: boolean
    announcement: boolean
  }
  test: {
    start: boolean
    complete: boolean
    failed: boolean
    report: boolean
  }
  channels: {
    internal: boolean
    email: boolean
    wechat: boolean
    sms: boolean
  }
  emailAddress: string
  doNotDisturb: {
    enabled: boolean
    startTime: Date | null
    endTime: Date | null
  }
}

const settingsForm = reactive<SettingsForm>({
  system: {
    maintenance: true,
    announcement: true
  },
  test: {
    start: false,
    complete: true,
    failed: true,
    report: true
  },
  channels: {
    internal: true,
    email: false,
    wechat: false,
    sms: false
  },
  emailAddress: '',
  doNotDisturb: {
    enabled: false,
    startTime: null,
    endTime: null
  }
})

const handleSave = () => {
  // 这里应该调用API保存设置
  ElMessage.success('设置保存成功')
}

const handleReset = () => {
  // 恢复默认设置
  settingsForm.system.maintenance = true
  settingsForm.system.announcement = true
  settingsForm.test.start = false
  settingsForm.test.complete = true
  settingsForm.test.failed = true
  settingsForm.test.report = true
  settingsForm.channels.internal = true
  settingsForm.channels.email = false
  settingsForm.channels.wechat = false
  settingsForm.channels.sms = false
  settingsForm.emailAddress = ''
  settingsForm.doNotDisturb.enabled = false
  settingsForm.doNotDisturb.startTime = null
  settingsForm.doNotDisturb.endTime = null
  ElMessage.success('已恢复默认设置')
}
</script>

<style scoped>
.message-setting-container {
  padding: 20px;
}

.message-setting-container h3 {
  margin: 0;
}

.form-item-desc {
  margin-left: 10px;
  color: #999;
  font-size: 12px;
}

:deep(.el-divider__text) {
  font-weight: bold;
  color: #333;
}
</style>


