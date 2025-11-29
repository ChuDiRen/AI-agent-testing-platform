<template>
    <BaseForm 
        ref="baseFormRef"
        :title="isViewMode ? '角色详情' : (ruleForm.id ? '编辑角色' : '新增角色')"
        :model="ruleForm" 
        :rules="rules" 
        label-width="120px"
        :loading="loading"
        @submit="onBaseFormSubmit"
        @cancel="closeForm"
    >
        <el-form-item label="角色ID" prop="id">
            <el-input v-model="ruleForm.id" disabled/>
        </el-form-item>
        <el-form-item label="角色名称" prop="role_name">
            <el-input v-model="ruleForm.role_name" placeholder="请输入角色名称" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="角色描述" prop="remark">
            <el-input type="textarea" v-model="ruleForm.remark" placeholder="请输入角色描述" :readonly="isViewMode" />
        </el-form-item>
    </BaseForm>
</template>

<script lang="ts" setup>
import { ref, reactive, computed } from "vue"
import { queryById, insertData, updateData } from './role'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'
import BaseForm from '@/components/BaseForm/index.vue'

const router = useRouter()

// 判断是否为查看模式
const isViewMode = computed(() => router.currentRoute.value.query.view === 'true')

// BaseForm 引用
const baseFormRef = ref()
const loading = ref(false)

// 表单数据
const ruleForm = reactive({
    id: 0,
    role_name: '',
    remark: ''
})

// 表单验证规则
const rules = computed(() => {
    if (isViewMode.value) {
        return {}
    }
    return {
        role_name: [
            { required: true, message: '请输入角色名称', trigger: 'blur' }
        ]
    }
})

// 提交表单
const onBaseFormSubmit = async () => {
    loading.value = true
    try {
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.id > 0) {
            const res = await updateData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('更新成功')
                router.push('/roleList')
            } else {
                ElMessage.error(res.data.msg || '更新失败')
            }
        } else {
            const res = await insertData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('新增成功')
                router.push('/roleList')
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
    router.push('/roleList')
}

// 加载表单数据
const loadData = async (id: number) => {
    try {
        const res = await queryById(id)
        ruleForm.id = res.data.data.id
        ruleForm.role_name = res.data.data.role_name
        ruleForm.remark = res.data.data.remark || ''
    } catch (error) {
        console.error('加载数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
    }
}

// 如果有id参数，说明是编辑或查看，需要获取数据
let query_id = router.currentRoute.value.query.id
ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
}
</script>

<style scoped>
</style>
