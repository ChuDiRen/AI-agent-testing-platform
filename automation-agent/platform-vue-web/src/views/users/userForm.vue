<template>
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
        <el-form-item label="密码" prop="password">
            <el-input v-model="ruleForm.password" />
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
import Breadcrumb from "../Breadcrumb.vue"; // 面包屑导航，导入
const router = useRouter()

// 表单实例
const ruleFormRef = ref<FormInstance>()
// 表单数据 - 不同的页面，不同的表单字段
const ruleForm = reactive({
    id: 0,
    username: '',
    password: ''
})

// 表单验证规则 - 不同的页面，不同的校验规则
const rules = reactive<any>({
    username: [
        { required: true, message: '必填项', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '必填项', trigger: 'blur' }
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
  

