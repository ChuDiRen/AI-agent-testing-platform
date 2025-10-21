<template>
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
        <el-form-item label="角色ID" prop="id">
            <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="角色名称" prop="role_name">
            <el-input v-model="ruleForm.role_name" placeholder="请输入角色名称" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="角色描述" prop="remark">
            <el-input type="textarea" v-model="ruleForm.remark" placeholder="请输入角色描述" :readonly="isViewMode" />
        </el-form-item>
        <!-- 表单操作 -->
        <el-form-item>
            <el-button v-if="!isViewMode" type="primary" @click="submitForm(ruleFormRef)">
                提交
            </el-button>
            <el-button v-if="!isViewMode" @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">{{ isViewMode ? '返回' : '关闭' }}</el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from "vue"
import { queryById, insertData, updateData } from './role'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'

const router = useRouter()

// 判断是否为查看模式
const isViewMode = computed(() => router.currentRoute.value.query.view === 'true')

// 表单实例
const ruleFormRef = ref<FormInstance>()
// 表单数据
const ruleForm = reactive({
    id: 0,
    role_name: '',
    remark: ''
})

// 表单验证规则 - 查看模式下不需要验证
const rules = computed(() => {
    if (isViewMode.value) {
        return {}
    }
    return {
        role_name: [
            { required: true, message: '请输入角色名称', trigger: 'blur' }
        ]
    }
})

// 提交表单
const submitForm = async (form: FormInstance | undefined) => {
    if (!form) return
    await form.validate((valid, fields) => {
        if (!valid) {
            return 
        } 
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.id > 0) {
            updateData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    ElMessage.success('更新成功')
                    router.push('/roleList')
                } else {
                    ElMessage.error(res.data.msg || '更新失败')
                }
            }).catch((error: any) => {
                console.error('更新失败:', error)
                ElMessage.error('更新失败，请稍后重试')
            })
        } else {
            insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    ElMessage.success('新增成功')
                    router.push('/roleList')
                } else {
                    ElMessage.error(res.data.msg || '新增失败')
                }
            }).catch((error: any) => {
                console.error('新增失败:', error)
                ElMessage.error('新增失败，请稍后重试')
            })
        }
    })
}

// 重置表单
const resetForm = (form: FormInstance | undefined) => {
    if (!form) return
    form.resetFields()
}

// 关闭表单
const closeForm = () => {
    router.push('/roleList')
}

// 加载表单数据
const loadData = async (id: number) => {
    try {
        const res = await queryById(id)
        ruleForm.id = res.data.data.id
        ruleForm.role_name = res.data.data.role_name
        ruleForm.remark = res.data.data.remark || ''
    } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
    }
}

// 如果有id参数，说明是编辑或查看，需要获取数据
let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
</script>

<style scoped>
/* 查看模式样式优化 */
:deep(.el-input.is-disabled .el-input__wrapper),
:deep(.el-select.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
  cursor: not-allowed;
}

/* 只读输入框样式 - 保持白色背景，允许选择文本 */
:deep(.el-input__inner[readonly]),
:deep(.el-textarea__inner[readonly]) {
  cursor: text !important;
  user-select: text !important;
  background-color: #ffffff !important;
  color: var(--el-text-color-primary);
}

/* 只读输入框悬停效果 */
:deep(.el-input__inner[readonly]:hover),
:deep(.el-textarea__inner[readonly]:hover) {
  background-color: #fafafa !important;
}

/* 只读状态下去除边框焦点效果 */
:deep(.el-input.is-readonly:hover .el-input__wrapper),
:deep(.el-textarea.is-readonly:hover .el-textarea__inner) {
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
}
</style>

