<template>
  <!--100vh就沾满了整个屏幕-->
  <!--上面这个是vite的CSS 下面是EL的样式 都是一样的效果-->
  <el-row class="login-container">
    <!-- <el-row style="min-height: 100vh;" class="bg-indigo-400"> -->
    <!--总数是24 就是24列-->
    <!-- <el-col :span="16" class="flex items-center justify-center"> -->
    <!--响应式后-->
    <el-col :lg="16" class="left">
      <div>
        <div>
          欢迎光临华测教育
        </div>
        <div>欢迎使用华测教育的在线测试平台学习,这里是《高级测试开发课》的演示地址</div>
      </div>
    </el-col>
    <!-- <el-col :span="8" class="bg-indigo-50 flex items-center justify-center flex-col"> -->
    <!--响应式后-->
    <el-col :lg="8" class=" right">

      <h2 class="title">欢迎回来</h2>
      <!--下面这个布局是个很明显的flex布局，左中右 都是水平垂直居中-->
      <!--上下都要有外间距，所以my-5 都是灰色-->
      <!--space-x-2 就是左右间距-->
      <div>
        <!--然后这里需要渲染颜色-->
        <span class="line"></span>
        <span>账号密码登录</span>
        <span class="line"></span>
      </div>

      <el-form ref="formRef" :rules="rules" :model="form" class="w-[250px]">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名">
            <!--这里需要插槽处理图标问题-->
            <template #prefix>
              <el-icon class="el-input__icon">
                <User />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input type="password" v-model="form.password" placeholder="请输入密码" show-password>
            <template #prefix>
              <el-icon>
                <Lock />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button class="w-[250px] round" type="primary" @click="onSubmit">登录</el-button>
        </el-form-item>
      </el-form>
    </el-col>
  </el-row>
</template>

<script setup>
import { reactive, ref } from "vue";
// import { Lock,User } from '@element-plus/icons-vue';
import { login } from './login'
import { useCookies } from '@vueuse/integrations/useCookies';
import { ElNotification } from 'element-plus'
import { useRouter } from "vue-router";

const cookie = useCookies()
const router = useRouter()


// do not use same name with ref
const form = reactive({
  username: "",
  password: ""
});


const rules = {
  username: [
    { required: true, message: '用户名不能为空', trigger: 'blur' },
    { min: 3, max: 16, message: '用户名长度必须在3到16之间', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '密码不能为空', trigger: 'blur' }
  ]

}

const formRef = ref(null)

const onSubmit = () => {
  formRef.value.validate((valid) => {
    // console.log(valid);
    if (!valid) {
      return false
    }
    login(form.username, form.password)
      .then(res => {
        console.log("请求成功")
        console.log(res.data.data)
        if (res.data.code == 200 && res.data.data.token != null) {
          ElNotification({
            title: 'Success',
            message: '登录成功',
            type: 'success',
            duration: 2000
          })
          cookie.set("l-token", res.data.data.token)
          router.push("/home")

        } else {
          ElNotification({
            title: '登录失败',
            message: res.data.msg,
            type: 'error',
            duration: 2000
          })
        }
      }).catch(err => {
        ElNotification({
          title: '错误',
          message: '登录出现错误，请联系系统管理员',
          type: 'error',
          duration: 2000
        })
        return false
      })


  })
};
</script>

<style scoped>
.login-container {
  @apply min-h-screen bg-indigo-400;
}

.login-container .left,
.login-container .right {
  @apply flex items-center justify-center;
}

.login-container .right {
  @apply flex-col bg-indigo-50
}

.left>div>div:first-child {
  @apply font-bold text-5xl text-light-50 mb-4;
}

.left>div>div:last-child {
  @apply text-sm text-gray-200;
}

.right .title {
  @apply font-bold text-3xl text-gray-800;
}

.right>div {
  @apply flex items-center justify-center my-5 text-gray-300 space-x-2;
}

.right .line {
  @apply h-[1px] w-16 bg-gray-200;
}</style>