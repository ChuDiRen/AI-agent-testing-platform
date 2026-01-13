<template>
  <el-row class="login-container">
    <!-- flex 创建一个弹性区域 -->
    <!-- items-center 垂直居中 -->
    <!-- justify-center 水平居中 -->
    <!-- flex-col 一个div占一行 -->
    <el-col :lg="16" class="left">
      <div>欢迎光临华测教育</div>
      <div>
        欢迎使用华测教育的在线测试平台学习,这里是《高级测试开发课》的演示地址
      </div>
    </el-col>
    <el-col :lg="8" class="right"  >
      <!-- 欢迎回来 -->
      <h2 class="title">欢迎回来</h2>
      <!-- 标题  -->
      <div>
        <span class="line"></span>
        <span>账号密码登录</span>
        <span class="line"></span>
      </div>

      <!-- 登录主模块 -->
      <el-form  ref="formRef" :model="form" :rules="rules" class="w-[250px]">
        <el-form-item prop="username">
          <!-- 输入用户名 并且带上图标-->
          <el-input v-model="form.username" placeholder="请输入用户名" >
            <template #prefix>
              <el-icon class="el-input__icon"><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <!-- 输入密码 并且带上图标-->
        <el-form-item  prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" type="password" show-password>
            <template #prefix>
              <el-icon class="el-input__icon"><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button round type="primary" @click="onSubmit" class="w-[250px]">
          登 录
          </el-button>
        </el-form-item>
      </el-form>
    </el-col>
  </el-row>
</template>

<script setup>
// 导入响应式模块
import { ref,reactive } from "vue";
// 导入route管理
import { useRouter } from "vue-router";
//  导入登录的脚本
import { login} from "./login";
import { ElMessage } from "element-plus";
// 实例化对象
const router = useRouter();


// 字段校验：script增加如下代码
const rules = {
  username: [{ required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 3, max: 15, message: '用户名长度必须在3-15之间', trigger: 'blur' },],
  password: [{ required: true, message: '密码不能为空', trigger: 'blur' },
  { min: 6, max: 12, message: '用户名长度必须在6-12之间', trigger: 'blur' },],
  // ...
}

// do not use same name with ref
const form = reactive({
  username: "",
  password: "",
});

// 第一步：获取页面的数据-响应式API(记得要导入)
const formRef =ref(null)
// 第二步：进行数据校验
const onSubmit = () => {
  // 执行对应的数据校验
  console.log(formRef.value.validate); // 回调函数...执行一遍之后结果可以当参数传递
  // 函数即可调用
  formRef.value.validate((valid)=>{
    console.log(valid) // 无数据返回：false；否则返回：true
    // 接下来我们就可以在这个位置写逻辑
    if(!valid){
      console.log("校验不通过")
      return false // 如果是false ，则直接返回
    }
    console.log("校验通过")
    // 验证通过之后进行开始发送请求
    login(form.username,form.password)
    .then(res=>{
      console.log("当前的响应数据：",res.data.data.token)

      // 前端进行判断并且跳转
      if(res.data.code ==200 && res.data.data.token != null){
      // 写入token到请求头中
      // 存储令牌（加密后的字符串）
      localStorage.setItem('token', res.data.data.token);
      console.log("312321321312321")
      router.push("/home")// 假设我们跳转到主页面
      ElMessage.success(res.data.msg)
      }
    })
    .catch(err=>{
       console.log(err)
    })
    // router.push("/home")// 假设我们跳转到主页面
  })
};




</script>

<style scoped>
.login-container {
  @apply min-h-screen bg-indigo-400;
}
/* 对应的样式可以重名叠加，多个可以用逗号分割 */
.login-container .left,
.login-container .right {
  @apply flex items-center justify-center;
}
.login-container .left
{
  @apply  flex-col;
}
.login-container .right {
  @apply flex-col bg-indigo-50;
}

/* 类下面的第一个div */
.left>div:first-child {
  @apply font-bold text-5xl text-light-50 mb-4;
}
/* 类下面的最后一个div */
.left> div:last-child {
  @apply text-sm text-gray-200;
}

/* 标题 */
.right .title {
  @apply font-bold text-3xl text-gray-800;
}
/* 主题内容 */
.right > div {
  @apply flex items-center justify-center my-5 text-gray-300 space-x-2;
}
/* 横线 */
.right .line {
  @apply h-[1px] w-16 bg-gray-200;
}
</style>