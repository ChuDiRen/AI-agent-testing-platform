<template>
    <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" label-width="120px" class="demo-ruleForm"
        status-icon>
        <el-form-item label="菜单ID" prop="menu_id">
            <el-input v-model="ruleForm.menu_id" disabled/>
        </el-form-item>
        <el-form-item label="上级菜单" prop="parent_id">
            <el-tree-select
                v-model="ruleForm.parent_id"
                :data="menuTreeOptions"
                :props="{ value: 'menu_id', label: 'menu_name', children: 'children' }"
                check-strictly
                placeholder="请选择上级菜单"
            />
        </el-form-item>
        <el-form-item label="菜单名称" prop="menu_name">
            <el-input v-model="ruleForm.menu_name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单类型" prop="type">
            <el-radio-group v-model="ruleForm.type">
                <el-radio label="0">菜单</el-radio>
                <el-radio label="1">按钮</el-radio>
            </el-radio-group>
        </el-form-item>
        <el-form-item label="图标" v-show="ruleForm.type === '0'">
            <el-input v-model="ruleForm.icon" placeholder="请输入图标类名" />
        </el-form-item>
        <el-form-item label="路由路径" v-show="ruleForm.type === '0'">
            <el-input v-model="ruleForm.path" placeholder="请输入路由路径" />
        </el-form-item>
        <el-form-item label="组件路径" v-show="ruleForm.type === '0'">
            <el-input v-model="ruleForm.component" placeholder="请输入组件路径" />
        </el-form-item>
        <el-form-item label="权限标识" prop="perms">
            <el-input v-model="ruleForm.perms" placeholder="如：system:user:add" />
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
import { queryById, insertData, updateData, getMenuTree } from './menu'
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from "vue-router"

const router = useRouter()

// 表单实例
const ruleFormRef = ref<FormInstance>()
// 菜单树选项
const menuTreeOptions = ref([{ menu_id: 0, menu_name: '顶级菜单', children: [] }])

// 表单数据
const ruleForm = reactive({
    menu_id: 0,
    parent_id: 0,
    menu_name: '',
    path: '',
    component: '',
    perms: '',
    icon: '',
    type: '0',
    order_num: 0
})

// 表单验证规则
const rules = reactive<any>({
    menu_name: [
        { required: true, message: '请输入菜单名称', trigger: 'blur' }
    ],
    type: [
        { required: true, message: '请选择菜单类型', trigger: 'change' }
    ]
})

// 加载菜单树（用于上级菜单选择）
const loadMenuTree = async () => {
    const res = await getMenuTree()
    if (res.data.code === 200) {
        menuTreeOptions.value = [{ menu_id: 0, menu_name: '顶级菜单', children: res.data.data }]
    }
}
loadMenuTree()

// 提交表单
const submitForm = async (form: FormInstance | undefined) => {
    if (!form) return
    await form.validate((valid, fields) => {
        if (!valid) {
            return 
        } 
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.menu_id > 0) {
            updateData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/menuList')
                }
            })
        } else {
            insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
                if (res.data.code == 200) {
                    router.push('/menuList')
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
    router.push('/menuList')
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
    ruleForm.menu_id = res.data.data.menu_id
    ruleForm.parent_id = res.data.data.parent_id
    ruleForm.menu_name = res.data.data.menu_name
    ruleForm.path = res.data.data.path
    ruleForm.component = res.data.data.component
    ruleForm.perms = res.data.data.perms
    ruleForm.icon = res.data.data.icon
    ruleForm.type = res.data.data.type
    ruleForm.order_num = res.data.data.order_num
}

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
let query_parent_id = router.currentRoute.value.query.parent_id

ruleForm.menu_id = query_id ? Number(query_id) : 0
if (ruleForm.menu_id > 0) {
    loadData(ruleForm.menu_id)
} else if (query_parent_id !== undefined) {
    // 新增子菜单时，设置父菜单ID
    ruleForm.parent_id = Number(query_parent_id)
}
</script>

