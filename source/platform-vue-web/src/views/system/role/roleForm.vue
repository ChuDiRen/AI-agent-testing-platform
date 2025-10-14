<template>
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
        <el-form-item label="角色ID" prop="role_id">
            <el-input v-model="ruleForm.role_id" disabled/>
        </el-form-item>
        <el-form-item label="角色名称" prop="role_name">
            <el-input v-model="ruleForm.role_name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色描述" prop="remark">
            <el-input type="textarea" v-model="ruleForm.remark" placeholder="请输入角色描述" />
        </el-form-item>
        <!-- 表单操作 -->
        <el-form-item>
            <el-button type="primary" @click="submitForm(ruleFormRef)">
                提交
            </el-button>
            <el-button @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryById, insertData, updateData } from './role'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from "vue-router"

const router = useRouter()

// 表单实例
const ruleFormRef = ref<FormInstance>()
// 表单数据
const ruleForm = reactive({
    role_id: 0,
    role_name: '',
    remark: ''
})

// 表单验证规则
const rules = reactive<any>({
    role_name: [
        { required: true, message: '请输入角色名称', trigger: 'blur' }
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
        if (ruleForm.role_id > 0) {
            updateData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/roleList')
                }
            })
        } else {
            insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/roleList')
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

// 关闭表单
const closeForm = () => {
    router.push('/roleList')
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
    ruleForm.role_id = res.data.data.role_id
    ruleForm.role_name = res.data.data.role_name
    ruleForm.remark = res.data.data.remark
}

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
ruleForm.role_id = query_id ? Number(query_id) : 0
if (ruleForm.role_id > 0) {
    loadData(ruleForm.role_id)
}
</script>

