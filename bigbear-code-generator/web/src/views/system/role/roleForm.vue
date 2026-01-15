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
        <el-form-item label="角色标识" prop="role_key">
            <el-input v-model="ruleForm.role_key" placeholder="请输入角色标识(如:admin,user)" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="显示排序" prop="role_sort">
            <el-input-number v-model="ruleForm.role_sort" :min="0" :readonly="isViewMode" />
        </el-form-item>
        <el-form-item label="数据权限" prop="data_scope">
            <el-select v-model="ruleForm.data_scope" placeholder="请选择数据权限范围" :disabled="isViewMode">
                <el-option label="全部数据权限" value="1" />
                <el-option label="自定义数据权限" value="2" />
                <el-option label="本部门数据权限" value="3" />
                <el-option label="本部门及以下数据权限" value="4" />
                <el-option label="仅本人数据权限" value="5" />
            </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
            <el-radio-group v-model="ruleForm.status" :disabled="isViewMode">
                <el-radio label="1">正常</el-radio>
                <el-radio label="0">停用</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="角色描述" prop="remark">
            <el-input type="textarea" v-model="ruleForm.remark" placeholder="请输入角色描述" :readonly="isViewMode" />
        </el-form-item>
    </BaseForm>
</template>

<script setup>
import { ref, reactive, computed } from "vue"
import { queryById, insertData, updateData } from './role'
import { useRouter } from "vue-router"
import { ElMessage } from 'element-plus'
import BaseForm from '~/components/BaseForm/index.vue'

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
    role_key: '',
    role_sort: 0,
    data_scope: '1',
    status: '1',
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
const loadData = async (id) => {
    try {
        const res = await queryById(id)
        const data = res.data.data
        ruleForm.id = data.id
        ruleForm.role_name = data.role_name
        ruleForm.role_key = data.role_key || ''
        ruleForm.role_sort = data.role_sort || 0
        ruleForm.data_scope = data.data_scope || '1'
        ruleForm.status = data.status || '1'
        ruleForm.remark = data.remark || ''
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
