import axios from "axios"
import {ElMessage, ElNotification } from 'element-plus'

const service = axios.create({
    // baseURL: "http://127.0.0.1:5000"
    baseURL: "/api"
})


// 请求拦截器：添加令牌到请求头
service.interceptors.request.use(
  config => {
    // 从localStorage获取令牌
    const token = localStorage.getItem('token');
    // 如果令牌存在，添加到请求头
    if (token) {
      config.headers.token = `${token}`;
    }
    return config;
  },
  error => {
    // 处理请求错误
    ElMessage.error('网络异常，请稍后再试')
    return Promise.reject(error);
  }
);

// 添加响应拦截器
service.interceptors.response.use(response => {
    close()
    if(response.data.code != 200) {
        ElMessage.error(response.data.msg + '，状态码:' + response.data.code)
    } else {
        if(response.data.msg != null) {
            ElNotification({
                title: response.data.msg,
                type: 'success',
                duration: 1000
              })
        }
    }
    return response
}, error => {
    // close()

    // 处理401未授权错误
    if (error.response && error.response.status === 401) {
      ElMessage.error('网络异常，请稍后再试')
      // 清除本地token
      localStorage.removeItem('token');
      // 跳转到登录页
      window.location.href = '/login';
      // 清除cookie中的tabList数据
      // 注意：这里需要引入useCookies 来进行清除
      clearAllCookies();
    }
    
    return Promise.reject(error)
})


// 清除所有cookie的函数
import { useCookies } from '@vueuse/integrations/useCookies';
function clearAllCookies() {
    // 清除tabList cookie
    document.cookie = "tabList=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/";
    
    // 如果使用了js-cookie库，可以这样清除：
    useCookies.remove('tabList');
}


export default service