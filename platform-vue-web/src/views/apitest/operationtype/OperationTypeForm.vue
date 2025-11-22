<template>
  <div class="form-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h3>{{ ruleForm.id > 0 ? '编辑操作类型' : '新增操作类型' }}</h3>
        </div>
      </template>

      <el-form 
        ref="ruleFormRef" 
        :model="ruleForm" 
        :rules="rules" 
        label-width="120px" 
        class="demo-ruleForm" 
        status-icon
      >
        <el-form-item label="操作类型编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>

        <el-form-item label="操作类型名称" prop="operation_type_name">
          <el-input 
            v-model="ruleForm.operation_type_name" 
            placeholder="请输入操作类型名称，如：数据库操作" 
          />
        </el-form-item>

        <el-form-item label="执行函数名" prop="ex_fun_name">
          <el-input 
            v-model="ruleForm.ex_fun_name" 
            placeholder="请输入执行函数名，如：execute_db_query" 
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">提交</el-button>
          <el-button @click="resetForm(ruleFormRef)">清空</el-button>
          <el-button @click="closeForm()">关闭</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive } from "vue";
import type { FormInstance, FormRules } from 'element-plus';
import { useRouter } from "vue-router";
import { ElMessage } from 'element-plus';
import { queryById, insertData, updateData } from './operationtype.js';

const router = useRouter();

// 表单实例
const ruleFormRef = ref<FormInstance>();

// 表单数据
const ruleForm = reactive({
  id: 0,
  operation_type_name: '',
  ex_fun_name: ''
});

// 表单验证规则
const rules = reactive<FormRules>({
  operation_type_name: [
    { required: true, message: '操作类型名称为必填项', trigger: 'blur' }
  ],
  ex_fun_name: [
    { required: true, message: '执行函数名为必填项', trigger: 'blur' }
  ]
});

// 提交表单
const submitForm = async (form: FormInstance | undefined) => {
  if (!form) return;
  await form.validate((valid, fields) => {
    if (!valid) {
      return;
    }
    // 有ID代表是修改，没有ID代表是新增
    if (ruleForm.id > 0) {
      updateData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
        if (res.data.code == 200) {
          ElMessage.success('更新成功');
          router.push('/OperationTypeList');
        } else {
          ElMessage.error(res.data.msg || '更新失败');
        }
      }).catch((error: any) => {
        console.error('更新失败:', error);
        ElMessage.error('更新失败，请稍后重试');
      });
    } else {
      insertData(ruleForm).then((res: { data: { code: number; msg: string; }; }) => {
        if (res.data.code == 200) {
          ElMessage.success('新增成功');
          router.push('/OperationTypeList');
        } else {
          ElMessage.error(res.data.msg || '新增失败');
        }
      }).catch((error: any) => {
        console.error('新增失败:', error);
        ElMessage.error('新增失败，请稍后重试');
      });
    }
  });
};

// 重置表单
const resetForm = (form: FormInstance | undefined) => {
  if (!form) return;
  form.resetFields();
};

// 关闭表单 - 回到数据列表页
const closeForm = () => {
  router.push('/OperationTypeList');
};

// 加载表单数据
const loadData = async (id: number) => {
  const res = await queryById(id);
  ruleForm.id = res.data.data.id;
  ruleForm.operation_type_name = res.data.data.operation_type_name;
  ruleForm.ex_fun_name = res.data.data.ex_fun_name;
};

// 如果有id参数，说明是编辑，需要获取数据
let query_id = router.currentRoute.value.query.id;
ruleForm.id = query_id ? Number(query_id) : 0;

if (ruleForm.id > 0) {
  loadData(ruleForm.id);
}
</script>

<style scoped>
.form-container {
  padding: 20px;
}

.form-card {
  max-width: 800px;
  margin: 0 auto;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.demo-ruleForm {
  padding: 20px;
}
</style>
