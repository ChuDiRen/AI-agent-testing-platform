<template>
    <BaseForm 
        ref="baseFormRef"
        :title="ruleForm.id ? '编辑部门' : '新增部门'"
        :model="ruleForm" 
        :rules="rules" 
        label-width="120px"
        :loading="loading"
        @submit="onBaseFormSubmit"
        @cancel="closeForm"
    >
        <el-form-item label="部门ID" prop="id">
            <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="上级部门" prop="parent_id">
            <el-tree-select
                v-model="ruleForm.parent_id"
                :data="deptTreeOptions"
                :props="{ value: 'id', label: 'dept_name', children: 'children' }"
                check-strictly
                placeholder="请选择上级部门"
            />
        </el-form-item>
        <el-form-item label="部门名称" prop="dept_name">
            <el-input v-model="ruleForm.dept_name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="排序" prop="order_num">
            <el-input-number v-model="ruleForm.order_num" :min="0" style="width: 100%;" />
        </el-form-item>
    </BaseForm>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryById, insertData, updateData, getDeptTree } from './dept'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'
import BaseForm from '~/components/BaseForm/index.vue'

const router = useRouter()

// BaseForm 引用
const baseFormRef = ref()
const loading = ref(false)

// 部门树选项
const deptTreeOptions = ref([{ id: 0, dept_name: '顶级部门', children: [] }])

// 表单数据
const ruleForm = reactive({
    id: 0,
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
        deptTreeOptions.value = [{ id: 0, dept_name: '顶级部门', children: res.data.data }]
    }
}
loadDeptTree()

// 提交表单
const onBaseFormSubmit = async () => {
    loading.value = true
    try {
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.id > 0) {
            const res = await updateData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('更新成功')
                router.push('/deptList')
            } else {
                ElMessage.error(res.data.msg || '更新失败')
            }
        } else {
            const res = await insertData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('新增成功')
                router.push('/deptList')
            } else {
                ElMessage.error(res.data.msg || '新增失败')
            }
        }
    } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error('操作失败，请稍后重试')
    } finally {
        loading.value = false
    }
}

// 关闭表单
const closeForm = () => {
    router.push('/deptList')
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
    ruleForm.id = res.data.data.id
    ruleForm.parent_id = res.data.data.parent_id
    ruleForm.dept_name = res.data.data.dept_name
    ruleForm.order_num = res.data.data.order_num
}

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
let query_parent_id = router.currentRoute.value.query.parent_id

ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
} else if (query_parent_id !== undefined) {
    // 新增子部门时，设置父部门ID
    ruleForm.parent_id = Number(query_parent_id)
}
</script>
