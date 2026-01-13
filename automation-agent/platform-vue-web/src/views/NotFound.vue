<template>
  <div class="not-found">
    <div class="error-code">404</div>
    <h2>页面未找到</h2>
    <p>抱歉，您访问的页面不存在或已被移除</p>
    <router-link to="/Statistics" class="home-link">返回首页</router-link>
  </div>
</template>

<style scoped>
.not-found {
  text-align: center;
  padding: 50px 20px;
}

.error-code {
  font-size:  clamp(5rem, 20vw, 10rem);  /* 响应式字体大小 */
  font-weight: bold;  
  color: #ff4d4f;
  margin: 20px 0;
  line-height: 1;
}

h2 {
  color: #303133;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

p {
  color: #606266;
  margin-bottom: 30px;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.home-link {
  display: inline-block;
  background-color: #42b983;
  color: white;
  padding: 10px 24px;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.3s;
}

.home-link:hover {
  background-color: #359469;
}
</style>