<template>
    <BaseForm 
        ref="baseFormRef"
        :title="ruleForm.id ? '编辑菜单' : '新增菜单'"
        :model="ruleForm" 
        :rules="rules" 
        label-width="120px"
        :loading="loading"
        @submit="onBaseFormSubmit"
        @cancel="closeForm"
    >
        <el-row :gutter="20">
            <el-col :span="24">
                <el-form-item label="菜单ID" prop="id">
                    <el-input v-model="ruleForm.id" disabled/>
                </el-form-item>
            </el-col>
            <el-col :span="24">
                <el-form-item label="上级菜单" prop="parent_id">
                    <el-tree-select
                        v-model="ruleForm.parent_id"
                        :data="menuTreeOptions"
                        :props="{ value: 'id', label: 'menu_name', children: 'children' }"
                        check-strictly
                        placeholder="请选择上级菜单"
                    />
                </el-form-item>
            </el-col>
            
            <el-col :span="24">
                <el-form-item label="菜单类型" prop="menu_type">
                    <el-radio-group v-model="ruleForm.menu_type" @change="onMenuTypeChange">
                        <el-radio value="M">目录</el-radio>
                        <el-radio value="C">菜单</el-radio>
                        <el-radio value="F">按钮</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-col>
            
            <el-col :span="24" v-if="ruleForm.menu_type !== 'F'">
                <el-form-item label="菜单图标" prop="icon">
                    <IconSelect v-model="ruleForm.icon" />
                </el-form-item>
            </el-col>
            
            <el-col :span="12">
                <el-form-item label="菜单名称" prop="menu_name">
                    <el-input v-model="ruleForm.menu_name" placeholder="请输入菜单名称" />
                </el-form-item>
            </el-col>
            
            <el-col :span="12">
                <el-form-item label="显示排序" prop="order_num">
                    <el-input-number v-model="ruleForm.order_num" controls-position="right" :min="0" style="width: 100%;" />
                </el-form-item>
            </el-col>
            
            <el-col :span="12" v-if="ruleForm.menu_type !== 'F'">
                <el-form-item label="是否外链" prop="is_frame">
                    <el-radio-group v-model="ruleForm.is_frame">
                        <el-radio value="0">是</el-radio>
                        <el-radio value="1">否</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-col>
            
            <el-col :span="12" v-if="ruleForm.menu_type !== 'F'">
                <el-form-item label="路由地址" prop="path">
                    <el-input v-model="ruleForm.path" placeholder="请输入路由地址" />
                </el-form-item>
            </el-col>
            
            <el-col :span="12" v-if="ruleForm.menu_type === 'C'">
                <el-form-item label="组件路径" prop="component">
                    <el-input v-model="ruleForm.component" placeholder="请输入组件路径" />
                </el-form-item>
            </el-col>
            
            <el-col :span="12" v-if="ruleForm.menu_type === 'C'">
                <el-form-item label="路由参数" prop="query">
                    <el-input v-model="ruleForm.query" placeholder='如：{"id": 1, "name": "ry"}' />
                </el-form-item>
            </el-col>
            
            <el-col :span="12" v-if="ruleForm.menu_type === 'C'">
                <el-form-item label="是否缓存" prop="is_cache">
                    <el-radio-group v-model="ruleForm.is_cache">
                        <el-radio value="0">缓存</el-radio>
                        <el-radio value="1">不缓存</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-col>
            
            <el-col :span="12">
                <el-form-item label="显示状态" prop="visible">
                    <el-radio-group v-model="ruleForm.visible">
                        <el-radio value="0">显示</el-radio>
                        <el-radio value="1">隐藏</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-col>
            
            <el-col :span="12">
                <el-form-item label="菜单状态" prop="status">
                    <el-radio-group v-model="ruleForm.status">
                        <el-radio value="0">正常</el-radio>
                        <el-radio value="1">停用</el-radio>
                    </el-radio-group>
                </el-form-item>
            </el-col>
            
            <el-col :span="24">
                <el-form-item label="权限标识" prop="perms">
                    <el-input v-model="ruleForm.perms" placeholder="请输入权限标识，如：system:user:list" maxlength="100" />
                </el-form-item>
            </el-col>
            
            <el-col :span="24">
                <el-form-item label="备注" prop="remark">
                    <el-input v-model="ruleForm.remark" type="textarea" :rows="3" placeholder="请输入备注" />
                </el-form-item>
            </el-col>
        </el-row>
    </BaseForm>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryById, insertData, updateData, getMenuTree } from './menu'
