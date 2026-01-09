<template>
  <!--100vh就沾满了整个屏幕-->
  <!--上面这个是vite的CSS 下面是EL的样式 都是一样的效果-->
  <div class="login-container">
    <div class="login-content">
      <!-- 左侧欢迎区域 -->
      <div class="left">
        <div>
          <div>欢迎光临大熊AI</div>
          <div>欢迎使用大熊AI代码生成器</div>
        </div>
      </div>
      <!-- 右侧登录表单 -->
      <div class="right">
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
            <el-input
              type="password"
              v-model="form.password"
              placeholder="请输入密码"
              show-password
            >
              <template #prefix>
                <el-icon>
                  <Lock />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button class="w-[250px] round" type="primary" @click="onSubmit"
              >登录</el-button
            >
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { login, getUserInfo } from "./login.js";
import { ElNotification } from "element-plus";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { getUserMenus, getMenuTree } from "~/views/system/menu/menu";

const router = useRouter();
const store = useStore();

/**
 * 从菜单树中递归提取所有权限标识
 */
function extractPermissions(menuTree, permissions = []) {
  if (!menuTree || !Array.isArray(menuTree)) return permissions;
  
  menuTree.forEach(menu => {
    // 提取当前菜单的权限
    if (menu.perms) {
      permissions.push(menu.perms);
    }
    // 递归处理子菜单
    if (menu.children && menu.children.length > 0) {
      extractPermissions(menu.children, permissions);
    }
  });
  
  return permissions;
}

// token 存储到 localStorage
function setToken(token) {
    localStorage.setItem('token', token);
}

// do not use same name with ref
const form = reactive({
  username: "",
  password: "",
});

const rules = {
  username: [
    { required: true, message: "用户名不能为空", trigger: "blur" },
    { min: 3, max: 16, message: "用户名长度必须在3到16之间", trigger: "blur" },
  ],
  password: [{ required: true, message: "密码不能为空", trigger: "blur" }],
};

const formRef = ref(null);

const onSubmit = () => {
  // 提交登录表单
  formRef.value.validate(async (valid) => {
    if (!valid) {
      return false;
    }
    try {
      // 1. 登录获取 token
      const loginRes = await login(form.username, form.password);
      if (loginRes.data.code !== 200 || !loginRes.data.data?.access_token) {
        ElNotification({
          title: "登录失败",
          message: loginRes.data.msg || "登录失败",
          type: "error",
          duration: 2000,
        });
        return;
      }

      // 2. 保存 token
      const token = loginRes.data.data.access_token;
      setToken(token);

      // 3. 获取用户信息
      const userRes = await getUserInfo();
      if (userRes.data.code !== 200 || !userRes.data.data) {
        ElNotification({
          title: "错误",
          message: "获取用户信息失败",
          type: "error",
          duration: 2000,
        });
        return;
      }

      const userInfo = userRes.data.data;
      
      // 4. 保存用户信息到全局状态
      store.commit("setUserInfo", userInfo);
      localStorage.setItem("username", userInfo.username);

      ElNotification({
        title: "Success",
        message: "登录成功",
        type: "success",
        duration: 2000,
      });

      // 5. 拉取用户菜单
      const userId = userInfo.id;
      if (userId) {
        try {
          const menuRes = await getUserMenus(userId);
          if (menuRes?.data?.code === 200) {
            let tree = menuRes.data.data || [];
            console.log("登录时获取的用户菜单数据:", tree);
            if (tree.length === 0) {
              // 兜底：用户无绑定权限，展示全量菜单树
              console.log("用户菜单为空，获取全量菜单");
              const allRes = await getMenuTree();
              if (allRes?.data?.code === 200) {
                tree = allRes.data.data || [];
              }
            }
            
            console.log("设置用户菜单，菜单数量:", tree.length);
            store.commit("setMenuTree", tree);
            
            // 6. 从菜单树中提取权限列表
            const permissions = extractPermissions(tree);
            console.log("提取的权限列表:", permissions);
            store.commit("setPermissions", permissions);
            localStorage.setItem("permissions", JSON.stringify(permissions));
          }
        } catch (e) {
          console.error("处理菜单数据失败:", e);
        }
      }

      // 7. 跳转到主页
      router.replace("/home");
    } catch (err) {
      console.error("登录错误:", err);
      ElNotification({
        title: "错误",
        message: "登录出现错误，请联系系统管理员",
        type: "error",
        duration: 2000,
      });
    }
  });
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
  padding: 20px;
}

/* 内容容器 - 限制最大宽度，大屏幕居中 */
.login-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(40px, 8vw, 120px);
  max-width: 1000px;
  width: 100%;
  position: relative;
  z-index: 1;
  margin: 0 auto;
}

/* 动态背景装饰 */
.login-container::before,
.login-container::after {
  content: "";
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
  0%,
  100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -50px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

.login-content .left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 20px;
}

.login-content .right {
  flex: 0 0 auto;
  width: clamp(320px, 35vw, 400px);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: clamp(32px, 4vw, 48px);
  box-shadow: var(--shadow-xl);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-theme="dark"] .login-content .right {
  background: rgba(30, 41, 59, 0.95);
}

.login-content .right:hover {
  transform: translateY(-8px);
  box-shadow: 0 24px 38px 3px rgba(0, 0, 0, 0.14);
}

.left > div > div:first-child {
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 3.5rem);
  color: white;
  margin-bottom: 1rem;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  animation: slideInLeft 0.8s ease;
  white-space: nowrap;
}

.left > div > div:last-child {
  font-size: clamp(0.9rem, 1.5vw, 1.25rem);
  color: rgba(255, 255, 255, 0.9);
  max-width: 400px;
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
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.right > div {
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

/* 平板适配 */
@media (max-width: 1024px) {
  .login-content {
    max-width: 900px;
  }
  
  .login-content .left {
    padding-right: 10px;
  }
}

/* 小屏幕/手机适配 */
@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
    gap: 30px;
    max-width: 100%;
  }

  .login-content .left {
    display: none;
  }

  .login-content .right {
    width: 100%;
    max-width: 360px;
    border-radius: 16px;
  }

  .right .title {
    font-size: 1.5rem;
  }
}

/* 大屏幕优化 */
@media (min-width: 1400px) {
  .login-content {
    max-width: 1100px;
  }
}

/* 超大屏幕优化 (2K+) */
@media (min-width: 1920px) {
  .login-content {
    max-width: 1200px;
  }
}
</style>
