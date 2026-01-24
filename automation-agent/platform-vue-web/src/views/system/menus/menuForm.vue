<template>
  <div>
    <Breadcrumb />
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm" status-icon>
        <el-form-item label="编号" prop="id">
            <el-input v-model="ruleForm.id" disabled />
        </el-form-item>
        <el-form-item label="菜单名称" prop="name">
            <el-input v-model="ruleForm.name" />
        </el-form-item>
        <el-form-item label="菜单类型" prop="menu_type">
            <el-select v-model="ruleForm.menu_type" placeholder="选择类型">
                <el-option label="目录" value="catalog" />
                <el-option label="菜单" value="menu" />
            </el-select>
        </el-form-item>
        <el-form-item label="菜单路径" prop="path">
            <el-input v-model="ruleForm.path" />
        </el-form-item>
        <el-form-item label="图标" prop="icon">
            <el-input v-model="ruleForm.icon" />
        </el-form-item>
        <el-form-item label="组件" prop="component">
            <el-input v-model="ruleForm.component" />
        </el-form-item>
        <el-form-item label="排序" prop="order">
            <el-input-number v-model="ruleForm.order" :min="0" />
        </el-form-item>
        <el-form-item label="父级ID" prop="parent_id">
            <el-input-number v-model="ruleForm.parent_id" :min="0" />
        </el-form-item>
        <el-form-item label="是否隐藏">
            <el-switch v-model="ruleForm.is_hidden" />
        </el-form-item>
        <el-form-item label="是否缓存">
            <el-switch v-model="ruleForm.keepalive" />
        </el-form-item>
        <el-form-item label="重定向">
            <el-input v-model="ruleForm.redirect" />
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
import menuApi from './menuApi'
import { useRouter } from "vue-router"
import Breadcrumb from "../Breadcrumb.vue"

const router = useRouter()
const ruleFormRef = ref(null)

const ruleForm = reactive({
    id: 0,
    name: '',
    menu_type: 'catalog',
    path: '',
    icon: '',
    component: 'Layout',
    order: 0,
    parent_id: 0,
    is_hidden: false,
    keepalive: true,
    redirect: ''
})

const rules = reactive({
    name: [{ required: true, message: '必填项', trigger: 'blur' }],
    path: [{ required: true, message: '必填项', trigger: 'blur' }],
    component: [{ required: true, message: '必填项', trigger: 'blur' }]
})

const submitForm = async (form) => {
    if (!form) return
    await form.validate((valid) => {
        if (!valid) return
        if (ruleForm.id > 0) {
            menuApi.updateData(ruleForm).then((res) => {
                if (res.data.code == 200) router.push('/menuList')
            })
        } else {
            menuApi.insertData(ruleForm).then((res) => {
                if (res.data.code == 200) router.push('/menuList')
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
    const res = await menuApi.queryById(id)
    Object.assign(ruleForm, res.data.data)
}

let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) loadData(ruleForm.id)
</script>
