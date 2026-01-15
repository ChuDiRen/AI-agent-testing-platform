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
                :disabled="ruleForm.id > 0 && hasChildren(ruleForm.id)"
            />
            <div v-if="ruleForm.id > 0 && hasChildren(ruleForm.id)" class="form-tip">
                该部门下已有子部门，不建议修改上级部门
            </div>
        </el-form-item>
        <el-form-item label="部门名称" prop="dept_name">
            <el-input v-model="ruleForm.dept_name" placeholder="请输入部门名称" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="负责人" prop="leader">
            <el-input v-model="ruleForm.leader" placeholder="请输入负责人姓名" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
            <el-input v-model="ruleForm.phone" placeholder="请输入联系电话" maxlength="20" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
            <el-input v-model="ruleForm.email" placeholder="请输入邮箱地址" maxlength="100" />
        </el-form-item>
        <el-form-item label="部门状态" prop="status">
            <el-radio-group v-model="ruleForm.status">
                <el-radio value="0">正常</el-radio>
                <el-radio value="1">停用</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="排序" prop="order_num">
            <el-input-number v-model="ruleForm.order_num" :min="0" style="width: 100%;" />
            <div class="form-tip">数值越小排序越靠前</div>
        </el-form-item>
    </BaseForm>
</template>

<script setup>
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

// 部门树（用于检查是否有子部门）
const fullDeptTree = ref([])

// 表单数据
const ruleForm = reactive({
    id: 0,
    parent_id: 0,
    dept_name: '',
    leader: '',
    phone: '',
    email: '',
    status: '0',
    order_num: 0
})

// 表单验证规则
const rules = reactive({
    dept_name: [
        { required: true, message: '请输入部门名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
    ],
    phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ],
    email: [
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ]
})

// 检查部门是否有子部门
const hasChildren = (deptId) => {
    if (!deptId || deptId === 0) return false
    const findInTree = (tree) => {
        for (const dept of tree) {
            if (dept.id === deptId) {
                return dept.children && dept.children.length > 0
            }
            if (dept.children && dept.children.length > 0) {
                const found = findInTree(dept.children)
                if (found !== undefined) return found
            }
        }
        return false
    }
    return findInTree(fullDeptTree.value)
}

// 加载部门树（用于上级部门选择）
const loadDeptTree = async () => {
    const res = await getDeptTree()
    if (res.data.code === 200) {
        fullDeptTree.value = res.data.data
        // 移除当前部门及其子部门，避免形成循环
        const filteredTree = ruleForm.id > 0 
            ? removeDeptAndChildren(res.data.data, ruleForm.id)
            : res.data.data
        deptTreeOptions.value = [{ id: 0, dept_name: '顶级部门', children: filteredTree }]
    }
}

// 移除部门及其子部门
const removeDeptAndChildren = (deptList, deptId) => {
    return deptList.filter(dept => {
        if (dept.id === deptId) {
            return false
        }
        if (dept.children && dept.children.length > 0) {
            dept.children = removeDeptAndChildren(dept.children, deptId)
        }
        return true
    })
}

// 提交表单
const onBaseFormSubmit = async () => {
    // 表单验证
    if (!baseFormRef.value) {
        return
    }
    
    const valid = await baseFormRef.value.validate().catch(() => false)
    if (!valid) {
        return
    }
    
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
const loadData = async (id) => {
    try {
        const res = await queryById(id)
        if (res.data.code === 200) {
            const data = res.data.data
            ruleForm.id = data.id
            ruleForm.parent_id = data.parent_id
            ruleForm.dept_name = data.dept_name
            ruleForm.leader = data.leader || ''
            ruleForm.phone = data.phone || ''
            ruleForm.email = data.email || ''
            ruleForm.status = data.status || '0'
            ruleForm.order_num = data.order_num || 0
        } else {
            ElMessage.error(res.data.msg || '加载数据失败')
            router.push('/deptList')
        }
    } catch (error) {
        console.error('加载部门数据失败:', error)
        ElMessage.error('加载数据失败，请稍后重试')
        router.push('/deptList')
    }
}

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
let query_parent_id = router.currentRoute.value.query.parent_id

ruleForm.id = query_id ? Number(query_id) : 0

// 先加载部门树，再加载数据
loadDeptTree().then(() => {
    if (ruleForm.id > 0) {
        loadData(ruleForm.id)
    } else if (query_parent_id !== undefined) {
        // 新增子部门时，设置父部门ID
        ruleForm.parent_id = Number(query_parent_id)
    }
})
</script>

<style scoped>
.form-tip {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
    line-height: 1.4;
}
</style>
