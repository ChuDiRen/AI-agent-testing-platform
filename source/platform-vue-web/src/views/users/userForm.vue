<template>
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
        <!-- 不同的页面，不同的表单字段 -->
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="用户名" prop="username">
            <el-input v-model="ruleForm.username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
            <el-input v-model="ruleForm.password" type="password" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
            <el-input v-model="ruleForm.email" />
        </el-form-item>
        <el-form-item label="联系电话" prop="mobile">
            <el-input v-model="ruleForm.mobile" />
        </el-form-item>
        <el-form-item label="部门ID" prop="dept_id">
            <el-input v-model.number="ruleForm.dept_id" type="number" />
        </el-form-item>
        <el-form-item label="性别" prop="ssex">
            <el-radio-group v-model="ruleForm.ssex">
                <el-radio label="0">男</el-radio>
                <el-radio label="1">女</el-radio>
                <el-radio label="2">保密</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="状态" prop="status">
            <el-radio-group v-model="ruleForm.status">
                <el-radio label="1">有效</el-radio>
                <el-radio label="0">锁定</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="头像" prop="avatar">
            <el-input v-model="ruleForm.avatar" placeholder="头像URL" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
            <el-input v-model="ruleForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <!-- 如果有不需要展示在页面的属性，建议通过 v-show="false" 进行控制，不要直接删除，这样方便你后续改来改去 -->
        <!-- END 表单字段 -->
        <!-- 表单操作 -->
        <el-form-item>
            <el-button type="primary" @click="submitForm(ruleFormRef)">
                提交
            </el-button>
            <el-button @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
        <!-- END 表单操作 -->
    </el-form>
</template>
  
<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryById, insertData, updateData } from './user' // 不同页面不同的接口
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from "vue-router";
const router = useRouter()

// 表单实例
const ruleFormRef = ref<FormInstance>()
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
const rules = reactive<any>({
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
                    router.push('/userList') // 跳转回列表页面 - 不同的页面，不同的路径
                }
            })
        } else {
            insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/userList') // 跳转回列表页面 - 不同的页面，不同的路径
                }
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

// 如果有id参数，说明是编辑，需要获取数据
console.log(router)
let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
// 其他逻辑

</script>
  

