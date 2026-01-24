<template>
  <div>
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="角色名称" prop="name">
            <el-input v-model="ruleForm.name" />
        </el-form-item>
        <el-form-item label="角色描述" prop="desc">
            <el-input v-model="ruleForm.desc" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(ruleFormRef)">
                提交
            </el-button>
            <el-button @click="resetForm(ruleFormRef)">清空</el-button>
            <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue"
import roleApi from './roleApi'
import { useRouter } from "vue-router"
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const ruleFormRef = ref(null)

const ruleForm = reactive({
    id: 0,
    name: '',
    desc: ''
})

const rules = reactive({
    name: [
        { required: true, message: '必填项', trigger: 'blur' }
    ]
})

const submitForm = async (form) => {
    if (!form) return
    await form.validate((valid, fields) => {
        if (!valid) {
            return
        }
        if (ruleForm.id > 0) {
            roleApi.updateData(ruleForm).then((res) => {
                if (res.data.code == 200) {
                    router.push('/roleList')
                }
            })
        } else {
            roleApi.insertData(ruleForm).then((res) => {
                if (res.data.code == 200) {
                    router.push('/roleList')
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
    const res = await roleApi.queryById(id)
    ruleForm.id = res.data.data.id
    ruleForm.name = res.data.data.name
    ruleForm.desc = res.data.data.desc
}

let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
</script>
