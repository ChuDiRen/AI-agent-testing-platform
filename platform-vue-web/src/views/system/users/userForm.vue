<template>
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
            <!-- 不同的页面，不同的表单字段 -->
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="用户名" prop="username">
            <el-input v-model="ruleForm.username" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
            <el-input v-model="ruleForm.password" type="password" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
            <el-input v-model="ruleForm.email" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="联系电话" prop="mobile">
            <el-input v-model="ruleForm.mobile" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="部门" prop="dept_id">
            <el-select v-model="ruleForm.dept_id" placeholder="请选择部门" clearable :disabled="isViewMode">
                <el-option v-for="dept in deptOptions" :key="dept.id" :label="dept.name" :value="dept.id" />
            </el-select>
        </el-form-item>
        <el-form-item label="性别" prop="ssex">
            <el-radio-group v-model="ruleForm.ssex" :disabled="isViewMode">
                <el-radio value="0">男</el-radio>
                <el-radio value="1">女</el-radio>
                <el-radio value="2">保密</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="status">
            <el-radio-group v-model="ruleForm.status" :disabled="isViewMode">
                <el-radio value="1">有效</el-radio>
                <el-radio value="0">锁定</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="头像" prop="avatar">
            <el-input 
                v-model="ruleForm.avatar" 
                placeholder="请输入头像URL"
                :readonly="isViewMode"
            />
        </el-form-item>
        <el-form-item label="描述" prop="description">
            <el-input v-model="ruleForm.description" type="textarea" :rows="3" :readonly="isViewMode" />
        </el-form-item>
        <!-- 如果有不需要展示在页面的属性，建议通过 v-show="false" 进行控制，不要直接删除，这样方便你后续改来改去 -->
        <!-- END 表单字段 -->
        <!-- 表单操作 -->
        <el-form-item>
            <el-button v-if="!isViewMode" type="primary" @click="submitForm(ruleFormRef)">
                提交
            </el-button>
            <el-button v-if="!isViewMode" @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">{{ isViewMode ? '返回' : '关闭' }}</el-button>
        </el-form-item>
        <!-- END 表单操作 -->
    </el-form>
</template>
  
<script lang="ts" setup>
import { ref, reactive, computed } from "vue"
import { queryById, insertData, updateData } from './user' // 不同页面不同的接口
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from "vue-router"
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import axios from '~/axios'
const router = useRouter()
const store = useStore()

// 判断是否为查看模式
const isViewMode = computed(() => router.currentRoute.value.query.view === 'true')

// 表单实例
const ruleFormRef = ref<FormInstance>()
// 部门选项列表
const deptOptions = ref<any[]>([])
// 表单数据 - 不同的页面，不同的表单字段
const ruleForm = reactive({
    id: 0,
    username: '',
    password: '',
    email: '',
    mobile: '',
    dept_id: null,
    ssex: '2',
    status: '1',
    avatar: '',
    description: ''
})

// 表单验证规则 - 不同的页面，不同的校验规则
// 查看模式下不需要验证
const rules = computed(() => {
    if (isViewMode.value) {
        return {}
    }
    return {
        username: [
            { required: true, message: '必填项', trigger: 'blur' }
        ],
        password: [
            { required: true, message: '必填项', trigger: 'blur' }
        ],
        email: [
            { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ],
        mobile: [
            { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
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
            updateData(ruleForm).then(async (res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    ElMessage.success('更新成功')
                    // 如果修改的是当前登录用户，重新获取完整的用户信息并更新 Vuex
                    if (store.state.userInfo && store.state.userInfo.id === ruleForm.id) {
                        try {
                            const userRes = await queryById(ruleForm.id)
                            if (userRes.data.code === 200) {
                                store.commit('setUserInfo', userRes.data.data)
                            }
                        } catch (error) {
                            // 静默处理错误
                        }
                    }
                    router.push('/userList') // 跳转回列表页面 - 不同的页面，不同的路径
                } else {
                    ElMessage.error(res.data.msg || '更新失败')
                }
            }).catch((error: any) => {
                ElMessage.error('更新失败，请稍后重试')
            })
        } else {
            insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    ElMessage.success('新增成功')
                    router.push('/userList') // 跳转回列表页面 - 不同的页面，不同的路径
                } else {
                    ElMessage.error(res.data.msg || '新增失败')
                }
            }).catch(() => {
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
// 关闭表单 - 回到数据列表页 - 不同的页面，不同的路径
const closeForm = () => {
    router.push('/userList')
}
// 加载部门数据
const loadDeptData = async () => {
    try {
        const res = await axios.get('/dept/tree')
        if (res.data.code === 200) {
            const depts = res.data.data
            // 将部门树扁平化为选项列表
            const flattenDepts = (deptList: any[], options: any[] = []) => {
                if (!deptList || !Array.isArray(deptList)) {
                    return options
                }
                deptList.forEach(dept => {
                    // 只添加有效的部门数据（id 和 dept_name 都存在）
                    if (dept.id !== undefined && dept.id !== null && dept.dept_name) {
                        options.push({ id: dept.id, name: dept.dept_name })
                    }
                    if (dept.children && dept.children.length > 0) {
                        flattenDepts(dept.children, options)
                    }
                })
                return options
            }
            deptOptions.value = flattenDepts(depts)
        }
    } catch (error) {
        // 静默处理错误
    }
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
    // 不同的页面，不同的表单字段 (注意这里的res.data.data.xxx，xxx是接口返回的字段，不同的接口，字段不同)
    ruleForm.id = res.data.data.id
    ruleForm.username = res.data.data.username
    ruleForm.password = res.data.data.password
    ruleForm.email = res.data.data.email || ''
    ruleForm.mobile = res.data.data.mobile || ''
    ruleForm.dept_id = res.data.data.dept_id
    ruleForm.ssex = res.data.data.ssex || '2'
    ruleForm.status = res.data.data.status || '1'
    ruleForm.avatar = res.data.data.avatar || ''
    ruleForm.description = res.data.data.description || ''
}

// 初始化：先加载部门数据
loadDeptData()

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
// 其他逻辑

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

/* 禁用状态的单选框和选择器 */
:deep(.el-radio.is-disabled),
:deep(.el-select.is-disabled) {
  opacity: 0.6;
}
</style>
  

