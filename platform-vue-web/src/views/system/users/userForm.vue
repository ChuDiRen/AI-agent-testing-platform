<template>
    <BaseForm 
        ref="baseFormRef"
        :title="isViewMode ? '用户详情' : (ruleForm.id ? '编辑用户' : '新增用户')"
        :model="ruleForm" 
        :rules="rules" 
        label-width="120px"
        :loading="loading"
        @submit="onBaseFormSubmit"
        @cancel="closeForm"
    >
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
        <!-- END 表单字段 -->
        
        <!-- 底部按钮已被BaseForm接管 -->
    </BaseForm>
</template>
  
<script lang="ts" setup>
import { ref, reactive, computed } from "vue"
import { queryById, insertData, updateData } from './user'
import { getDeptTree } from '~/views/system/dept/dept'
import { useRouter } from "vue-router"
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import BaseForm from '~/components/BaseForm/index.vue'

const router = useRouter()
const store = useStore()

// 判断是否为查看模式
const isViewMode = computed(() => router.currentRoute.value.query.view === 'true')

// BaseForm 引用
const baseFormRef = ref()
const loading = ref(false)

// 部门选项列表
const deptOptions = ref<any[]>([])
// 表单数据
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

// 表单验证规则
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

// 提交表单 (BaseForm 已验证通过)
const onBaseFormSubmit = async () => {
    loading.value = true
    try {
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.id > 0) {
            const res = await updateData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('更新成功')
                // 如果修改的是当前登录用户，重新获取完整的用户信息并更新 Vuex
                if (store.state.userInfo && store.state.userInfo.id === ruleForm.id) {
                    try {
                        const userRes = await queryById(ruleForm.id)
                        if (userRes.data.code === 200) {
                            store.commit('setUserInfo', userRes.data.data)
                        }
                    } catch (error) { }
                }
                router.push('/userList')
            } else {
                ElMessage.error(res.data.msg || '更新失败')
            }
        } else {
            const res = await insertData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('新增成功')
                router.push('/userList')
            } else {
                ElMessage.error(res.data.msg || '新增失败')
            }
        }
    } catch (error) {
        ElMessage.error('操作失败，请稍后重试')
    } finally {
        loading.value = false
    }
}

// 关闭表单
const closeForm = () => {
    router.push('/userList')
}

// 加载部门数据
const loadDeptData = async () => {
    try {
        const res = await getDeptTree()
        if (res.data.code === 200) {
            const depts = res.data.data
            const flattenDepts = (deptList: any[], options: any[] = []) => {
                if (!deptList || !Array.isArray(deptList)) {
                    return options
                }
                deptList.forEach(dept => {
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
    } catch (error) { }
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
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

// 初始化
loadDeptData()

let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
</script>

<style scoped>
</style>
  

