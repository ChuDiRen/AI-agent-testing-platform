<template>
  <div class="form-container">
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <h3>{{ ruleForm.id > 0 ? '编辑用例步骤' : '新增用例步骤' }}</h3>
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
        <el-form-item label="步骤编号" prop="id">
          <el-input v-model="ruleForm.id" disabled />
        </el-form-item>

        <el-form-item label="用例ID" prop="api_case_info_id">
          <el-input-number 
            v-model="ruleForm.api_case_info_id" 
            :min="1"
            placeholder="请输入用例ID" 
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="关键字" prop="key_word_id">
          <el-select 
            v-model="ruleForm.key_word_id" 
            placeholder="请选择关键字" 
            style="width: 100%"
            filterable
          >
            <el-option 
              v-for="keyword in keywordList" 
              :key="keyword.id" 
              :label="keyword.name" 
              :value="keyword.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="步骤描述" prop="step_desc">
          <el-input 
            v-model="ruleForm.step_desc" 
            type="textarea"
            :rows="3"
            placeholder="请输入步骤描述" 
          />
        </el-form-item>

        <el-form-item label="引用变量" prop="ref_variable">
          <el-input 
            v-model="ruleForm.ref_variable" 
            placeholder="请输入引用变量，如：${user_id}" 
          />
        </el-form-item>

        <el-form-item label="执行顺序" prop="run_order">
          <el-input-number 
            v-model="ruleForm.run_order" 
            :min="1"
            placeholder="请输入执行顺序" 
            style="width: 100%"
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
import { queryById, insertData, updateData } from './apiinfocasestep.js';
import { queryAll as queryAllKeywords } from '../keyword/apiKeyWord.js';

const router = useRouter();

// 表单实例
const ruleFormRef = ref<FormInstance>();

// 表单数据
const ruleForm = reactive({
  id: 0,
  api_case_info_id: 0,
  key_word_id: 0,
  step_desc: '',
  ref_variable: '',
  run_order: 1
});

// 关键字列表
const keywordList = ref([]);

// 加载关键字列表
const loadKeywords = () => {
  queryAllKeywords().then((res: { data: { code: number; data: any; msg: string } }) => {
    if (res.data.code === 200) {
      keywordList.value = res.data.data || [];
    } else {
      console.error('加载关键字失败:', res.data.msg);
    }
  }).catch((error: any) => {
    console.error('加载关键字失败:', error);
  });
};
loadKeywords();

// 表单验证规则
const rules = reactive<FormRules>({
  api_case_info_id: [
    { required: true, message: '用例ID为必填项', trigger: 'blur' }
  ],
  key_word_id: [
    { required: true, message: '关键字为必填项', trigger: 'change' }
  ],
  step_desc: [
    { required: true, message: '步骤描述为必填项', trigger: 'blur' }
  ],
  run_order: [
    { required: true, message: '执行顺序为必填项', trigger: 'blur' }
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
          router.push('/ApiInfoCaseStepList');
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
          router.push('/ApiInfoCaseStepList');
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
  router.push('/ApiInfoCaseStepList');
};

// 加载表单数据
const loadData = async (id: number) => {
  const res = await queryById(id);
  ruleForm.id = res.data.data.id;
  ruleForm.api_case_info_id = res.data.data.api_case_info_id;
  ruleForm.key_word_id = res.data.data.key_word_id;
  ruleForm.step_desc = res.data.data.step_desc;
  ruleForm.ref_variable = res.data.data.ref_variable;
  ruleForm.run_order = res.data.data.run_order;
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
