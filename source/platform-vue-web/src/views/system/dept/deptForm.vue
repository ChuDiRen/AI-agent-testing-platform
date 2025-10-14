<template>
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
        <el-form-item label="部门ID" prop="dept_id">
            <el-input v-model="ruleForm.dept_id" disabled/>
        </el-form-item>
        <el-form-item label="上级部门" prop="parent_id">
            <el-tree-select
                v-model="ruleForm.parent_id"
                :data="deptTreeOptions"
                :props="{ value: 'dept_id', label: 'dept_name', children: 'children' }"
                check-strictly
                placeholder="请选择上级部门"
            />
        </el-form-item>
        <el-form-item label="部门名称" prop="dept_name">
            <el-input v-model="ruleForm.dept_name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="排序" prop="order_num">
            <el-input-number v-model="ruleForm.order_num" :min="0" />
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
import { queryById, insertData, updateData, getDeptTree } from './dept'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from "vue-router"

const router = useRouter()

// 表单实例
const ruleFormRef = ref<FormInstance>()
// 部门树选项
const deptTreeOptions = ref([{ dept_id: 0, dept_name: '顶级部门', children: [] }])

// 表单数据
const ruleForm = reactive({
    dept_id: 0,
    parent_id: 0,
    dept_name: '',
    order_num: 0
})

// 表单验证规则
const rules = reactive<any>({
    dept_name: [
        { required: true, message: '请输入部门名称', trigger: 'blur' }
    ]
})

// 加载部门树（用于上级部门选择）
const loadDeptTree = async () => {
    const res = await getDeptTree()
    if (res.data.code === 200) {
        deptTreeOptions.value = [{ dept_id: 0, dept_name: '顶级部门', children: res.data.data }]
    }
}
loadDeptTree()

// 提交表单
const submitForm = async (form: FormInstance | undefined) => {
    if (!form) return
    await form.validate((valid, fields) => {
        if (!valid) {
            return 
        } 
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.dept_id > 0) {
            updateData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/deptList')
                }
            })
        } else {
            insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/deptList')
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
    router.push('/deptList')
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
    ruleForm.dept_id = res.data.data.dept_id
    ruleForm.parent_id = res.data.data.parent_id
    ruleForm.dept_name = res.data.data.dept_name
    ruleForm.order_num = res.data.data.order_num
}

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
let query_parent_id = router.currentRoute.value.query.parent_id

ruleForm.dept_id = query_id ? Number(query_id) : 0
if (ruleForm.dept_id > 0) {
    loadData(ruleForm.dept_id)
} else if (query_parent_id !== undefined) {
    // 新增子部门时，设置父部门ID
    ruleForm.parent_id = Number(query_parent_id)
}
</script>

