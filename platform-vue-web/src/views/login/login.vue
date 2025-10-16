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
import { login } from './login.js'
import { useCookies } from '@vueuse/integrations/useCookies';
import { ElNotification } from 'element-plus'
import { useRouter } from "vue-router";
import { useStore } from 'vuex'
import { getUserMenus, getMenuTree } from '~/views/system/menu/menu'

const cookie = useCookies()
const router = useRouter()
const store = useStore()


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
        if (res.data.code == 200 && res.data.data.token != null) {
          ElNotification({
            title: 'Success',
            message: '登录成功',
            type: 'success',
            duration: 2000
          })
          cookie.set("l-token", res.data.data.token)
          // 持久化一个用户ID，供刷新兜底拉取菜单
          if(res?.data?.data?.id){
            cookie.set('l-user-id', res.data.data.id)
          }
          // 保存用户信息到全局状态
          try {
            store.commit('setUserInfo', res.data.data)
          } catch (e) {}
          // 拉取并写入用户菜单树，然后再跳转首页
          const userId = res?.data?.data?.id
          if (userId) {
            return getUserMenus(userId).then(async menuRes => {
              if (menuRes?.data?.code === 200) {
                try {
                  const tree = menuRes.data.data || []
                  if (tree.length > 0) {
                    store.commit('setMenuTree', tree)
                  } else {
                    // 兜底：用户无绑定权限，展示全量菜单树
                    const allRes = await getMenuTree()
                    if (allRes?.data?.code === 200) {
                      store.commit('setMenuTree', allRes.data.data || [])
                    }
                  }
                } catch (e) {}
              }
              // 确保菜单数据加载完成后再跳转
              router.replace("/Statistics")
            })
          } else {
            router.replace("/Statistics")
          }

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
  min-height: 100vh;
  background: var(--primary-gradient);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 动态背景装饰 */
.login-container::before,
.login-container::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 20s infinite ease-in-out;
}

.login-container::before {
  width: 500px;
  height: 500px;
  top: -250px;
  right: -250px;
}

.login-container::after {
  width: 300px;
  height: 300px;
  bottom: -150px;
  left: -150px;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  33% { transform: translate(30px, -50px) rotate(120deg); }
  66% { transform: translate(-20px, 20px) rotate(240deg); }
}

.login-container .left,
.login-container .right {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 1;
}

.login-container .right {
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 48px;
  box-shadow: var(--shadow-xl);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-theme="dark"] .login-container .right {
  background: rgba(30, 41, 59, 0.95);
}

.login-container .right:hover {
  transform: translateY(-8px);
  box-shadow: 0 24px 38px 3px rgba(0, 0, 0, 0.14);
}

.left>div>div:first-child {
  font-weight: 700;
  font-size: 3rem;
  color: white;
  margin-bottom: 1.5rem;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: slideInLeft 0.8s ease;
}

.left>div>div:last-child {
  font-size: 1.125rem;
  color: rgba(255, 255, 255, 0.9);
  max-width: 500px;
  line-height: 1.6;
  animation: slideInLeft 0.8s ease 0.2s both;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.right .title {
  font-weight: 700;
  font-size: 2rem;
  color: var(--text-primary);
  margin-bottom: 1rem;
  animation: fadeIn 0.8s ease 0.4s both;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.right>div {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1.5rem 0;
  color: var(--text-tertiary);
  gap: 0.75rem;
  animation: fadeIn 0.8s ease 0.5s both;
}

.right .line {
  height: 1px;
  width: 4rem;
  background: var(--border-color);
}

/* 表单输入框动效 */
:deep(.el-form) {
  animation: fadeIn 0.8s ease 0.6s both;
}

:deep(.el-input) {
  transition: all 0.3s ease;
}

:deep(.el-input:focus-within) {
  transform: translateX(4px);
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: var(--shadow-md);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  transform: translateY(-2px);
}

:deep(.el-button) {
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

:deep(.el-button:hover) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

:deep(.el-button:active) {
  transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .left {
    display: none;
  }
  
  .login-container .right {
    padding: 32px 24px;
    border-radius: 16px;
    margin: 20px;
  }
  
  .right .title {
    font-size: 1.5rem;
  }
}
</style>