import axios from "axios"
import {ElMessage, ElNotification } from 'element-plus'

const service = axios.create({
    baseURL: "http://127.0.0.1:5000"
})

// token 刷新相关变量
let isRefreshing = false; // 是否正在刷新 token
let refreshSubscribers = []; // 存储待重试的请求

// 添加订阅者（等待 token 刷新完成后重试的请求）
function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback);
}

// 通知所有订阅者 token 已刷新
function onTokenRefreshed(newToken) {
  refreshSubscribers.forEach(callback => callback(newToken));
  refreshSubscribers = [];
}

// 刷新 token 的函数
async function refreshToken() {
  const refreshToken = localStorage.getItem('refreshToken');
  if (!refreshToken) {
    console.log('没有 refreshToken，无法刷新');
    return null;
  }

  try {
    // 使用 service 实例，但标记跳过拦截器
    const response = await service.post('/refresh', {
      refreshToken: refreshToken
    }, {
      _skipInterceptor: true  // 自定义标记，跳过拦截器处理
    });

    console.log('刷新 token 响应:', response.data);

    if (response.data.code === 200) {
      const responseData = response.data.data || response.data;
      const { token, refreshToken: newRefreshToken } = responseData;
      
      if (token && newRefreshToken) {
        // 保存新的 token
        localStorage.setItem('token', token);
        localStorage.setItem('refreshToken', newRefreshToken);
        console.log('Token 刷新成功');
        return token;
      }
    }
    console.log('Token 刷新失败: 响应格式不正确');
    return null;
  } catch (error) {
    console.error('刷新 token 失败:', error);
    return null;
  }
}

// 请求拦截器：添加令牌到请求头
service.interceptors.request.use(
  config => {
    // 检查是否跳过拦截器
    if (config._skipInterceptor) {
      delete config._skipInterceptor;
      return config;
    }

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
    // 跳过拦截器标记的请求，直接返回
    if (response.config._skipInterceptor) {
        return response;
    }
    
    // 对于登录和刷新接口，不在拦截器中显示错误消息，让业务代码自己处理
    const isLoginRequest = response.config.url && response.config.url.includes('/login');
    const isRefreshRequest = response.config.url && response.config.url.includes('/refresh');
    
    if(response.data.code != 200) {
        if (!isLoginRequest && !isRefreshRequest) {
            ElMessage.error(response.data.msg + '，状态码:' + response.data.code)
        }
    } else {
        if(response.data.msg != null && !isLoginRequest && !isRefreshRequest) {
            ElNotification({
                title: response.data.msg,
                type: 'success',
                duration: 1000
              })
        }
    }
    return response
}, async error => {
    const originalRequest = error.config;

    // 处理401未授权错误 - 尝试刷新 token
    if (error.response && error.response.status === 401) {
      // 防止无限重试 - 如果已经重试过，直接跳转登录
      if (originalRequest._retry) {
        console.log('Token 刷新后仍然失败，跳转登录');
        ElMessage.error('登录已过期，请重新登录');
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        clearAllCookies();
        return Promise.reject(error);
      }

      // 如果是刷新 token 接口返回 401，直接跳转登录
      if (originalRequest.url.includes('/refresh')) {
        console.log('刷新接口返回401，跳转登录');
        ElMessage.error('登录已过期，请重新登录');
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        clearAllCookies();
        return Promise.reject(error);
      }

      // 标记该请求已经重试过
      originalRequest._retry = true;

      // 如果正在刷新 token，将请求加入队列
      if (isRefreshing) {
        console.log('正在刷新 token，将请求加入队列');
        return new Promise(resolve => {
          subscribeTokenRefresh(newToken => {
            originalRequest.headers.token = newToken;
            resolve(service(originalRequest));
          });
        });
      }

      // 开始刷新 token
      console.log('开始刷新 token');
      isRefreshing = true;
      
      try {
        const newToken = await refreshToken();
        
        if (newToken) {
          console.log('Token 刷新成功，重试原请求');
          // token 刷新成功，更新请求头并重试原请求
          originalRequest.headers.token = newToken;
          // 通知所有等待的请求
          onTokenRefreshed(newToken);
          isRefreshing = false;
          return service(originalRequest);
        } else {
          // token 刷新失败，跳转到登录页
          console.log('Token 刷新失败，跳转登录');
          ElMessage.error('登录已过期，请重新登录');
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          window.location.href = '/login';
          clearAllCookies();
          isRefreshing = false;
          return Promise.reject(error);
        }
      } catch (refreshError) {
        console.error('Token 刷新异常:', refreshError);
        ElMessage.error('登录已过期，请重新登录');
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        clearAllCookies();
        isRefreshing = false;
        return Promise.reject(refreshError);
      }
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