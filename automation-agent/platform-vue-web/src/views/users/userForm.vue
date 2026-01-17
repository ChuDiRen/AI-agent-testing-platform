<template>
  <div>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
        <!-- 不同的页面，不同的表单字段 -->
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="用户名" prop="username">
            <el-input v-model="ruleForm.username" />
        </el-form-item>
        <el-form-item label="姓名" prop="alias">
            <el-input v-model="ruleForm.alias" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
            <el-input v-model="ruleForm.email" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
            <el-input v-model="ruleForm.phone" />
        </el-form-item>
        <el-form-item v-if="ruleForm.id === 0" label="密码" prop="password">
            <el-input v-model="ruleForm.password" type="password" show-password placeholder="新增用户时必填" />
        </el-form-item>
        <el-form-item label="角色" prop="role_ids">
            <el-checkbox-group v-model="ruleForm.role_ids">
                <el-checkbox v-for="role in roleOptions" :key="role.id" :value="role.id">
                    {{ role.name }}
                </el-checkbox>
            </el-checkbox-group>
        </el-form-item>
        <el-form-item label="部门" prop="dept_id">
            <el-tree-select v-model="ruleForm.dept_id" :data="deptOptions" :props="{ label: 'name', value: 'id' }"
                placeholder="请选择部门" clearable check-strictly />
        </el-form-item>
        <el-form-item label="超级用户">
            <el-switch v-model="ruleForm.is_superuser" />
        </el-form-item>
        <el-form-item label="启用状态">
            <el-switch v-model="ruleForm.is_active" />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(ruleFormRef)">
                提交
            </el-button>
            <el-button @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
        <!-- END 表单操作 -->
    </el-form>
  </div>
</template>
  
<script setup>
import { ref, reactive, onMounted } from "vue"
import userApi from './userApi'
import roleApi from '../roles/roleApi'
import deptApi from '../depts/deptApi'
import { useRouter } from "vue-router"
import Breadcrumb from "../Breadcrumb.vue"
const router = useRouter()

const ruleFormRef = ref()
const roleOptions = ref([])
const deptOptions = ref([])

const ruleForm = reactive({
    id: 0,
    username: '',
    alias: '',
    email: '',
    phone: '',
    password: '',
    role_ids: [],
    dept_id: null,
    is_superuser: false,
    is_active: true
})

const rules = reactive({
    username: [
        { required: true, message: '必填项', trigger: 'blur' }
    ],
    email: [
        { required: true, message: '必填项', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '新增用户时密码必填', trigger: 'blur' }
    ],
    role_ids: [
        { required: true, message: '请至少选择一个角色', trigger: 'change' }
    ]
})

const loadRoleOptions = async () => {
    try {
        const res = await roleApi.queryByPage({ page: 1, pageSize: 9999 })
        if (res.data.code === 200) {
            roleOptions.value = res.data.data
        }
    } catch (error) {
        console.error('加载角色列表失败:', error)
    }
}

const loadDeptOptions = async () => {
    try {
        const res = await deptApi.queryTree()
        if (res.data.code === 200) {
            deptOptions.value = res.data.data
        }
    } catch (error) {
        console.error('加载部门列表失败:', error)
    }
}

onMounted(() => {
    loadRoleOptions()
    loadDeptOptions()
})

const submitForm = async (form) => {
    if (!form) return
    await form.validate((valid) => {
        if (!valid) {
            return 
        }
        if (ruleForm.id > 0) {
            userApi.updateData(ruleForm).then((res) => {
                if (res.data.code == 200) {
                    router.push('/userList')
                }
            })
        } else {
            userApi.insertData(ruleForm).then((res) => {
                if (res.data.code == 200) {
                    router.push('/userList')
                }
            })
        }
    })
}

const resetForm = (form) => {
    if (!form) return
    form.resetFields()
}

const closeForm = () => {
    router.back()
}

const loadData = async (id) => {
    const res = await userApi.queryById(id)
    const data = res.data.data
    ruleForm.id = data.id
    ruleForm.username = data.username
    ruleForm.alias = data.alias
    ruleForm.email = data.email
    ruleForm.phone = data.phone
    ruleForm.password = ''
    ruleForm.role_ids = data.roles?.map((r) => r.id) || []
    ruleForm.dept_id = data.dept?.id || null
    ruleForm.is_superuser = data.is_superuser || false
    ruleForm.is_active = data.is_active !== false
}

let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
</script>
  

