<template>
  <div>
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="API路径" prop="path">
            <el-input v-model="ruleForm.path" placeholder="/api/xxx" />
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
            <el-select v-model="ruleForm.method" placeholder="选择方法">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
            </el-select>
        </el-form-item>
        <el-form-item label="请求简介" prop="summary">
            <el-input v-model="ruleForm.summary" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="API标签" prop="tags">
            <el-input v-model="ruleForm.tags" placeholder="user, role, menu..." />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
            <el-button @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import apiApi from './apiApi'
import { useRouter } from "vue-router"
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const ruleFormRef = ref(null)

const ruleForm = reactive({
    id: 0,
    path: '',
    method: 'GET',
    summary: '',
    tags: ''
})

const rules = reactive({
    path: [{ required: true, message: '必填项', trigger: 'blur' }],
    method: [{ required: true, message: '必填项', trigger: 'change' }]
})

const submitForm = async (form) => {
    if (!form) return
    await form.validate((valid) => {
        if (!valid) return
        if (ruleForm.id > 0) {
            apiApi.updateData(ruleForm).then((res) => {
                if (res.data.code == 200) router.push('/apiList')
            })
        } else {
            apiApi.insertData(ruleForm).then((res) => {
                if (res.data.code == 200) router.push('/apiList')
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
    const res = await apiApi.queryById(id)
    Object.assign(ruleForm, res.data.data)
}

let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) loadData(ruleForm.id)
</script>
