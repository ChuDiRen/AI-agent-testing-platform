<template>
  <div>
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="部门名称" prop="name">
            <el-input v-model="ruleForm.name" />
        </el-form-item>
        <el-form-item label="备注" prop="desc">
            <el-input v-model="ruleForm.desc" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
            <el-input-number v-model="ruleForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="父级ID" prop="parent_id">
            <el-input-number v-model="ruleForm.parent_id" :min="0" />
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
import deptApi from './deptApi'
import { useRouter } from "vue-router"
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const ruleFormRef = ref(null)

const ruleForm = reactive({
    id: 0,
    name: '',
    desc: '',
    order: 0,
    parent_id: 0
})

const rules = reactive({
    name: [{ required: true, message: '必填项', trigger: 'blur' }]
})

const submitForm = async (form) => {
    if (!form) return
    await form.validate((valid) => {
        if (!valid) return
        if (ruleForm.id > 0) {
            deptApi.updateData(ruleForm).then((res) => {
                if (res.data.code == 200) router.push('/deptList')
            })
        } else {
            deptApi.insertData(ruleForm).then((res) => {
                if (res.data.code == 200) router.push('/deptList')
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
    const res = await deptApi.queryById(id)
    Object.assign(ruleForm, res.data.data)
}

let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) loadData(ruleForm.id)
</script>