import { useRouter } from "vue-router"
import IconSelect from '@/components/IconSelect.vue'
import { ElMessage } from 'element-plus'
import BaseForm from '@/components/BaseForm/index.vue'

const router = useRouter()

// BaseForm 引用
const baseFormRef = ref()
const loading = ref(false)

// 菜单树选项
const menuTreeOptions = ref([{ id: 0, menu_name: '顶级菜单', children: [] }])

// 表单数据
const ruleForm = reactive({
    id: 0,
    parent_id: 0,
    menu_name: '',
    path: '',
    component: '',
    query: '',
    perms: '',
    icon: '',
    menu_type: 'C', // M目录 C菜单 F按钮
    visible: '0',   // 0显示 1隐藏
    status: '0',    // 0正常 1停用
    is_cache: '0',  // 0缓存 1不缓存
    is_frame: '1',  // 0是 1否
    order_num: 0,
    remark: ''
})

// 表单验证规则
const rules = reactive<any>({
    menu_name: [
        { required: true, message: '请输入菜单名称', trigger: 'blur' }
    ],
    menu_type: [
        { required: true, message: '请选择菜单类型', trigger: 'change' }
    ],
    order_num: [
        { required: true, message: '请输入显示排序', trigger: 'blur' }
    ]
})

// 菜单类型变化时的处理
const onMenuTypeChange = (value: string) => {
    // 清空某些字段
    if (value === 'F') {
        // 按钮不需要路由相关信息
        ruleForm.path = ''
        ruleForm.component = ''
        ruleForm.icon = ''
        ruleForm.is_cache = '0'
        ruleForm.is_frame = '1'
    } else if (value === 'M') {
        // 目录不需要组件
        ruleForm.component = ''
        ruleForm.is_cache = '0'
    }
}

// 加载菜单树（用于上级菜单选择）
const loadMenuTree = async () => {
    const res = await getMenuTree()
    if (res.data.code === 200) {
        menuTreeOptions.value = [{ id: 0, menu_name: '顶级菜单', children: res.data.data }]
    }
}
loadMenuTree()

// 提交表单
const onBaseFormSubmit = async () => {
    loading.value = true
    try {
        // 有ID 代表是修改， 没ID 代表是新增
        if (ruleForm.id > 0) {
            const res = await updateData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('更新成功')
                router.push('/menuList')
            } else {
                ElMessage.error(res.data.msg || '更新失败')
            }
        } else {
            const res = await insertData(ruleForm)
            if (res.data.code == 200) {
                ElMessage.success('新增成功')
                router.push('/menuList')
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
    router.push('/menuList')
}

// 加载表单数据
const loadData = async (id: number) => {
    const res = await queryById(id)
    ruleForm.id = res.data.data.id
    ruleForm.parent_id = res.data.data.parent_id
    ruleForm.menu_name = res.data.data.menu_name
    ruleForm.path = res.data.data.path || ''
    ruleForm.component = res.data.data.component || ''
    ruleForm.query = res.data.data.query || ''
    ruleForm.perms = res.data.data.perms || ''
    ruleForm.icon = res.data.data.icon || ''
    ruleForm.menu_type = res.data.data.menu_type || 'C'
    ruleForm.visible = res.data.data.visible || '0'
    ruleForm.status = res.data.data.status || '0'
    ruleForm.is_cache = res.data.data.is_cache || '0'
    ruleForm.is_frame = res.data.data.is_frame || '1'
    ruleForm.order_num = res.data.data.order_num || 0
    ruleForm.remark = res.data.data.remark || ''
}

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id
let query_parent_id = router.currentRoute.value.query.parent_id

ruleForm.id = query_id ? Number(query_id) : 0
if (ruleForm.id > 0) {
    loadData(ruleForm.id)
} else if (query_parent_id !== undefined) {
    // 新增子菜单时，设置父菜单ID
    ruleForm.parent_id = Number(query_parent_id)
}
</script>

